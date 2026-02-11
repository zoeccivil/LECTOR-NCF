"""
WhatsApp message handler using Twilio API
"""
from twilio.rest import Client
from typing import Optional
import httpx
from app.utils.logger import app_logger
from app.utils.config import settings


class WhatsAppHandler:
    """Handles WhatsApp messaging via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        try:
            if settings.twilio_account_sid and settings.twilio_auth_token:
                self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                app_logger.info("Twilio WhatsApp client initialized")
            else:
                self.client = None
                app_logger.warning("Twilio credentials not configured")
        except Exception as e:
            app_logger.error(f"Failed to initialize Twilio client: {e}")
            self.client = None
    
    async def download_media(self, media_url: str, auth_token: Optional[str] = None) -> Optional[bytes]:
        """
        Download media from Twilio URL
        
        Args:
            media_url: URL of the media file
            auth_token: Twilio auth token for authentication
            
        Returns:
            Media content as bytes or None if failed
        """
        try:
            app_logger.info(f"Downloading media from: {media_url}")
            
            # Use auth if provided
            auth = None
            if settings.twilio_account_sid and auth_token:
                auth = (settings.twilio_account_sid, auth_token)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(media_url, auth=auth, timeout=30.0)
                response.raise_for_status()
                
                content = response.content
                app_logger.info(f"Downloaded {len(content)} bytes")
                return content
                
        except Exception as e:
            app_logger.error(f"Error downloading media: {e}")
            return None
    
    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message to a number
        
        Args:
            to_number: Recipient's WhatsApp number (format: whatsapp:+1234567890)
            message: Message text to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            app_logger.error("Twilio client not initialized")
            return False
        
        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            app_logger.info(f"Sending WhatsApp message to {to_number}")
            
            message_obj = self.client.messages.create(
                from_=settings.twilio_whatsapp_number,
                to=to_number,
                body=message
            )
            
            app_logger.info(f"Message sent successfully. SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_confirmation(self, to_number: str) -> bool:
        """
        Send confirmation message that invoice is being processed
        
        Args:
            to_number: Recipient's WhatsApp number
            
        Returns:
            True if sent successfully
        """
        message = "✅ Factura recibida, procesando..."
        return self.send_message(to_number, message)
    
    def send_success(self, to_number: str, ncf: str, total: Optional[float] = None) -> bool:
        """
        Send success message with invoice details
        
        Args:
            to_number: Recipient's WhatsApp number
            ncf: NCF number
            total: Total amount
            
        Returns:
            True if sent successfully
        """
        if total:
            message = f"✅ Factura NCF: {ncf} - Monto: RD${total:,.2f} - Procesada correctamente"
        else:
            message = f"✅ Factura NCF: {ncf} - Procesada correctamente"
        
        return self.send_message(to_number, message)
    
    def send_error(self, to_number: str, error_detail: Optional[str] = None) -> bool:
        """
        Send error message
        
        Args:
            to_number: Recipient's WhatsApp number
            error_detail: Optional error detail
            
        Returns:
            True if sent successfully
        """
        message = "❌ No se pudo leer la factura. Por favor, envía una foto más clara."
        if error_detail:
            message += f"\n\nDetalle: {error_detail}"
        
        return self.send_message(to_number, message)
    
    def send_partial_success(self, to_number: str, warnings: list) -> bool:
        """
        Send partial success message with warnings
        
        Args:
            to_number: Recipient's WhatsApp number
            warnings: List of warning messages
            
        Returns:
            True if sent successfully
        """
        message = "⚠️ Factura procesada parcialmente.\n\n"
        message += "Algunos datos no pudieron ser extraídos:\n"
        for warning in warnings:
            message += f"• {warning}\n"
        
        return self.send_message(to_number, message)


# Global WhatsApp handler instance
whatsapp_handler = WhatsAppHandler()
