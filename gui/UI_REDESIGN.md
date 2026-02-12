# LECTOR-NCF GUI Redesign - Implementation Guide

## Overview

This document describes the complete UI/UX redesign of the LECTOR-NCF GUI application, focusing on:

1. **Data Separation**: New `/ocr_invoices/` Firebase collection for WhatsApp OCR invoices
2. **Modern UI**: Minimalist design with custom SVG icons and consistent styling
3. **Component Library**: Reusable components with hover effects and animations

## 🎨 Design System

### Color Palette

```python
PRIMARY = '#2563EB'      # Modern blue
PRIMARY_DARK = '#1E40AF'
PRIMARY_LIGHT = '#DBEAFE'
SUCCESS = '#10B981'      # Emerald green
WARNING = '#F59E0B'      # Amber
ERROR = '#EF4444'        # Soft red
PENDING = '#F59E0B'      # Amber
GRAY_50 = '#F9FAFB'
GRAY_100 = '#F3F4F6'
GRAY_200 = '#E5E7EB'
GRAY_300 = '#D1D5DB'
GRAY_700 = '#374151'
GRAY_900 = '#111827'
WHITE = '#FFFFFF'
```

### Typography

- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI"
- **Sizes**: 11px (caption), 13px (body), 15px (subtitle), 20px (title), 28px (heading)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Spacing

- **XS**: 4px
- **SM**: 8px
- **MD**: 12px
- **LG**: 16px
- **XL**: 24px
- **XXL**: 32px

### Border Radius

- **SMALL**: 6px
- **MEDIUM**: 8px
- **LARGE**: 12px

### Shadows

- **Small**: `0 1px 3px rgba(0,0,0,0.1)`
- **Medium**: `0 4px 6px rgba(0,0,0,0.1)`
- **Large**: `0 10px 15px rgba(0,0,0,0.1)`

## 📁 New File Structure

```
gui/
├── assets/
│   └── icons/              # 30 custom SVG icons
│       ├── dashboard.svg
│       ├── invoice.svg
│       ├── company.svg
│       └── ... (27 more)
├── utils/
│   ├── theme.py            # Design system constants
│   ├── icon_helper.py      # SVG icon loading utility
│   ├── animations.py       # Animation helpers
│   └── styles.py           # Updated QSS stylesheet
├── widgets/
│   ├── components.py       # Reusable UI components
│   ├── empresa_list.py     # Redesigned sidebar
│   ├── factura_table.py    # Redesigned table
│   └── ...
├── screens/
│   ├── dashboard.py        # Redesigned dashboard with tabs
│   └── ...
├── app.py                  # Updated main app
└── main.py                 # Updated entry point
```

## 🔧 Firebase Integration

### New OCR Invoices Collection

The redesign introduces a new `/ocr_invoices/` collection specifically for WhatsApp OCR invoices, separate from the existing `/invoices/` accounting system collection.

#### Collection Structure

```python
{
  'id': str (uuid),
  'company_id': int,
  'ncf': str,
  'rnc': str,
  'razon_social': str,
  'fecha_emision': datetime,
  'subtotal': float,
  'itbis': float,
  'total': float,
  'imagen_original': str (URL),
  'whatsapp_message_id': str,
  'processed_at': datetime,
  'confianza_ocr': float,
  'revisada': bool,
  'exportada': bool,
  'estado': 'pendiente' | 'revisada' | 'exportada',
  'reviewed_at': datetime (optional),
  'exported_at': datetime (optional)
}
```

#### New Firebase Methods

Added to `app/firebase_handler.py`:

- `save_ocr_invoice(invoice_data, empresa_id, whatsapp_msg_id)` - Save to `/ocr_invoices/`
- `get_ocr_facturas_by_empresa(empresa_id, estado=None)` - Get OCR invoices by company
- `get_ocr_factura(factura_id)` - Get single OCR invoice
- `update_ocr_factura(factura_id, updates)` - Update OCR invoice
- `mark_ocr_factura_revisada(factura_id)` - Mark as reviewed
- `mark_ocr_factura_exportada(factura_id)` - Mark as exported
- `delete_ocr_factura(factura_id)` - Delete OCR invoice
- `get_ocr_facturas_count_by_empresa(empresa_id)` - Get counts by status

## 🎁 Reusable Components

### StatusBadge

Pill-style status indicator with automatic styling:

```python
from gui.widgets.components import StatusBadge

badge = StatusBadge('pendiente')  # or 'revisada', 'exportada'
```

### IconButton

Button with SVG icon and hover effects:

```python
from gui.widgets.components import IconButton

btn = IconButton('edit', text='Editar', tooltip='Editar factura')
```

### SearchBox

Search input with icon and clear button:

```python
from gui.widgets.components import SearchBox

search = SearchBox(placeholder='Buscar...')
search.search_changed.connect(on_search)
```

### StatsCard

Statistics card with icon and value:

```python
from gui.widgets.components import StatsCard

card = StatsCard('invoice', '24', 'Facturas Pendientes')
```

### EmptyState

Empty state component for no data scenarios:

```python
from gui.widgets.components import EmptyState

empty = EmptyState(
    'invoice',
    'No hay facturas',
    'Aún no se han procesado facturas para esta empresa'
)
```

## 🚀 Running the Application

### Prerequisites

```bash
pip install -r gui/requirements_gui.txt
```

Key dependencies:
- PyQt6 >= 6.6.0
- PyQt6-SVG >= 6.6.0
- Pillow >= 10.0.0

### Launch

```bash
cd gui
python main.py
```

## 📱 UI Features

### Dashboard Screen

- **Sidebar**: Company list with circular badge counters showing pending invoices
- **Header**: Title, search box, refresh button, and export button
- **Tabs**: Filter invoices by status (Todas, Pendientes, Revisadas, Exportadas)
- **Table**: 
  - Row numbering column
  - Zebra striping for alternating rows
  - Hover effects with background highlight
  - Status badges with icons
  - Action buttons with SVG icons (edit, delete)

### Empresa List (Sidebar)

- Logo and app title at the top
- Company items with:
  - Company icon
  - Company name
  - Circular badge with pending count
- Hover state with left border highlight
- Selected state with blue background

### Factura Table

- Column headers with uppercase labels and letter spacing
- Row numbering for easy reference
- Alternating row colors (#FFFFFF / #F9FAFB)
- Hover effects with subtle elevation
- Status badges with appropriate colors
- Icon-only action buttons with tooltips

## 🎯 Key Changes from Original

1. **Data Source**: Now uses `/ocr_invoices/` collection instead of `/invoices/`
2. **Tab Navigation**: Replaced radio buttons with tab widget for status filtering
3. **Icon System**: All icons are now custom SVG files (no emoji or system icons)
4. **Color Scheme**: Updated to modern blue (#2563EB) from Material Blue (#1976D2)
5. **Typography**: Standardized on Inter font family
6. **Spacing**: Consistent spacing system throughout
7. **Components**: Modular, reusable components in `components.py`
8. **Animations**: Animation helpers for smooth transitions

## 🔒 Security & Data Integrity

- ✅ Does NOT modify `/companies/` or `/invoices/` collections
- ✅ Only works with new `/ocr_invoices/` collection
- ✅ Maintains compatibility with existing export system
- ✅ Uses Firebase security rules for data access

## 📚 Additional Resources

- Design inspiration: Linear, Notion, Stripe Dashboard
- Icon style: Outline icons with 2px stroke width
- Accessibility: WCAG AA contrast compliance

## 🐛 Testing

Run component tests:

```bash
python tests/test_ui_redesign.py
```

This will verify:
- All modules can be imported
- Firebase handler has new OCR methods
- All 30 SVG icons exist

## 📝 Notes

- The redesign maintains backward compatibility with existing screens (Editor, Exporter)
- Future enhancements can add empty states, loading states, and error states
- Animation system is in place but minimally used initially
- All styling is centralized in `theme.py` and `styles.py` for easy maintenance
