"""
Green-API WhatsApp Handler
"""
import httpx
import os
from loguru import logger as app_logger
from typing import Optional

class GreenAPIHandler:
    def __init__(self):
        self.id_instance = os.environ.get("GREENAPI_INSTANCE_ID")
        self.api_token = os.environ.get("GREENAPI_TOKEN")
        
        if self.id_instance and self.api_token:
            self.base_url = f"https://api.green-api.com/waInstance{self.id_instance}"
            self.enabled = True
            app_logger.info("✅ Green-API handler initialized")
        else:
            self.enabled = False
            app_logger.warning("⚠️ Green-API credentials not configured")
    
    def _format_phone(self, phone: str) -> str:
        """Convert whatsapp:+18293757344 to 18293757344@c.us"""
        clean = phone.replace("whatsapp:", "").replace("+", "").strip()
        return f"{clean}@c.us"
    
    async def send_message(self, to: str, message: str) -> Optional[dict]:
        """Send WhatsApp message via Green-API"""
        if not self.enabled:
            app_logger.warning("Green-API not enabled")
            return None
        
        try:
            chat_id = self._format_phone(to)
            url = f"{self.base_url}/sendMessage/{self.api_token}"
            
            payload = {
                "chatId": chat_id,
                "message": message
            }
            
            app_logger.info(f"📤 Green-API sending to {chat_id}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                app_logger.info(f"✅ Green-API message sent. ID: {result.get('idMessage')}")
                return result
                
        except Exception as e:
            app_logger.error(f"❌ Green-API error: {e}")
            return None
    
    async def send_confirmation(self, to: str):
        """Send confirmation message"""
        return await self.send_message(to, "✅ Factura recibida, procesando... ⏳")
    
    async def send_success(self, to: str, ncf: str, total: float):
        """Send success message"""
        message = f"""📄 *Lectura Exitosa*

✅ *NCF:* {ncf}
💰 *Total:* RD${total:,.2f}"""
        return await self.send_message(to, message)
    
    async def send_error(self, to: str, error_msg: str = None):
        """Send error message"""
        if error_msg:
            message = f"❌ Error: {error_msg}"
        else:
            message = "❌ No se pudo procesar la factura. Intenta con otra imagen más clara."
        return await self.send_message(to, message)
    
    async def send_partial_success(self, to: str, warnings: list):
        """Send partial success message"""
        message = f"""⚠️ *Lectura Parcial*

Advertencias:
{chr(10).join(f'• {w}' for w in warnings)}"""
        return await self.send_message(to, message)


# Global instance
greenapi_handler = GreenAPIHandler()