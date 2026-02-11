"""
Main FastAPI application with WhatsApp webhook endpoint
"""
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import Response
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path
import os

from app.utils.logger import app_logger
from app.utils.config import settings
from app.utils.image_processor import optimize_image_for_ocr, validate_image_format
from app.models import WhatsAppMessage, ProcessingResult, Invoice
from app.whatsapp_handler import whatsapp_handler
from app.ocr_processor import ocr_processor
from app.ncf_parser import ncf_parser
from app.export_handler import export_handler

# Create FastAPI app
app = FastAPI(
    title="LECTOR-NCF",
    description="Sistema de Lectura OCR de Facturas NCF desde WhatsApp",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    app_logger.info("=" * 50)
    app_logger.info("LECTOR-NCF Starting...")
    app_logger.info(f"Debug mode: {settings.debug}")
    app_logger.info(f"Export format: {settings.export_format}")
    app_logger.info("=" * 50)
    
    # Create necessary directories
    os.makedirs("data/temp", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "running",
        "service": "LECTOR-NCF",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/webhook/whatsapp",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "ocr": ocr_processor.client is not None,
            "whatsapp": whatsapp_handler.client is not None
        }
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    MessageSid: str = Form(...),
    NumMedia: str = Form("0"),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
    Body: Optional[str] = Form(None)
):
    """
    WhatsApp webhook endpoint for receiving messages from Twilio
    
    This endpoint receives WhatsApp messages with invoice images,
    processes them through OCR, extracts NCF data, and sends results back.
    """
    app_logger.info(f"Received WhatsApp message from {From}")
    app_logger.info(f"Message SID: {MessageSid}, Media count: {NumMedia}")
    
    try:
        # Parse WhatsApp message
        num_media = int(NumMedia)
        
        # Check if message has media
        if num_media == 0:
            app_logger.warning("No media attached to message")
            whatsapp_handler.send_message(
                From,
                "Por favor envía una foto de la factura. 📸"
            )
            return Response(content="", status_code=200)
        
        # Send confirmation
        whatsapp_handler.send_confirmation(From)
        
        # Download image
        app_logger.info(f"Downloading image from: {MediaUrl0}")
        image_bytes = await whatsapp_handler.download_media(
            MediaUrl0,
            settings.twilio_auth_token
        )
        
        if not image_bytes:
            app_logger.error("Failed to download image")
            whatsapp_handler.send_error(From, "No se pudo descargar la imagen")
            return Response(content="", status_code=200)
        
        # Validate image format
        if not validate_image_format(image_bytes):
            app_logger.error("Invalid image format")
            whatsapp_handler.send_error(From, "Formato de imagen no válido")
            return Response(content="", status_code=200)
        
        # Save original image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"factura_{timestamp}.jpg"
        temp_path = Path("data/temp") / image_filename
        
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        app_logger.info(f"Saved original image: {temp_path}")
        
        # Optimize image for OCR
        optimized_image = optimize_image_for_ocr(image_bytes)
        
        # Perform OCR
        app_logger.info("Starting OCR processing...")
        ocr_text, confidence = ocr_processor.process_invoice_image(optimized_image)
        
        if not ocr_text:
            app_logger.error("OCR failed - no text extracted")
            whatsapp_handler.send_error(From, "No se pudo leer texto en la imagen")
            return Response(content="", status_code=200)
        
        app_logger.info(f"OCR successful. Text length: {len(ocr_text)}, Confidence: {confidence}")
        
        # Parse invoice data
        app_logger.info("Parsing invoice data...")
        invoice = ncf_parser.parse_invoice(ocr_text, confidence, image_filename)
        
        # Check extraction quality
        warnings = []
        if not invoice.ncf:
            warnings.append("NCF no encontrado")
        if not invoice.rnc:
            warnings.append("RNC no encontrado")
        if not invoice.montos.total:
            warnings.append("Monto total no encontrado")
        
        # Export to CSV/JSON
        try:
            export_result = export_handler.export([invoice])
            app_logger.info(f"Exported invoice data: {export_result}")
            
            # Also append to historical CSV
            export_handler.append_to_csv(invoice)
        except Exception as e:
            app_logger.error(f"Export failed: {e}")
        
        # Move image to processed folder
        processed_path = Path("data/processed") / image_filename
        temp_path.rename(processed_path)
        app_logger.info(f"Moved image to processed: {processed_path}")
        
        # Send response to user
        if warnings:
            whatsapp_handler.send_partial_success(From, warnings)
        elif invoice.ncf:
            whatsapp_handler.send_success(From, invoice.ncf, invoice.montos.total)
        else:
            whatsapp_handler.send_error(From)
        
        app_logger.info("Processing completed successfully")
        return Response(content="", status_code=200)
        
    except Exception as e:
        app_logger.error(f"Error processing WhatsApp message: {e}", exc_info=True)
        try:
            whatsapp_handler.send_error(From, "Error interno del sistema")
        except:
            pass
        return Response(content="", status_code=200)


@app.post("/process-invoice")
async def process_invoice_api(request: Request):
    """
    API endpoint for processing invoice images directly (without WhatsApp)
    
    Accepts: multipart/form-data with 'image' file
    """
    try:
        form = await request.form()
        image_file = form.get('image')
        
        if not image_file:
            raise HTTPException(status_code=400, detail="No image provided")
        
        # Read image bytes
        image_bytes = await image_file.read()
        
        # Validate image
        if not validate_image_format(image_bytes):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Process image
        optimized_image = optimize_image_for_ocr(image_bytes)
        ocr_text, confidence = ocr_processor.process_invoice_image(optimized_image)
        
        if not ocr_text:
            raise HTTPException(status_code=400, detail="Failed to extract text from image")
        
        # Parse invoice
        invoice = ncf_parser.parse_invoice(ocr_text, confidence)
        
        # Export
        export_result = export_handler.export([invoice])
        
        return {
            "success": True,
            "invoice": invoice.model_dump(),
            "exports": export_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error processing invoice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
