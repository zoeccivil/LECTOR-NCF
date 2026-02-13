"""
Google Cloud Vision OCR processor for invoice text extraction
"""
from google.cloud import vision
from typing import Optional, Tuple, Dict
import os
import re
from datetime import datetime
from app.utils.logger import app_logger
from app.utils.config import settings


class OCRProcessor:
    """Handles OCR processing using Google Cloud Vision API"""
    
    def __init__(self):
        """Initialize Google Cloud Vision client"""
        try:
            # ✅ Set credentials from config (supports google_cloud.credentials_path)
            creds_path = settings.google_application_credentials
            
            if creds_path and os.path.exists(creds_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                app_logger.info(f"Using Google Cloud credentials: {creds_path}")
            else:
                app_logger.warning(f"Credentials file not found: {creds_path}")
            
            self.client = vision.ImageAnnotatorClient()
            app_logger.info("✅ Google Cloud Vision client initialized successfully")
        except Exception as e:
            app_logger.error(f"❌ Failed to initialize Google Cloud Vision client: {e}")
            self.client = None
    
    def extract_text_from_image(self, image_bytes: bytes) -> Tuple[Optional[str], Optional[float]]:
        """
        Extract text from image using Google Cloud Vision OCR
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not self.client:
            app_logger.error("Vision client not initialized")
            return None, None
        
        try:
            # Create vision image
            image = vision.Image(content=image_bytes)
            
            # Perform text detection
            app_logger.info("Sending image to Google Cloud Vision API...")
            response = self.client.text_detection(image=image)
            
            # Check for errors
            if response.error.message:
                app_logger.error(f"Vision API error: {response.error.message}")
                return None, None
            
            # Get text annotations
            texts = response.text_annotations
            
            if not texts:
                app_logger.warning("No text detected in image")
                return None, 0.0
            
            # First annotation contains full text
            full_text = texts[0].description
            
            # Calculate average confidence
            confidence = self._calculate_confidence(response)
            
            app_logger.info(f"Successfully extracted {len(full_text)} characters with confidence {confidence:.2f}")
            app_logger.debug(f"Extracted text preview: {full_text[:200]}...")
            
            return full_text, confidence
            
        except Exception as e:
            app_logger.error(f"Error during OCR processing: {e}")
            return None, None
    
    def extract_text_with_document_detection(self, image_bytes: bytes) -> Tuple[Optional[str], Optional[float]]:
        """
        Extract text using document text detection (better for dense text)
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not self.client:
            app_logger.error("Vision client not initialized")
            return None, None
        
        try:
            # Create vision image
            image = vision.Image(content=image_bytes)
            
            # Perform document text detection
            app_logger.info("Performing document text detection...")
            response = self.client.document_text_detection(image=image)
            
            # Check for errors
            if response.error.message:
                app_logger.error(f"Vision API error: {response.error.message}")
                return None, None
            
            # Get full text
            if not response.full_text_annotation:
                app_logger.warning("No text detected in document")
                return None, 0.0
            
            full_text = response.full_text_annotation.text
            
            # Calculate confidence
            confidence = self._calculate_document_confidence(response)
            
            app_logger.info(f"Successfully extracted {len(full_text)} characters with confidence {confidence:.2f}")
            
            return full_text, confidence
            
        except Exception as e:
            app_logger.error(f"Error during document OCR processing: {e}")
            return None, None
    
    def _calculate_confidence(self, response) -> float:
        """Calculate average confidence from text annotations"""
        if not response.text_annotations or len(response.text_annotations) <= 1:
            return 0.0
        
        # Skip first annotation (full text) and calculate average
        confidences = []
        for annotation in response.text_annotations[1:]:
            if hasattr(annotation, 'confidence'):
                confidences.append(annotation.confidence)
        
        if not confidences:
            return 0.85  # Default confidence if not available
        
        return sum(confidences) / len(confidences)
    
    def _calculate_document_confidence(self, response) -> float:
        """Calculate average confidence from document text detection"""
        if not response.full_text_annotation or not response.full_text_annotation.pages:
            return 0.0
        
        confidences = []
        for page in response.full_text_annotation.pages:
            if hasattr(page, 'confidence'):
                confidences.append(page.confidence)
        
        if not confidences:
            return 0.85  # Default confidence
        
        return sum(confidences) / len(confidences)
    
    def process_invoice_image(self, image_bytes: bytes, use_document_detection: bool = True) -> Tuple[Optional[str], Optional[float]]:
        """
        Process invoice image and extract text
        
        Args:
            image_bytes: Image data as bytes
            use_document_detection: Whether to use document text detection (better for invoices)
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if use_document_detection:
            return self.extract_text_with_document_detection(image_bytes)
        else:
            return self.extract_text_from_image(image_bytes)
    
    # ============================================
    # EXTRACCIÓN DE CAMPOS ESTRUCTURADOS
    # ============================================
    
    def extract_invoice_data(self, image_bytes: bytes) -> Dict:
        """
        Extract structured invoice data from image
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dict with extracted invoice fields
        """
        # ✅ Validación mejorada (sin modo MOCK)
        if not self.client:
            raise Exception(
                "❌ Google Cloud Vision client not initialized.\n\n"
                "Verifica que:\n"
                "1. El archivo de credenciales existe\n"
                "2. config.json tiene 'google_cloud.credentials_path' configurado\n"
                "3. La API de Vision está habilitada en Google Cloud Console\n\n"
                f"Ruta configurada: {settings.google_application_credentials}"
            )
        
        # Get OCR text
        app_logger.info("Processing image with Google Cloud Vision...")
        full_text, confidence = self.process_invoice_image(image_bytes)
        
        if not full_text:
            raise Exception("No se pudo extraer texto de la imagen")
        
        app_logger.info(f"OCR completed. Extracted {len(full_text)} characters with confidence {confidence:.2f}")
        
        # Extract structured data
        invoice_data = {
            'ncf': self._extract_ncf(full_text),
            'rnc': self._extract_rnc(full_text),
            'razon_social': self._extract_razon_social(full_text),
            'fecha_emision': self._extract_fecha(full_text),
            'subtotal': self._extract_subtotal(full_text),
            'itbis': self._extract_itbis(full_text),
            'total': self._extract_total(full_text),
            'confianza_ocr': confidence or 0.85,
            'texto_completo': full_text
        }
        
        # Calculate missing values
        if invoice_data['total'] and invoice_data['itbis'] and not invoice_data['subtotal']:
            invoice_data['subtotal'] = invoice_data['total'] - invoice_data['itbis']
        elif invoice_data['subtotal'] and invoice_data['itbis'] and not invoice_data['total']:
            invoice_data['total'] = invoice_data['subtotal'] + invoice_data['itbis']
        
        app_logger.info(f"Invoice data extracted: NCF={invoice_data['ncf']}, Total={invoice_data['total']}")
        
        return invoice_data
    
    def _extract_ncf(self, text: str) -> Optional[str]:
        """Extract NCF (Comprobante Fiscal)"""
        # ✅ Patrones mejorados para detectar más formatos
        patterns = [
            # Patrones básicos
            r'\b([BE]\d{10,11})\b',
            r'NCF[:\s]*([BE]\d{10,11})',
            r'Comprobante[:\s]*([BE]\d{10,11})',
            r'N[uú]mero[:\s]*([BE]\d{10,11})',
            
            # Con espacios o guiones
            r'\b([BE]\s?\d{2}\s?\d{8,9})\b',
            r'NCF[:\s]*([BE]\s?\d{2}\s?\d{8,9})',
            
            # Con formato específico (ej: B01-00000175)
            r'\b([BE]\d{2}[-\s]?\d{8,9})\b',
            
            # Más flexible
            r'([BE][0-9\s-]{10,15})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ncf_raw = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                # ✅ Limpiar espacios y guiones
                ncf = re.sub(r'[\s-]', '', ncf_raw)
                
                # ✅ Validar longitud
                if len(ncf) >= 11 and len(ncf) <= 13:
                    app_logger.debug(f"NCF found: {ncf}")
                    return ncf
        
        app_logger.warning("NCF not found in text")
        
        # ✅ DEBUG: Mostrar las primeras líneas del texto
        lines = text.split('\n')[:10]
        app_logger.debug(f"First 10 lines of OCR text:\n{chr(10).join(lines)}")
        
        return None
    
    def _extract_rnc(self, text: str) -> Optional[str]:
        """Extract RNC (Registro Nacional de Contribuyentes)"""
        # Pattern: 9 or 11 digits
        patterns = [
            r'RNC[:\s]*(\d{9,11})',
            r'Registro[:\s]*(\d{9,11})',
            r'Contribuyente[:\s]*(\d{9,11})',
            r'\b(\d{9})\b',
            r'\b(\d{11})\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rnc = match.group(1)
                # Validate length
                if len(rnc) in [9, 11]:
                    app_logger.debug(f"RNC found: {rnc}")
                    return rnc
        
        app_logger.warning("RNC not found in text")
        return None
    
    def _extract_razon_social(self, text: str) -> Optional[str]:
        """Extract company name (Razón Social)"""
        lines = text.split('\n')
        
        # Look for uppercase company names in first 15 lines
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            
            # Skip lines with common keywords
            skip_keywords = ['factura', 'invoice', 'ncf', 'rnc', 'fecha', 'date', 'total', 'comprobante']
            if any(keyword in line.lower() for keyword in skip_keywords):
                continue
            
            # Look for lines with mostly uppercase letters
            if len(line) > 10:
                uppercase_ratio = sum(1 for c in line if c.isupper()) / len(line)
                if uppercase_ratio > 0.6 and not re.search(r'\d{9}', line):
                    app_logger.debug(f"Razón Social found: {line}")
                    return line
        
        # Fallback: look for text after RNC
        rnc_match = re.search(r'RNC[:\s]*\d{9,11}[:\s]*(.+)', text, re.IGNORECASE)
        if rnc_match:
            razon = rnc_match.group(1).strip().split('\n')[0]
            if len(razon) > 5:
                app_logger.debug(f"Razón Social found (after RNC): {razon}")
                return razon
        
        app_logger.warning("Razón Social not found in text")
        return None
    
    def _extract_fecha(self, text: str) -> Optional[datetime]:
        """Extract invoice date"""
        # Patterns: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        patterns = [
            r'(\d{2})[/-](\d{2})[/-](\d{4})',
            r'(\d{4})[/-](\d{2})[/-](\d{2})',
            r'Fecha[:\s]*(\d{2})[/-](\d{2})[/-](\d{4})',
            r'Date[:\s]*(\d{2})[/-](\d{2})[/-](\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    
                    # Try DD/MM/YYYY
                    if len(groups) == 3:
                        if len(groups[2]) == 4:  # DD/MM/YYYY
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        else:  # YYYY/MM/DD
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        
                        fecha = datetime(year, month, day)
                        app_logger.debug(f"Fecha found: {fecha.strftime('%Y-%m-%d')}")
                        return fecha
                except ValueError:
                    continue
        
        app_logger.warning("Fecha not found, using current date")
        return datetime.now()
    
    def _extract_amount(self, text: str, keywords: list) -> Optional[float]:
        """Generic amount extractor"""
        for keyword in keywords:
            # Patterns for amounts
            patterns = [
                rf'{keyword}[:\s]*\$?\s*([\d,]+\.?\d*)',
                rf'{keyword}[:\s]*RD\$?\s*([\d,]+\.?\d*)',
                rf'{keyword}[:\s]*DOP\s*([\d,]+\.?\d*)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1).replace(',', '')
                        amount = float(value)
                        app_logger.debug(f"{keyword} found: {amount}")
                        return amount
                    except ValueError:
                        continue
        
        return None
    
    def _extract_subtotal(self, text: str) -> Optional[float]:
        """Extract subtotal"""
        keywords = ['subtotal', 'sub-total', 'sub total', 'imponible', 'base']
        return self._extract_amount(text, keywords)
    
    def _extract_itbis(self, text: str) -> Optional[float]:
        """Extract ITBIS (tax)"""
        keywords = ['itbis', 'impuesto', 'tax', 'iva']
        return self._extract_amount(text, keywords)
    
    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount"""
        keywords = ['total', 'total a pagar', 'monto total', 'gran total']
        return self._extract_amount(text, keywords)


# Global OCR processor instance
ocr_processor = OCRProcessor()