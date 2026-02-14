"""
Main FastAPI application with WhatsApp webhook endpoint
"""
from fastapi import FastAPI, Form, Request, HTTPException, UploadFile, File
from fastapi.responses import Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path
import os
import shutil
import json

from app.utils.logger import app_logger
from app.utils.config import settings
from app.utils.image_processor import optimize_image_for_ocr, validate_image_format
from app.models import WhatsAppMessage, ProcessingResult, Invoice
from app.whatsapp_handler import whatsapp_handler
from app.ocr_processor import ocr_processor
from app.ncf_parser import ncf_parser
from app.export_handler import export_handler
from app.firebase_handler import firebase_handler

# Create FastAPI app
app = FastAPI(
    title="LECTOR-NCF",
    description="Sistema de Lectura OCR de Facturas NCF desde WhatsApp",
    version="1.0.0"
)

# Constants for Credentials
CREDENTIALS_DIR = Path("credentials")
FIREBASE_CRED_PATH = CREDENTIALS_DIR / "firebase-credentials.json"


def check_firebase_credentials():
    """Returns True if the Firebase credentials file exists."""
    return FIREBASE_CRED_PATH.exists()


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    app_logger.info("=" * 50)
    app_logger.info("LECTOR-NCF Starting...")
    app_logger.info(f"Debug mode: {settings.debug}")
    app_logger.info("=" * 50)
    
    # Create necessary directories
    os.makedirs("data/temp", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    
    if not check_firebase_credentials():
        app_logger.warning("⚠️ FIREBASE CREDENTIALS NOT FOUND. Please visit /setup to configure them.")


@app.get("/")
async def root():
    """Root endpoint - redirects to setup if credentials are missing"""
    if not check_firebase_credentials():
        return RedirectResponse(url="/setup")
        
    return {
        "status": "running",
        "service": "LECTOR-NCF",
        "firebase_configured": True,
        "endpoints": {
            "webhook": "/webhook/whatsapp",
            "status": "/webhook/status",
            "setup": "/setup"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "firebase_configured": check_firebase_credentials(),
        "services": {
            "whatsapp": whatsapp_handler is not None,
            "ocr": ocr_processor is not None,
            "firebase": firebase_handler.db is not None if firebase_handler else False
        }
    }


# ==========================================
# SETUP UI (WEB CREDENTIAL SELECTOR)
# ==========================================

@app.get("/setup", response_class=HTMLResponse)
async def setup_page():
    """Displays the web UI to upload Firebase credentials"""
    firebase_configured = check_firebase_credentials()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LECTOR-NCF | Configuración</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh; 
                padding: 20px;
            }
            .container { 
                background-color: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.2); 
                width: 100%; 
                max-width: 550px; 
                text-align: center;
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            h2 { 
                color: #333; 
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .status-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .status-success {
                background-color: #d4edda;
                color: #155724;
            }
            .status-warning {
                background-color: #fff3cd;
                color: #856404;
            }
            .upload-box { 
                border: 2px dashed #667eea; 
                padding: 30px; 
                margin: 20px 0; 
                border-radius: 10px;
                background-color: #f8f9ff;
                transition: all 0.3s ease;
            }
            .upload-box:hover {
                border-color: #764ba2;
                background-color: #f0f2ff;
            }
            input[type="file"] {
                width: 100%;
                padding: 10px;
                cursor: pointer;
            }
            input[type="text"] {
                width: 100%; 
                padding: 12px; 
                margin-bottom: 15px; 
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            input[type="text"]:focus {
                outline: none;
                border-color: #667eea;
            }
            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 14px 20px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px; 
                width: 100%; 
                margin-top: 10px;
                font-weight: bold;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            .btn:active {
                transform: translateY(0);
            }
            .info-box {
                background-color: #e8f4f8;
                border-left: 4px solid #17a2b8;
                padding: 15px;
                margin: 20px 0;
                text-align: left;
                border-radius: 5px;
            }
            .info-box strong {
                color: #17a2b8;
            }
            .footer {
                margin-top: 30px;
                color: #999;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔥 LECTOR-NCF</h2>
            <p class="subtitle">Sistema de Lectura OCR de Facturas</p>
            
            """ + (
                '<div class="status-badge status-success">✅ Firebase Configurado</div>' 
                if firebase_configured else 
                '<div class="status-badge status-warning">⚠️ Configuración Pendiente</div>'
            ) + """
            
            <div class="info-box">
                <strong>📋 Requisitos:</strong><br>
                • Archivo <code>firebase-credentials.json</code><br>
                • URL de Firebase Database<br>
                • Permisos de administrador
            </div>
            
            <form action="/setup/upload" method="post" enctype="multipart/form-data">
                <div class="upload-box">
                    <p style="margin-bottom: 15px; color: #666;">📁 Selecciona tu archivo JSON</p>
                    <input type="file" name="file" accept=".json" required>
                </div>
                <input 
                    type="text" 
                    name="database_url" 
                    placeholder="https://tu-proyecto.firebaseio.com" 
                    required
                    """ + (f'value="{settings.firebase_database_url}"' if firebase_configured and hasattr(settings, 'firebase_database_url') else '') + """
                >
                <button type="submit" class="btn">💾 Guardar y Conectar</button>
            </form>
            
            <div class="footer">
                <p>LECTOR-NCF v1.0.0 | © 2026 ZOEC CIVIL</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/setup/upload")
async def upload_credentials(file: UploadFile = File(...), database_url: str = Form(...)):
    """Handles the upload of the credentials file and saves it"""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="El archivo debe ser un JSON")

        # Create credentials directory if it doesn't exist
        os.makedirs(CREDENTIALS_DIR, exist_ok=True)
        
        # Save the uploaded file
        with open(FIREBASE_CRED_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Verify it's a valid JSON
        try:
            with open(FIREBASE_CRED_PATH, "r") as f:
                json.load(f)
        except json.JSONDecodeError:
            os.remove(FIREBASE_CRED_PATH)
            raise HTTPException(status_code=400, detail="El archivo JSON es inválido o está corrupto.")

        # Re-initialize Firebase Handler
        settings.firebase_credentials = str(FIREBASE_CRED_PATH)
        settings.firebase_database_url = database_url
        firebase_handler.__init__()
        
        app_logger.info("✅ Firebase credentials uploaded and initialized successfully")

        return RedirectResponse(url="/setup", status_code=303)
        
    except Exception as e:
        app_logger.error(f"Error saving credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# WHATSAPP WEBHOOK
# ==========================================

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
    """WhatsApp webhook endpoint for receiving messages from Twilio"""
    
    # Check Firebase credentials before processing
    if not check_firebase_credentials():
        app_logger.error("Message received but Firebase is not configured.")
        return Response(content="", status_code=200)

    app_logger.info(f"Received WhatsApp message from {From}")
    
    try:
        num_media = int(NumMedia)
        
        # No media sent
        if num_media == 0:
            whatsapp_handler.send_message(From, "Por favor envía una foto de la factura. 📸")
            return Response(content="", status_code=200)
        
        # Send confirmation message
        whatsapp_handler.send_confirmation(From)
        
        # Download image
        image_bytes = await whatsapp_handler.download_media(MediaUrl0, settings.twilio_auth_token)
        if not image_bytes:
            whatsapp_handler.send_error(From, "No se pudo descargar la imagen")
            return Response(content="", status_code=200)
        
        # Save temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"factura_{timestamp}.jpg"
        temp_path = Path("data/temp") / image_filename
        
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        
        # Process with OCR
        optimized_image = optimize_image_for_ocr(image_bytes)
        ocr_text, confidence = ocr_processor.process_invoice_image(optimized_image)
        
        if not ocr_text:
            whatsapp_handler.send_error(From, "No se pudo leer texto en la imagen")
            return Response(content="", status_code=200)
        
        # Parse invoice data
        invoice = ncf_parser.parse_invoice(ocr_text, confidence, image_filename)
        
        # Check for warnings
        warnings = []
        if not invoice.ncf: 
            warnings.append("NCF no encontrado")
        if not invoice.montos.total: 
            warnings.append("Monto total no encontrado")
        
        # Export to CSV/JSON
        export_handler.export([invoice])
        
        # Save to Firebase
        try:
            firebase_handler.save_invoice(invoice)
        except Exception as e:
            app_logger.error(f"Firebase save failed: {e}")
        
        # Move to processed folder
        processed_path = Path("data/processed") / image_filename
        temp_path.rename(processed_path)
        
        # Send response to user
        if warnings:
            whatsapp_handler.send_partial_success(From, warnings)
        elif invoice.ncf:
            whatsapp_handler.send_success(From, invoice.ncf, invoice.montos.total)
        else:
            whatsapp_handler.send_error(From)
        
        return Response(content="", status_code=200)
        
    except Exception as e:
        app_logger.error(f"Error processing message: {e}")
        try:
            whatsapp_handler.send_error(From, "Error interno del sistema")
        except:
            pass
        return Response(content="", status_code=200)



    # ==========================================
    # GREEN-API WEBHOOK
    # ==========================================

    @app.post("/webhook/greenapi")
    async def greenapi_webhook(request: Request):
        """Green-API webhook endpoint for receiving messages"""
        
        try:
            data = await request.json()
            app_logger.info(f"Received Green-API webhook: {data}")
            
            # Green-API envía diferentes tipos de notificaciones
            type_webhook = data.get("typeWebhook")
            
            if type_webhook == "incomingMessageReceived":
                message_data = data.get("messageData", {})
                
                # Obtener datos del mensaje
                chat_id = message_data.get("chatId")  # 18293757344@c.us
                message_type = message_data.get("typeMessage")
                
                # Extraer número de teléfono
                phone = chat_id.split("@")[0]
                from_number = f"whatsapp:+{phone}"
                
                # Si es imagen
                if message_type == "imageMessage":
                    app_logger.info(f"Processing image from {from_number}")
                    
                    # Enviar confirmación
                    await greenapi_handler.send_message(
                        from_number, 
                        "✅ Factura recibida, procesando... ⏳"
                    )
                    
                    # Descargar imagen
                    download_url = message_data.get("downloadUrl")
                    if not download_url:
                        await greenapi_handler.send_error(from_number, "No se pudo descargar la imagen")
                        return Response(content="", status_code=200)
                    
                    # Descargar imagen
                    async with httpx.AsyncClient() as client:
                        img_response = await client.get(download_url)
                        image_bytes = img_response.content
                    
                    # Guardar temporalmente
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_filename = f"factura_{timestamp}.jpg"
                    temp_path = Path("data/temp") / image_filename
                    
                    with open(temp_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    # Procesar con OCR
                    optimized_image = optimize_image_for_ocr(image_bytes)
                    ocr_text, confidence = ocr_processor.process_invoice_image(optimized_image)
                    
                    if not ocr_text:
                        await greenapi_handler.send_error(from_number, "No se pudo leer texto en la imagen")
                        return Response(content="", status_code=200)
                    
                    # Parsear factura
                    invoice = ncf_parser.parse_invoice(ocr_text, confidence, image_filename)
                    
                    # Verificar warnings
                    warnings = []
                    if not invoice.ncf: 
                        warnings.append("NCF no encontrado")
                    if not invoice.montos.total: 
                        warnings.append("Monto total no encontrado")
                    
                    # Exportar
                    export_handler.export([invoice])
                    
                    # Guardar en Firebase
                    try:
                        firebase_handler.save_invoice(invoice)
                    except Exception as e:
                        app_logger.error(f"Firebase save failed: {e}")
                    
                    # Mover a procesados
                    processed_path = Path("data/processed") / image_filename
                    temp_path.rename(processed_path)
                    
                    # Enviar respuesta
                    if warnings:
                        await greenapi_handler.send_partial_success(from_number, warnings)
                    elif invoice.ncf:
                        await greenapi_handler.send_success(from_number, invoice.ncf, invoice.montos.total)
                    else:
                        await greenapi_handler.send_error(from_number)
                
                elif message_type == "textMessage":
                    # Mensaje de texto
                    text = message_data.get("textMessageData", {}).get("textMessage", "")
                    app_logger.info(f"Text message from {from_number}: {text}")
                    
                    await greenapi_handler.send_message(
                        from_number,
                        "Por favor envía una foto de la factura. 📸"
                    )
            
            return Response(content="", status_code=200)
            
        except Exception as e:
            app_logger.error(f"Error processing Green-API webhook: {e}")
            return Response(content="", status_code=200)


# ==========================================
# STATUS WEBHOOK
# ==========================================

@app.post("/webhook/status")
async def whatsapp_status(request: Request):
    """Receive WhatsApp message status updates from Twilio"""
    try:
        form_data = await request.form()
        message_sid = form_data.get("MessageSid")
        message_status = form_data.get("MessageStatus")
        error_code = form_data.get("ErrorCode")
        error_message = form_data.get("ErrorMessage")
        
        if error_code:
            app_logger.error(f"Message {message_sid} failed - Code: {error_code}, Message: {error_message}")
        else:
            app_logger.info(f"Message status update - SID: {message_sid}, Status: {message_status}")
        
        return Response(content="", status_code=200)
    except Exception as e:
        app_logger.error(f"Error processing status webhook: {e}")
        return Response(content="", status_code=200)


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    import uvicorn
    
    # Usar PORT de Render si está disponible
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.debug)