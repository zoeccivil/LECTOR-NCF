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
    
    # GUI-specific methods
    
    def get_empresas(self) -> list:
        """
        Get all empresas (companies) from Firestore
        
        Returns:
            List of empresa dictionaries with id, rnc, nombre, total_facturas
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            empresas_ref = self.db.collection('empresas')
            empresas = []
            
            for doc in empresas_ref.stream():
                empresa_data = doc.to_dict()
                empresa_data['id'] = doc.id
                empresas.append(empresa_data)
            
            app_logger.info(f"Loaded {len(empresas)} empresas")
            return empresas
            
        except Exception as e:
            app_logger.error(f"Error getting empresas: {e}")
            return []
    
    def get_facturas_by_empresa(self, empresa_id: str) -> list:
        """
        Get all facturas for a specific empresa
        
        Args:
            empresa_id: Empresa document ID
            
        Returns:
            List of factura dictionaries
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            facturas_ref = self.db.collection('facturas').document(empresa_id).collection('items')
            facturas = []
            
            for doc in facturas_ref.stream():
                factura_data = doc.to_dict()
                factura_data['id'] = doc.id
                facturas.append(factura_data)
            
            app_logger.info(f"Loaded {len(facturas)} facturas for empresa {empresa_id}")
            return facturas
            
        except Exception as e:
            app_logger.error(f"Error getting facturas for empresa {empresa_id}: {e}")
            return []
    
    def get_factura(self, empresa_id: str, factura_id: str) -> Optional[dict]:
        """
        Get a specific factura
        
        Args:
            empresa_id: Empresa document ID
            factura_id: Factura document ID
            
        Returns:
            Factura dictionary or None
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return None
        
        try:
            factura_ref = self.db.collection('facturas').document(empresa_id).collection('items').document(factura_id)
            factura_doc = factura_ref.get()
            
            if factura_doc.exists:
                factura_data = factura_doc.to_dict()
                factura_data['id'] = factura_doc.id
                return factura_data
            else:
                app_logger.warning(f"Factura {factura_id} not found")
                return None
                
        except Exception as e:
            app_logger.error(f"Error getting factura {factura_id}: {e}")
            return None
    
    def update_factura(self, empresa_id: str, factura_id: str, updates: dict) -> bool:
        """
        Update factura fields
        
        Args:
            empresa_id: Empresa document ID
            factura_id: Factura document ID
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return False
        
        try:
            factura_ref = self.db.collection('facturas').document(empresa_id).collection('items').document(factura_id)
            factura_ref.update(updates)
            
            app_logger.info(f"Updated factura {factura_id}: {list(updates.keys())}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error updating factura {factura_id}: {e}")
            return False
    
    def mark_factura_revisada(self, empresa_id: str, factura_id: str) -> bool:
        """
        Mark factura as reviewed
        
        Args:
            empresa_id: Empresa document ID
            factura_id: Factura document ID
            
        Returns:
            True if updated successfully
        """
        return self.update_factura(empresa_id, factura_id, {'revisada': True})
    
    def mark_factura_exportada(self, empresa_id: str, factura_id: str) -> bool:
        """
        Mark factura as exported
        
        Args:
            empresa_id: Empresa document ID
            factura_id: Factura document ID
            
        Returns:
            True if updated successfully
        """
        return self.update_factura(empresa_id, factura_id, {'exportada': True})
    
    def get_facturas_pendientes(self, empresa_id: str) -> list:
        """
        Get pending (not reviewed) facturas for an empresa
        
        Args:
            empresa_id: Empresa document ID
            
        Returns:
            List of pending factura dictionaries
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            facturas_ref = self.db.collection('facturas').document(empresa_id).collection('items')
            facturas = []
            
            # Query for pending facturas (revisada == False or not set)
            query = facturas_ref.where('revisada', '==', False)
            
            for doc in query.stream():
                factura_data = doc.to_dict()
                factura_data['id'] = doc.id
                facturas.append(factura_data)
            
            app_logger.info(f"Loaded {len(facturas)} pending facturas for empresa {empresa_id}")
            return facturas
            
        except Exception as e:
            app_logger.error(f"Error getting pending facturas for empresa {empresa_id}: {e}")
            return []
    
    def get_facturas_para_exportar(self, empresa_id: str) -> list:
        """
        Get facturas ready for export (reviewed but not exported)
        
        Args:
            empresa_id: Empresa document ID
            
        Returns:
            List of factura dictionaries ready for export
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            facturas_ref = self.db.collection('facturas').document(empresa_id).collection('items')
            facturas = []
            
            # Query for reviewed but not exported facturas
            query = facturas_ref.where('revisada', '==', True).where('exportada', '==', False)
            
            for doc in query.stream():
                factura_data = doc.to_dict()
                factura_data['id'] = doc.id
                facturas.append(factura_data)
            
            app_logger.info(f"Loaded {len(facturas)} facturas ready for export for empresa {empresa_id}")
            return facturas
            
        except Exception as e:
            app_logger.error(f"Error getting facturas for export for empresa {empresa_id}: {e}")
            return []
    
    def delete_factura(self, empresa_id: str, factura_id: str) -> bool:
        """
        Delete a factura
        
        Args:
            empresa_id: Empresa document ID
            factura_id: Factura document ID
            
        Returns:
            True if deleted successfully
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return False
        
        try:
            factura_ref = self.db.collection('facturas').document(empresa_id).collection('items').document(factura_id)
            factura_ref.delete()
            
            app_logger.info(f"Deleted factura {factura_id}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error deleting factura {factura_id}: {e}")
            return False
    
    # OCR Invoices Methods - New Collection for WhatsApp OCR Invoices
    
    def save_ocr_invoice(self, invoice_data: dict, empresa_id: int, whatsapp_msg_id: str = None) -> bool:
        """
        Save OCR invoice to /ocr_invoices/ collection
        
        Args:
            invoice_data: Invoice data dictionary
            empresa_id: Company ID
            whatsapp_msg_id: WhatsApp message ID (optional)
            
        Returns:
            True if saved successfully
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return False
        
        try:
            from datetime import datetime
            import uuid
            
            # Prepare OCR invoice data
            ocr_invoice = {
                'id': invoice_data.get('id', str(uuid.uuid4())),
                'company_id': empresa_id,
                'ncf': invoice_data.get('ncf'),
                'rnc': invoice_data.get('rnc'),
                'razon_social': invoice_data.get('razon_social'),
                'fecha_emision': invoice_data.get('fecha_emision'),
                'subtotal': invoice_data.get('subtotal', 0.0),
                'itbis': invoice_data.get('itbis', 0.0),
                'total': invoice_data.get('total', 0.0),
                'imagen_original': invoice_data.get('imagen_original'),
                'whatsapp_message_id': whatsapp_msg_id,
                'processed_at': firestore.SERVER_TIMESTAMP,
                'confianza_ocr': invoice_data.get('confianza_ocr', 0.0),
                'revisada': False,
                'exportada': False,
                'estado': 'pendiente'
            }
            
            # Save to /ocr_invoices/ collection
            doc_ref = self.db.collection('ocr_invoices').document(ocr_invoice['id'])
            doc_ref.set(ocr_invoice)
            
            app_logger.info(f"OCR invoice saved to Firebase: {ocr_invoice['id']}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error saving OCR invoice to Firebase: {e}")
            return False
    
    def get_ocr_facturas_by_empresa(self, empresa_id: int, estado: str = None) -> list:
        """
        Get OCR invoices for a specific company
        
        Args:
            empresa_id: Company ID
            estado: Optional filter by status ('pendiente', 'revisada', 'exportada')
            
        Returns:
            List of OCR invoice dictionaries
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            # Query by company_id
            query = self.db.collection('ocr_invoices').where('company_id', '==', empresa_id)
            
            # Add status filter if provided
            if estado:
                query = query.where('estado', '==', estado)
            
            # Order by processed_at descending
            query = query.order_by('processed_at', direction=firestore.Query.DESCENDING)
            
            facturas = []
            for doc in query.stream():
                factura_data = doc.to_dict()
                factura_data['id'] = doc.id
                facturas.append(factura_data)
            
            app_logger.info(f"Loaded {len(facturas)} OCR facturas for empresa {empresa_id}")
            return facturas
            
        except Exception as e:
            app_logger.error(f"Error getting OCR facturas for empresa {empresa_id}: {e}")
            return []
    
    def get_ocr_factura(self, factura_id: str) -> Optional[dict]:
        """
        Get a specific OCR invoice
        
        Args:
            factura_id: OCR Invoice document ID
            
        Returns:
            OCR invoice dictionary or None
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return None
        
        try:
            doc_ref = self.db.collection('ocr_invoices').document(factura_id)
            doc = doc_ref.get()
            
            if doc.exists:
                factura_data = doc.to_dict()
                factura_data['id'] = doc.id
                return factura_data
            else:
                app_logger.warning(f"OCR factura {factura_id} not found")
                return None
                
        except Exception as e:
            app_logger.error(f"Error getting OCR factura {factura_id}: {e}")
            return None
    
    def update_ocr_factura(self, factura_id: str, updates: dict) -> bool:
        """
        Update OCR invoice fields
        
        Args:
            factura_id: OCR Invoice document ID
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return False
        
        try:
            doc_ref = self.db.collection('ocr_invoices').document(factura_id)
            doc_ref.update(updates)
            
            app_logger.info(f"Updated OCR factura {factura_id}: {list(updates.keys())}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error updating OCR factura {factura_id}: {e}")
            return False
    
    def mark_ocr_factura_revisada(self, factura_id: str) -> bool:
        """
        Mark OCR invoice as reviewed
        
        Args:
            factura_id: OCR Invoice document ID
            
        Returns:
            True if updated successfully
        """
        from datetime import datetime
        
        return self.update_ocr_factura(factura_id, {
            'revisada': True,
            'estado': 'revisada',
            'reviewed_at': firestore.SERVER_TIMESTAMP
        })
    
    def mark_ocr_factura_exportada(self, factura_id: str) -> bool:
        """
        Mark OCR invoice as exported
        
        Args:
            factura_id: OCR Invoice document ID
            
        Returns:
            True if updated successfully
        """
        return self.update_ocr_factura(factura_id, {
            'exportada': True,
            'estado': 'exportada',
            'exported_at': firestore.SERVER_TIMESTAMP
        })
    
    def delete_ocr_factura(self, factura_id: str) -> bool:
        """
        Delete an OCR invoice
        
        Args:
            factura_id: OCR Invoice document ID
            
        Returns:
            True if deleted successfully
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return False
        
        try:
            doc_ref = self.db.collection('ocr_invoices').document(factura_id)
            doc_ref.delete()
            
            app_logger.info(f"Deleted OCR factura {factura_id}")
            return True
            
        except Exception as e:
            app_logger.error(f"Error deleting OCR factura {factura_id}: {e}")
            return False
    
    def get_ocr_facturas_count_by_empresa(self, empresa_id: int) -> dict:
        """
        Get count of OCR invoices by status for a company
        
        Args:
            empresa_id: Company ID
            
        Returns:
            Dictionary with counts by status
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return {'pendiente': 0, 'revisada': 0, 'exportada': 0}
        
        try:
            counts = {'pendiente': 0, 'revisada': 0, 'exportada': 0}
            
            # Get all OCR invoices for this company
            query = self.db.collection('ocr_invoices').where('company_id', '==', empresa_id)
            
            for doc in query.stream():
                data = doc.to_dict()
                estado = data.get('estado', 'pendiente')
                counts[estado] = counts.get(estado, 0) + 1
            
            return counts
            
        except Exception as e:
            app_logger.error(f"Error getting OCR facturas count for empresa {empresa_id}: {e}")
            return {'pendiente': 0, 'revisada': 0, 'exportada': 0}


# Global Firebase handler instance
firebase_handler = FirebaseHandler()