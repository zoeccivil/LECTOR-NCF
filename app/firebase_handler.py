"""
Firebase integration handler
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
from typing import Optional
from app.models import Invoice
from app.utils.logger import app_logger
from app.utils.config import settings


class FirebaseHandler:
    """Handles Firebase Firestore operations"""
    
    def __init__(self):
        """Initialize Firebase app"""
        try:
            if settings.firebase_credentials:
                cred = credentials.Certificate(settings.firebase_credentials)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.firebase_database_url
                })
                self.db = firestore.client()
                app_logger.info("Firebase initialized successfully")
            else:
                self.db = None
                app_logger.warning("Firebase credentials not configured")
        except Exception as e:
            app_logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None
    
    def save_invoice(self, invoice: Invoice) -> bool:
        """
        Save invoice to Firestore
        
        Args:
            invoice: Invoice object to save
            
        Returns:
            True if saved successfully
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return False
        
        try:
            # Prepare data
            invoice_data = {
                'ncf': invoice.ncf,
                'rnc': invoice.rnc,
                'razon_social': invoice.razon_social,
                'fecha_emision': invoice.fecha_emision,
                'fecha_procesamiento': invoice.fecha_procesamiento,
                'montos': {
                    'subtotal': invoice.montos.subtotal,
                    'itbis': invoice.montos.itbis,
                    'total': invoice.montos.total,
                    'moneda': invoice.montos.moneda
                },
                'metadata': {
                    'imagen_original': invoice.metadata.imagen_original,
                    'confianza_ocr': invoice.metadata.confianza_ocr,
                    'origen': invoice.metadata.origen
                }
            }
            
            # Save to Firestore
            doc_ref = self.db.collection('facturas').document(invoice.id)
            doc_ref.set(invoice_data)
            
            app_logger.info(f"Invoice saved to Firebase: {invoice.id}")
            
            # Update provider statistics
            if invoice.rnc:
                self._update_provider_stats(invoice.rnc, invoice.razon_social)
            
            return True
            
        except Exception as e:
            app_logger.error(f"Error saving to Firebase: {e}")
            return False
    
    def _update_provider_stats(self, rnc: str, razon_social: Optional[str]):
        """Update provider statistics"""
        try:
            provider_ref = self.db.collection('proveedores').document(rnc)
            provider_doc = provider_ref.get()
            
            if provider_doc.exists:
                # Increment counter
                provider_ref.update({
                    'total_facturas': firestore.Increment(1)
                })
            else:
                # Create new provider
                provider_ref.set({
                    'rnc': rnc,
                    'razon_social': razon_social or '',
                    'total_facturas': 1
                })
                
        except Exception as e:
            app_logger.error(f"Error updating provider stats: {e}")


# Global Firebase handler instance
firebase_handler = FirebaseHandler()