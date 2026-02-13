"""
Script para analizar estructura completa del proyecto LECTOR-NCF
"""
import os
import json
from pathlib import Path
from typing import Dict, List

# Colores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def format_size(bytes_size: int) -> str:
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def print_tree(directory: Path, prefix: str = "", is_last: bool = True, max_depth: int = 5, current_depth: int = 0):
    """Print directory tree"""
    if current_depth >= max_depth:
        return
    
    # Skip certain directories
    skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.vscode', 'dist', 'build', '.pytest_cache'}
    
    try:
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return
    
    # Filter out skipped directories
    items = [item for item in items if item.name not in skip_dirs]
    
    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        
        # Tree characters
        branch = "└── " if is_last_item else "├── "
        extension = "    " if is_last_item else "│   "
        
        # Format name with size for files
        if item.is_file():
            try:
                size = format_size(item.stat().st_size)
                name = f"{Colors.WHITE}{item.name}{Colors.GRAY} ({size}){Colors.RESET}"
            except:
                name = f"{Colors.WHITE}{item.name}{Colors.RESET}"
        else:
            name = f"{Colors.YELLOW}{item.name}/{Colors.RESET}"
        
        print(f"{prefix}{branch}{name}")
        
        # Recurse into directories
        if item.is_dir():
            new_prefix = prefix + extension
            print_tree(item, new_prefix, is_last_item, max_depth, current_depth + 1)

def find_credentials(root_path: Path) -> List[Dict]:
    """Find credential files"""
    credentials = []
    
    for json_file in root_path.rglob("*.json"):
        # Skip venv and large files
        if 'venv' in str(json_file) or 'node_modules' in str(json_file):
            continue
        
        try:
            file_size = json_file.stat().st_size
            
            # Skip very large or very small files
            if file_size < 100 or file_size > 50 * 1024:
                continue
            
            with open(json_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Check if it's a Google Cloud credential
            if isinstance(content, dict) and ('private_key' in content or content.get('type') == 'service_account'):
                credentials.append({
                    'path': str(json_file),
                    'type': content.get('type', 'unknown'),
                    'email': content.get('client_email', 'N/A'),
                    'project_id': content.get('project_id', 'N/A'),
                    'size': format_size(file_size)
                })
        except:
            continue
    
    return credentials

def find_config_files(root_path: Path) -> List[Path]:
    """Find configuration files"""
    config_patterns = ['*.env*', 'config.json', 'settings.json', 'credentials.json', '.env']
    config_files = []
    
    for pattern in config_patterns:
        for file in root_path.rglob(pattern):
            if 'venv' not in str(file) and 'node_modules' not in str(file):
                config_files.append(file)
    
    return config_files

def find_google_cloud_files(root_path: Path) -> List[Path]:
    """Find Python files using Google Cloud"""
    python_files = []
    
    for py_file in root_path.rglob("*.py"):
        if 'venv' in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(keyword in content for keyword in ['google.cloud', 'vision', 'GOOGLE_APPLICATION_CREDENTIALS']):
                    python_files.append(py_file)
        except:
            continue
    
    return python_files

def main():
    """Main function"""
    root = Path(r"D:\Dropbox\GITHUB\LECTOR-NCF")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
    print(f"ANÁLISIS COMPLETO DE ESTRUCTURA - LECTOR-NCF")
    print(f"{'='*80}{Colors.RESET}\n")
    
    # 1. ESTRUCTURA COMPLETA
    print(f"{Colors.CYAN}{Colors.BOLD}📂 ESTRUCTURA DE DIRECTORIOS:{Colors.RESET}\n")
    print_tree(root, max_depth=4)
    
    # 2. CREDENCIALES
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*80}")
    print(f"🔑 ARCHIVOS DE CREDENCIALES ENCONTRADOS:")
    print(f"{'='*80}{Colors.RESET}\n")
    
    credentials = find_credentials(root)
    if credentials:
        for cred in credentials:
            print(f"{Colors.GREEN}✓ CREDENCIAL ENCONTRADA:{Colors.RESET}")
            print(f"  {Colors.CYAN}Archivo:{Colors.RESET} {cred['path']}")
            print(f"  {Colors.YELLOW}Tipo:{Colors.RESET} {cred['type']}")
            print(f"  {Colors.YELLOW}Email:{Colors.RESET} {cred['email']}")
            print(f"  {Colors.YELLOW}Project:{Colors.RESET} {cred['project_id']}")
            print(f"  {Colors.GRAY}Tamaño:{Colors.RESET} {cred['size']}\n")
    else:
        print(f"{Colors.RED}✗ No se encontraron archivos de credenciales de Google Cloud{Colors.RESET}\n")
    
    # 3. ARCHIVOS DE CONFIGURACIÓN
    print(f"{Colors.MAGENTA}{Colors.BOLD}{'='*80}")
    print(f"⚙️  ARCHIVOS DE CONFIGURACIÓN:")
    print(f"{'='*80}{Colors.RESET}\n")
    
    config_files = find_config_files(root)
    if config_files:
        for config in config_files:
            print(f"{Colors.WHITE}📄 {config}{Colors.RESET}")
            
            # Show content preview for small files
            if config.suffix == '.json':
                try:
                    with open(config, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:5]
                        print(f"   {Colors.GRAY}Primeras líneas:{Colors.RESET}")
                        for line in lines:
                            print(f"   {Colors.GRAY}{line.rstrip()}{Colors.RESET}")
                except:
                    pass
            print()
    else:
        print(f"{Colors.RED}✗ No se encontraron archivos de configuración{Colors.RESET}\n")
    
    # 4. ARCHIVOS PYTHON CON GOOGLE CLOUD
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}")
    print(f"🐍 ARCHIVOS PYTHON QUE USAN GOOGLE CLOUD:")
    print(f"{'='*80}{Colors.RESET}\n")
    
    py_files = find_google_cloud_files(root)
    if py_files:
        for py_file in py_files:
            rel_path = py_file.relative_to(root)
            print(f"{Colors.CYAN}  • {rel_path}{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ No se encontraron archivos Python usando Google Cloud{Colors.RESET}\n")
    
    # 5. VARIABLES DE ENTORNO
    print(f"\n{Colors.YELLOW}{Colors.BOLD}{'='*80}")
    print(f"🔐 VARIABLES DE ENTORNO:")
    print(f"{'='*80}{Colors.RESET}\n")
    
    google_creds_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if google_creds_env:
        print(f"{Colors.GREEN}✓ GOOGLE_APPLICATION_CREDENTIALS:{Colors.RESET} {google_creds_env}")
        if Path(google_creds_env).exists():
            print(f"  {Colors.GREEN}✓ El archivo existe{Colors.RESET}")
        else:
            print(f"  {Colors.RED}✗ El archivo NO existe{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Variable GOOGLE_APPLICATION_CREDENTIALS no configurada{Colors.RESET}")
    
    # 6. RESUMEN
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
    print(f"📊 RESUMEN:")
    print(f"{'='*80}{Colors.RESET}\n")
    
    print(f"  {Colors.WHITE}Credenciales encontradas:{Colors.RESET} {Colors.GREEN if credentials else Colors.RED}{len(credentials)}{Colors.RESET}")
    print(f"  {Colors.WHITE}Archivos de configuración:{Colors.RESET} {Colors.GREEN if config_files else Colors.RED}{len(config_files)}{Colors.RESET}")
    print(f"  {Colors.WHITE}Archivos Python con Google Cloud:{Colors.RESET} {Colors.GREEN if py_files else Colors.RED}{len(py_files)}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}")
    print(f"FIN DEL ANÁLISIS")
    print(f"{'='*80}{Colors.RESET}\n")

if __name__ == "__main__":
    main()