"""
Firebase integration handler - ADAPTED FOR FACOT-APP STRUCTURE
Adapts LECTOR-NCF to work with existing /companies/ and /invoices/ collections
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Dict, List
from datetime import datetime
from app.models import Invoice
from app.utils.logger import app_logger

# Import config_manager
from gui.utils.config_manager import config_manager


class FirebaseHandler:
    """Handles Firebase Firestore operations - Adapted for facot-app structure"""
    
    def __init__(self):
        """Initialize Firebase app"""
        try:
            # Read credentials from config.json
            cred_path = config_manager.get_firebase_credentials_path()
            db_url = config_manager.get_firebase_database_url()
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': db_url
                })
                self.db = firestore.client()
                app_logger.info("Firebase Firestore initialized successfully")
                app_logger.info(f"Project: {config_manager.get_firebase_project_id()}")
                app_logger.info("Using adapted structure: /companies/ and /invoices/")
            else:
                self.db = None
                app_logger.warning("Firebase credentials not configured")
        except ValueError as e:
            # Firebase app already initialized
            app_logger.info("Firebase app already initialized, using existing instance")
            self.db = firestore.client()
        except Exception as e:
            app_logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None
    
    # ============================================================================
    # ADAPTED METHODS FOR /companies/ collection
    # ============================================================================
    
    def get_empresas(self) -> List[Dict]:
        """
        Get companies from /companies/ collection.
        Adapted to match LECTOR-NCF expected format.
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            companies_ref = self.db.collection('companies')
            docs = companies_ref.stream()
            
            empresas = []
            for doc in docs:
                data = doc.to_dict()
                
                # Count invoices for this company
                try:
                    company_id_int = int(doc.id)
                    invoice_count = self.db.collection('invoices') \
                        .where('company_id', '==', company_id_int) \
                        .count() \
                        .get()[0][0].value
                except:
                    invoice_count = 0
                
                empresas.append({
                    'id': f"comp_{doc.id}",  # Format: comp_1, comp_2, etc.
                    'rnc': data.get('rnc', ''),
                    'nombre': data.get('name', ''),
                    'total_facturas': invoice_count,
                    'direccion': data.get('address', ''),
                    'telefono': data.get('phone', ''),
                    'email': data.get('email', ''),
                    '_original_id': doc.id  # Keep original ID for queries
                })
            
            app_logger.info(f"Loaded {len(empresas)} empresas")
            return empresas
        
        except Exception as e:
            app_logger.error(f"Error getting empresas: {e}")
            return []
    
    def get_empresa(self, empresa_id: str) -> Optional[Dict]:
        """
        Get a specific company.
        empresa_id format: "comp_1", "comp_2", etc.
        """
        if not self.db:
            return None
        
        try:
            # Extract original ID (comp_1 -> 1)
            original_id = empresa_id.replace('comp_', '')
            
            doc = self.db.collection('companies').document(original_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                return {
                    'id': empresa_id,
                    'rnc': data.get('rnc', ''),
                    'nombre': data.get('name', ''),
                    '_original_id': original_id
                }
            
            return None
        
        except Exception as e:
            app_logger.error(f"Error getting empresa {empresa_id}: {e}")
            return None
    
    # ============================================================================
    # ADAPTED METHODS FOR /invoices/ collection
    # ============================================================================
    
    def get_facturas_by_empresa(self, empresa_id: str) -> List[Dict]:
        """
        Get invoices from /invoices/ filtered by company_id.
        empresa_id format: "comp_1", "comp_2", etc.
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            # Extract original company ID
            company_id = int(empresa_id.replace('comp_', ''))
            
            # Query invoices
            invoices_ref = self.db.collection('invoices') \
                .where('company_id', '==', company_id) \
                .order_by('invoice_date', direction=firestore.Query.DESCENDING) \
                .limit(1000)  # Safety limit
            
            docs = invoices_ref.stream()
            
            facturas = []
            for doc in docs:
                data = doc.to_dict()
                
                # Parse invoice_date (can be datetime or string)
                fecha_emision = data.get('invoice_date', '')
                if hasattr(fecha_emision, 'strftime'):
                    fecha_emision = fecha_emision.strftime('%Y-%m-%d')
                elif isinstance(fecha_emision, str):
                    # Already string, keep as is
                    pass
                else:
                    fecha_emision = ''
                
                # Calculate subtotal (total - itbis)
                total = float(data.get('total_amount', 0))
                itbis = float(data.get('itbis', 0))
                subtotal = total - itbis
                
                # Determine if reviewed (has category assigned)
                revisada = data.get('invoice_category') is not None
                
                # Map to LECTOR-NCF format
                factura = {
                    'id': doc.id,
                    'ncf': data.get('ncf', data.get('invoice_number', '')),
                    'rnc': data.get('rnc', ''),
                    'razon_social': data.get('third_party_name', data.get('client_name', '')),
                    'fecha_emision': fecha_emision,
                    'subtotal': subtotal,
                    'itbis': itbis,
                    'total': total,
                    'moneda': data.get('currency', 'DOP'),
                    'tipo_factura': data.get('invoice_type', 'Compra'),
                    'categoria': data.get('invoice_category', ''),
                    'imagen_original': data.get('attachment_storage_path', data.get('attachment_path', '')),
                    'pdf_path': data.get('pdf_path', ''),
                    'revisada': revisada,
                    'exportada': False,  # You can add logic here if you track exports
                    'confianza_ocr': 1.0,  # Not tracked in your system
                    '_original_data': data  # Keep original for reference
                }
                
                facturas.append(factura)
            
            app_logger.info(f"Loaded {len(facturas)} facturas for empresa {empresa_id}")
            return facturas
        
        except Exception as e:
            app_logger.error(f"Error getting facturas for empresa {empresa_id}: {e}")
            return []
    
    def get_factura(self, empresa_id: str, factura_id: str) -> Optional[Dict]:
        """
        Get a specific invoice.
        """
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('invoices').document(factura_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Parse date
                fecha_emision = data.get('invoice_date', '')
                if hasattr(fecha_emision, 'strftime'):
                    fecha_emision = fecha_emision.strftime('%Y-%m-%d')
                
                # Calculate subtotal
                total = float(data.get('total_amount', 0))
                itbis = float(data.get('itbis', 0))
                subtotal = total - itbis
                
                return {
                    'id': factura_id,
                    'ncf': data.get('ncf', data.get('invoice_number', '')),
                    'rnc': data.get('rnc', ''),
                    'razon_social': data.get('third_party_name', data.get('client_name', '')),
                    'fecha_emision': fecha_emision,
                    'subtotal': subtotal,
                    'itbis': itbis,
                    'total': total,
                    'moneda': data.get('currency', 'DOP'),
                    'tipo_factura': data.get('invoice_type', 'Compra'),
                    'categoria': data.get('invoice_category', ''),
                    'imagen_original': data.get('attachment_storage_path', data.get('attachment_path', '')),
                    'pdf_path': data.get('pdf_path', ''),
                    'revisada': data.get('invoice_category') is not None,
                    'exportada': False,
                    'confianza_ocr': 1.0,
                    '_original_data': data
                }
            
            return None
        
        except Exception as e:
            app_logger.error(f"Error getting factura {factura_id}: {e}")
            return None
    
    # ============================================================================
    # UPDATE METHODS
    # ============================================================================
    
    def update_factura(self, empresa_id: str, factura_id: str, updates: Dict) -> bool:
        """
        Update an invoice.
        Maps LECTOR-NCF fields to facot-app structure.
        """
        if not self.db:
            return False
        
        try:
            # Map LECTOR-NCF fields to facot-app fields
            facot_updates = {}
            
            if 'ncf' in updates:
                facot_updates['ncf'] = updates['ncf']
            
            if 'rnc' in updates:
                facot_updates['rnc'] = updates['rnc']
            
            if 'razon_social' in updates:
                facot_updates['third_party_name'] = updates['razon_social']
            
            if 'fecha_emision' in updates:
                # Convert string to datetime if needed
                fecha = updates['fecha_emision']
                if isinstance(fecha, str):
                    fecha = datetime.strptime(fecha, '%Y-%m-%d')
                facot_updates['invoice_date'] = fecha
            
            if 'total' in updates:
                facot_updates['total_amount'] = float(updates['total'])
                facot_updates['total_amount_rd'] = float(updates['total'])
            
            if 'itbis' in updates:
                facot_updates['itbis'] = float(updates['itbis'])
            
            if 'subtotal' in updates:
                # Subtotal is calculated, not stored separately in facot-app
                pass
            
            # Add updated_at timestamp
            facot_updates['updated_at'] = datetime.now().isoformat()
            
            # Update document
            self.db.collection('invoices').document(factura_id).update(facot_updates)
            
            app_logger.info(f"Updated factura {factura_id}")
            return True
        
        except Exception as e:
            app_logger.error(f"Error updating factura {factura_id}: {e}")
            return False
    
    def mark_factura_revisada(self, empresa_id: str, factura_id: str) -> bool:
        """
        Mark invoice as reviewed.
        In facot-app, this means assigning a category if not already assigned.
        """
        if not self.db:
            return False
        
        try:
            # Get current invoice
            doc = self.db.collection('invoices').document(factura_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Only update if not already categorized
                if not data.get('invoice_category'):
                    self.db.collection('invoices').document(factura_id).update({
                        'invoice_category': 'Revisada',  # Or use your category system
                        'updated_at': datetime.now().isoformat()
                    })
                
                app_logger.info(f"Marked factura {factura_id} as revisada")
                return True
            
            return False
        
        except Exception as e:
            app_logger.error(f"Error marking factura {factura_id} as revisada: {e}")
            return False
    
    def mark_factura_exportada(self, empresa_id: str, factura_id: str) -> bool:
        """
        Mark invoice as exported.
        You can add an 'exportada' field to your invoices if needed.
        """
        if not self.db:
            return False
        
        try:
            self.db.collection('invoices').document(factura_id).update({
                'exportada': True,
                'exported_at': datetime.now().isoformat()
            })
            
            app_logger.info(f"Marked factura {factura_id} as exportada")
            return True
        
        except Exception as e:
            app_logger.error(f"Error marking factura {factura_id} as exportada: {e}")
            return False
    
    # ============================================================================
    # FILTER METHODS
    # ============================================================================
    
    def get_facturas_pendientes(self, empresa_id: str) -> List[Dict]:
        """Get invoices that haven't been reviewed (no category assigned)."""
        if not self.db:
            return []
        
        try:
            company_id = int(empresa_id.replace('comp_', ''))
            
            invoices_ref = self.db.collection('invoices') \
                .where('company_id', '==', company_id) \
                .where('invoice_category', '==', None) \
                .order_by('invoice_date', direction=firestore.Query.DESCENDING)
            
            docs = invoices_ref.stream()
            
            facturas = []
            for doc in docs:
                data = doc.to_dict()
                
                fecha_emision = data.get('invoice_date', '')
                if hasattr(fecha_emision, 'strftime'):
                    fecha_emision = fecha_emision.strftime('%Y-%m-%d')
                
                total = float(data.get('total_amount', 0))
                itbis = float(data.get('itbis', 0))
                
                facturas.append({
                    'id': doc.id,
                    'ncf': data.get('ncf', data.get('invoice_number', '')),
                    'rnc': data.get('rnc', ''),
                    'razon_social': data.get('third_party_name', ''),
                    'fecha_emision': fecha_emision,
                    'subtotal': total - itbis,
                    'itbis': itbis,
                    'total': total,
                    'revisada': False,
                    'exportada': False
                })
            
            return facturas
        
        except Exception as e:
            app_logger.error(f"Error getting facturas pendientes: {e}")
            return []
    
    def get_facturas_para_exportar(self, empresa_id: str) -> List[Dict]:
        """Get invoices ready for export (reviewed but not exported)."""
        # Since we don't track 'exportada' yet, return all with category
        if not self.db:
            return []
        
        try:
            company_id = int(empresa_id.replace('comp_', ''))
            
            # Get all invoices with a category (reviewed)
            invoices_ref = self.db.collection('invoices') \
                .where('company_id', '==', company_id) \
                .order_by('invoice_date', direction=firestore.Query.DESCENDING)
            
            docs = invoices_ref.stream()
            
            facturas = []
            for doc in docs:
                data = doc.to_dict()
                
                # Only include if has category and not exported
                if data.get('invoice_category') and not data.get('exportada'):
                    fecha_emision = data.get('invoice_date', '')
                    if hasattr(fecha_emision, 'strftime'):
                        fecha_emision = fecha_emision.strftime('%Y-%m-%d')
                    
                    total = float(data.get('total_amount', 0))
                    itbis = float(data.get('itbis', 0))
                    
                    facturas.append({
                        'id': doc.id,
                        'ncf': data.get('ncf', data.get('invoice_number', '')),
                        'rnc': data.get('rnc', ''),
                        'razon_social': data.get('third_party_name', ''),
                        'fecha_emision': fecha_emision,
                        'subtotal': total - itbis,
                        'itbis': itbis,
                        'total': total,
                        'revisada': True,
                        'exportada': False
                    })
            
            return facturas
        
        except Exception as e:
            app_logger.error(f"Error getting facturas para exportar: {e}")
            return []
    
    # ============================================================================
    # DELETE METHOD
    # ============================================================================
    
    def delete_factura(self, empresa_id: str, factura_id: str) -> bool:
        """Delete an invoice."""
        if not self.db:
            return False
        
        try:
            self.db.collection('invoices').document(factura_id).delete()
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
    
    def get_ocr_facturas_by_empresa(self, empresa_id: str, estado: str = None) -> List[Dict]:
        """
        Get OCR-processed invoices from /ocr_invoices/ collection.
        estado: 'pendiente', 'revisada', 'exportada', or None (all)
        """
        if not self.db:
            app_logger.warning("Firebase not initialized")
            return []
        
        try:
            # Extract original company ID
            company_id = int(empresa_id.replace('comp_', ''))
            
            # Build query
            query = self.db.collection('ocr_invoices') \
                .where('company_id', '==', company_id)
            
            # Filter by estado if provided
            if estado:
                query = query.where('estado', '==', estado)
            
            # ⚠️ TEMPORAL: Comentado hasta que el índice esté listo
            # query = query.order_by('processed_at', direction=firestore.Query.DESCENDING)
            
            docs = query.stream()
            
            facturas = []
            for doc in docs:
                data = doc.to_dict()
                
                # Parse processed_at
                processed_at = data.get('processed_at', '')
                if hasattr(processed_at, 'strftime'):
                    processed_at_str = processed_at.strftime('%Y-%m-%d %H:%M')
                else:
                    processed_at_str = str(processed_at)
                
                # Parse fecha_emision
                fecha_emision = data.get('fecha_emision', '')
                if hasattr(fecha_emision, 'strftime'):
                    fecha_emision = fecha_emision.strftime('%Y-%m-%d')
                
                factura = {
                    'id': doc.id,
                    'ncf': data.get('ncf', ''),
                    'rnc': data.get('rnc', ''),
                    'razon_social': data.get('razon_social', ''),
                    'fecha_emision': fecha_emision,
                    'subtotal': float(data.get('subtotal', 0)),
                    'itbis': float(data.get('itbis', 0)),
                    'total': float(data.get('total', 0)),
                    'imagen_original': data.get('imagen_original', ''),
                    'confianza_ocr': float(data.get('confianza_ocr', 0)),
                    'revisada': data.get('revisada', False),
                    'exportada': data.get('exportada', False),
                    'estado': data.get('estado', 'pendiente'),
                    'processed_at': processed_at_str,
                    '_ocr_invoice': True
                }
                
                facturas.append(factura)
            
            # ✅ Ordenar manualmente en Python (mientras el índice se crea)
            facturas.sort(key=lambda x: x.get('processed_at', ''), reverse=True)
            
            app_logger.info(f"Loaded {len(facturas)} OCR facturas for empresa {empresa_id} (estado: {estado or 'all'})")
            return facturas
        
        except Exception as e:
            app_logger.error(f"Error getting OCR facturas: {e}")
            import traceback
            traceback.print_exc()
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


    def save_ocr_invoice(self, invoice: Dict, empresa_id: str, whatsapp_msg_id: str) -> str:
        """
        Save OCR-processed invoice to /ocr_invoices/ collection
        
        Args:
            invoice: Invoice data dict
            empresa_id: Empresa ID
            whatsapp_msg_id: WhatsApp message ID or manual ID
            
        Returns:
            Document ID of saved invoice
        """
        if not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            # Add to collection
            doc_ref = self.db.collection('ocr_invoices').add(invoice)
            doc_id = doc_ref[1].id
            
            app_logger.info(f"OCR invoice saved: {doc_id} (NCF: {invoice.get('ncf', 'N/A')})")
            return doc_id
            
        except Exception as e:
            app_logger.error(f"Error saving OCR invoice: {e}")
            raise


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


# Create singleton instance
firebase_handler = FirebaseHandler()