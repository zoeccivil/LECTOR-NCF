"""
Script para poblar /ocr_invoices/ con datos de prueba
Copia las últimas 20 facturas de /invoices/ a /ocr_invoices/ para testing
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from datetime import datetime
from gui.utils.config_manager import config_manager
import firebase_admin
from firebase_admin import credentials, firestore


def populate_ocr_invoices():
    """Populate /ocr_invoices/ with test data from /invoices/"""
    
    print("🔥 Conectando a Firebase...")
    
    # Initialize Firebase
    cred_path = config_manager.get_firebase_credentials_path()
    
    try:
        firebase_admin.delete_app(firebase_admin.get_app())
    except:
        pass
    
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    print("✅ Conexión establecida\n")
    
    # Get companies
    print("📂 Obteniendo empresas...")
    companies = {}
    for doc in db.collection('companies').stream():
        companies[int(doc.id)] = doc.to_dict()
    
    print(f"✅ {len(companies)} empresas encontradas\n")
    
    # Get last 20 invoices from each company
    total_copied = 0
    
    for company_id, company_data in companies.items():
        company_name = company_data.get('name', f'Company {company_id}')
        
        print(f"📋 Procesando: {company_name}")
        
        # Get last 20 invoices for this company
        try:
            invoices = db.collection('invoices') \
                .where('company_id', '==', company_id) \
                .order_by('invoice_date', direction=firestore.Query.DESCENDING) \
                .limit(20) \
                .stream()
            
            count = 0
            for invoice_doc in invoices:
                invoice_data = invoice_doc.to_dict()
                
                # Parse date
                invoice_date = invoice_data.get('invoice_date')
                if hasattr(invoice_date, 'strftime'):
                    fecha_emision = invoice_date
                elif isinstance(invoice_date, str):
                    try:
                        fecha_emision = datetime.strptime(invoice_date, '%Y-%m-%d')
                    except:
                        fecha_emision = datetime.now()
                else:
                    fecha_emision = datetime.now()
                
                # Calculate values
                total = float(invoice_data.get('total_amount', 0))
                itbis = float(invoice_data.get('itbis', 0))
                subtotal = total - itbis
                
                # Determine estado (random for testing)
                import random
                estados = ['pendiente', 'pendiente', 'revisada', 'exportada']  # More pendientes
                estado = random.choice(estados)
                
                # Create OCR invoice
                ocr_invoice = {
                    'company_id': company_id,
                    'ncf': invoice_data.get('ncf', invoice_data.get('invoice_number', 'N/A')),
                    'rnc': invoice_data.get('rnc', ''),
                    'razon_social': invoice_data.get('third_party_name', invoice_data.get('client_name', '')),
                    'fecha_emision': fecha_emision,
                    'subtotal': subtotal,
                    'itbis': itbis,
                    'total': total,
                    'imagen_original': invoice_data.get('attachment_storage_path', ''),
                    'whatsapp_message_id': f'test_{invoice_doc.id}',
                    'processed_at': datetime.now(),
                    'confianza_ocr': 0.95,
                    'revisada': estado in ['revisada', 'exportada'],
                    'exportada': estado == 'exportada',
                    'estado': estado,
                    '_migrated_from': invoice_doc.id,  # Keep reference
                    '_test_data': True  # Flag as test data
                }
                
                # Add to /ocr_invoices/
                db.collection('ocr_invoices').add(ocr_invoice)
                count += 1
            
            print(f"   ✅ {count} facturas copiadas")
            total_copied += count
            
        except Exception as e:
            print(f"   ⚠️ Error: {str(e)}")
            continue
    
    print(f"\n🎉 COMPLETADO: {total_copied} facturas copiadas a /ocr_invoices/")
    print("\n✨ Ahora puedes recargar la GUI y ver las facturas OCR")
    print("   Presiona 🔄 Refresh en la aplicación")


if __name__ == '__main__':
    print("=" * 60)
    print("  LECTOR-NCF - Poblar /ocr_invoices/ con datos de prueba")
    print("=" * 60)
    print("\n⚠️  Este script copiará las últimas 20 facturas de cada empresa")
    print("    de /invoices/ a /ocr_invoices/ para testing.\n")
    
    response = input("¿Continuar? (s/n): ")
    
    if response.lower() == 's':
        try:
            populate_ocr_invoices()
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ Cancelado")