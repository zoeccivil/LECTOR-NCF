#!/usr/bin/env python3
"""
Quick test script to verify the redesigned UI loads properly
This can be run without a full Firebase setup to test the UI components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")
    
    try:
        from gui.utils.theme import COLORS, FONTS, SPACING, RADIUS, SHADOWS
        print("✓ Theme module imports successfully")
    except Exception as e:
        print(f"✗ Theme module import failed: {e}")
        return False
    
    try:
        from gui.utils.icon_helper import IconHelper
        print("✓ Icon helper module imports successfully")
    except Exception as e:
        print(f"✗ Icon helper module import failed: {e}")
        return False
    
    try:
        from gui.utils.animations import AnimationHelper
        print("✓ Animations module imports successfully")
    except Exception as e:
        print(f"✗ Animations module import failed: {e}")
        return False
    
    try:
        from gui.widgets.components import (
            StatusBadge, IconButton, SearchBox, StatsCard, EmptyState
        )
        print("✓ Components module imports successfully")
    except Exception as e:
        print(f"✗ Components module import failed: {e}")
        return False
    
    try:
        from gui.utils.styles import GLOBAL_STYLES
        print("✓ Styles module imports successfully")
    except Exception as e:
        print(f"✗ Styles module import failed: {e}")
        return False
    
    return True

def test_firebase_handler():
    """Test that Firebase handler has new OCR methods"""
    print("\nTesting Firebase handler...")
    
    try:
        from app.firebase_handler import FirebaseHandler
        handler = FirebaseHandler()
        
        # Check for new OCR methods
        required_methods = [
            'save_ocr_invoice',
            'get_ocr_facturas_by_empresa',
            'get_ocr_factura',
            'update_ocr_factura',
            'mark_ocr_factura_revisada',
            'mark_ocr_factura_exportada',
            'delete_ocr_factura',
            'get_ocr_facturas_count_by_empresa'
        ]
        
        for method in required_methods:
            if hasattr(handler, method):
                print(f"✓ FirebaseHandler.{method} exists")
            else:
                print(f"✗ FirebaseHandler.{method} is missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Firebase handler test failed: {e}")
        return False

def test_icon_files():
    """Test that all required SVG icons exist"""
    print("\nTesting icon files...")
    
    from pathlib import Path
    icons_dir = Path(__file__).parent.parent / 'gui' / 'assets' / 'icons'
    
    required_icons = [
        'dashboard', 'invoice', 'company', 'search', 'filter',
        'export', 'edit', 'delete', 'check', 'close',
        'settings', 'refresh', 'upload', 'download', 'calendar',
        'money', 'user', 'whatsapp', 'ocr', 'pending',
        'reviewed', 'exported', 'arrow-left', 'arrow-right', 'chevron-down',
        'info', 'warning', 'error', 'zoom-in', 'zoom-out'
    ]
    
    missing_icons = []
    for icon in required_icons:
        icon_path = icons_dir / f'{icon}.svg'
        if icon_path.exists():
            print(f"✓ Icon {icon}.svg exists")
        else:
            print(f"✗ Icon {icon}.svg is missing")
            missing_icons.append(icon)
    
    return len(missing_icons) == 0

def main():
    """Run all tests"""
    print("=" * 60)
    print("LECTOR-NCF GUI Redesign - Component Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Firebase Handler", test_firebase_handler()))
    results.append(("Icon Files", test_icon_files()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! UI components are ready.")
        return 0
    else:
        print("✗ Some tests failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
