"""
Script de configuración de credenciales
Permite seleccionar archivos mediante dialog
"""
import os
import json
import shutil
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, simpledialog


def setup_credentials():
    """Configurar credenciales mediante file dialog"""
    
    print("=" * 70)
    print("🔧 CONFIGURACIÓN DE CREDENCIALES - LECTOR-NCF")
    print("=" * 70)
    
    # Crear directorio de credenciales
    creds_dir = Path("credentials")
    creds_dir.mkdir(exist_ok=True)
    
    # Inicializar Tkinter (ocultar ventana principal)
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # ==========================================
    # 1. FIREBASE CREDENTIALS
    # ==========================================
    print("\n📁 Selecciona el archivo de credenciales de FIREBASE...")
    print("   (firebase-credentials.json o similar)")
    
    firebase_file = filedialog.askopenfilename(
        title="Selecciona Firebase Credentials JSON",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )
    
    if firebase_file:
        # Copiar a credentials/
        dest_firebase = creds_dir / "firebase-credentials.json"
        shutil.copy2(firebase_file, dest_firebase)
        print(f"   ✅ Firebase credentials copiadas a: {dest_firebase}")
        
        # Verificar que sea válido
        try:
            with open(dest_firebase, 'r') as f:
                firebase_data = json.load(f)
            
            project_id = firebase_data.get("project_id", "N/A")
            print(f"   📋 Project ID: {project_id}")
        except Exception as e:
            print(f"   ⚠️ Advertencia: No se pudo validar el JSON: {e}")
    else:
        print("   ⏭️ Omitido")
    
    # ==========================================
    # 2. FIREBASE DATABASE URL
    # ==========================================
    if firebase_file:
        print("\n🔗 Ingresa la URL de Firebase Database:")
        print("   Ejemplo: https://tu-proyecto.firebaseio.com")
        
        database_url = simpledialog.askstring(
            "Firebase Database URL",
            "Ingresa la URL de Firebase Realtime Database:",
            initialvalue="https://facot-app-default-rtdb.firebaseio.com/"
        )
        
        if database_url:
            print(f"   ✅ Database URL: {database_url}")
        else:
            database_url = "https://facot-app-default-rtdb.firebaseio.com/"
            print(f"   ℹ️ Usando URL por defecto: {database_url}")
    else:
        database_url = None
    
    # ==========================================
    # 3. GOOGLE CLOUD VISION CREDENTIALS
    # ==========================================
    print("\n📁 Selecciona el archivo de credenciales de GOOGLE CLOUD VISION...")
    print("   (Si es el mismo que Firebase, selecciona el mismo archivo)")
    
    use_same = messagebox.askyesno(
        "Google Cloud Vision",
        "¿Usar las mismas credenciales de Firebase para Google Cloud Vision?"
    )
    
    if use_same and firebase_file:
        dest_vision = creds_dir / "google-vision-credentials.json"
        shutil.copy2(dest_firebase, dest_vision)
        print(f"   ✅ Usando mismas credenciales: {dest_vision}")
    else:
        vision_file = filedialog.askopenfilename(
            title="Selecciona Google Cloud Vision Credentials JSON",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if vision_file:
            dest_vision = creds_dir / "google-vision-credentials.json"
            shutil.copy2(vision_file, dest_vision)
            print(f"   ✅ Google Vision credentials copiadas a: {dest_vision}")
        else:
            print("   ⏭️ Omitido")
            dest_vision = None
    
    # ==========================================
    # 4. CREAR ARCHIVO .ENV
    # ==========================================
    print("\n📝 Creando archivo .env...")
    
    env_content = f"""# LECTOR-NCF Environment Variables
# Generado automáticamente por setup_credentials.py

# Firebase
FIREBASE_CREDENTIALS=credentials/firebase-credentials.json
FIREBASE_DATABASE_URL={database_url or 'https://facot-app-default-rtdb.firebaseio.com/'}

# Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=credentials/google-vision-credentials.json

# Twilio (opcional)
TWILIO_ACCOUNT_SID=ACcce41a5f483e545f2f24ed71cc93b64a
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Green-API (opcional)
GREENAPI_INSTANCE_ID=tu_instance_id_aqui
GREENAPI_TOKEN=tu_token_aqui

# WhatsApp Mode: dual, twilio, greenapi
WHATSAPP_MODE=dual

# Debug
DEBUG=False
"""
    
    env_path = Path(".env")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"   ✅ Archivo .env creado: {env_path}")
    
    # ==========================================
    # 5. RESUMEN
    # ==========================================
    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    
    if firebase_file:
        print(f"✅ Firebase:      credentials/firebase-credentials.json")
    else:
        print(f"⏭️ Firebase:      No configurado")
    
    if dest_vision and dest_vision.exists():
        print(f"✅ Google Vision: credentials/google-vision-credentials.json")
    else:
        print(f"⏭️ Google Vision: No configurado")
    
    print(f"✅ Variables:     .env")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("   1. Edita .env si necesitas agregar tokens de Twilio/Green-API")
    print("   2. Ejecuta: python -m app.main")
    print("   3. O ejecuta: uvicorn app.main:app --reload")
    print("=" * 70)
    
    root.destroy()


def verify_credentials():
    """Verificar que las credenciales existan"""
    
    print("\n🔍 Verificando credenciales...")
    
    files_to_check = [
        "credentials/firebase-credentials.json",
        "credentials/google-vision-credentials.json",
        ".env"
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - NO ENCONTRADO")
            all_exist = False
    
    if all_exist:
        print("\n✅ Todas las credenciales están configuradas")
        return True
    else:
        print("\n⚠️ Faltan algunas credenciales")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_credentials()
    else:
        print("\n🚀 Iniciando configurador de credenciales...")
        print("   Se abrirán ventanas de diálogo para seleccionar archivos.\n")
        
        try:
            setup_credentials()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nPresiona ENTER para salir...")