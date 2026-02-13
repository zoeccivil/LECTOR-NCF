"""
Diagnóstico de configuración WhatsApp
"""
import os
from pathlib import Path

print("="*60)
print("DIAGNÓSTICO DE WHATSAPP")
print("="*60)

# 1. Verificar archivos
files_to_check = [
    'app/whatsapp_handler.py',
    'app/main.py',
    'server.py',
    'webhook_server.py'
]

print("\n📁 ARCHIVOS ENCONTRADOS:")
for file in files_to_check:
    path = Path(file)
    status = "✅" if path.exists() else "❌"
    print(f"{status} {file}")

# 2. Verificar config
print("\n��️  CONFIGURACIÓN:")
try:
    from gui.utils.config_manager import config_manager
    
    sid = config_manager.get_twilio_account_sid()
    token = config_manager.get_twilio_auth_token()
    number = config_manager.get_twilio_whatsapp_number()
    
    print(f"Account SID: {'✅ Configurado' if sid else '❌ Falta'}")
    print(f"Auth Token: {'✅ Configurado' if token else '❌ Falta'}")
    print(f"WhatsApp Number: {number if number else '❌ Falta'}")
    
    if sid:
        print(f"\n  SID: {sid[:10]}...")
    if number:
        print(f"  Number: {number}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Verificar dependencias
print("\n📦 DEPENDENCIAS:")
packages = {
    'twilio': 'Twilio SDK',
    'flask': 'Flask Web Framework',
    'pyngrok': 'Ngrok Tunnel',
    'requests': 'HTTP Requests'
}

for package, name in packages.items():
    try:
        mod = __import__(package)
        version = getattr(mod, '__version__', 'instalado')
        print(f"✅ {name}: {version}")
    except ImportError:
        print(f"❌ {name}: no instalado")

# 4. Verificar handlers
print("\n🔧 HANDLERS:")
try:
    from app.whatsapp_handler import whatsapp_handler
    print("✅ WhatsApp Handler importado")
    
    # Ver métodos disponibles
    methods = [m for m in dir(whatsapp_handler) if not m.startswith('_')]
    print(f"   Métodos: {', '.join(methods[:5])}...")
except Exception as e:
    print(f"❌ WhatsApp Handler: {e}")

# 5. Verificar Firebase
print("\n🔥 FIREBASE:")
try:
    from app.firebase_handler import firebase_handler
    print("✅ Firebase Handler disponible")
    
    # Probar conexión
    empresas = firebase_handler.get_empresas()
    print(f"✅ Conexión OK - {len(empresas)} empresas cargadas")
except Exception as e:
    print(f"❌ Firebase: {e}")

# 6. Verificar OCR
print("\n🔍 OCR:")
try:
    from app.ocr_processor import ocr_processor
    if ocr_processor.client:
        print("✅ Google Cloud Vision inicializado")
    else:
        print("⚠️  OCR client no inicializado")
except Exception as e:
    print(f"❌ OCR: {e}")

# 7. Verificar ngrok
print("\n🌐 NGROK:")
ngrok_exe = Path('ngrok.exe')
if ngrok_exe.exists():
    print(f"✅ ngrok.exe encontrado: {ngrok_exe.absolute()}")
else:
    print("❌ ngrok.exe no encontrado")

# 8. Ver últimas facturas OCR
print("\n📄 ÚLTIMAS FACTURAS OCR:")
try:
    from app.firebase_handler import firebase_handler
    facturas = firebase_handler.get_ocr_facturas_by_empresa('comp_1', None)
    
    print(f"Total: {len(facturas)} facturas")
    
    # Mostrar las 3 más recientes
    facturas_sorted = sorted(
        facturas, 
        key=lambda x: x.get('processed_at', ''), 
        reverse=True
    )[:3]
    
    for i, f in enumerate(facturas_sorted, 1):
        ncf = f.get('ncf', 'Sin NCF')
        estado = f.get('estado', 'desconocido')
        manual = f.get('_manual_import', False)
        origen = '📥 Manual' if manual else '📱 WhatsApp'
        print(f"  {i}. {origen} - NCF: {ncf} - Estado: {estado}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)