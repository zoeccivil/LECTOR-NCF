# LECTOR-NCF GUI - Quick Start Guide

## Installation

### 1. Install Python dependencies

```bash
# Install main application dependencies
pip install -r requirements.txt

# Install GUI dependencies
pip install -r gui/requirements_gui.txt
```

### 2. System requirements (Linux)

For Linux systems, you may need to install additional system libraries:

```bash
sudo apt-get install libegl1 libgl1 libxkbcommon0 libdbus-1-3
```

### 3. Configure Firebase

Create a `.env` file in the root directory with your Firebase credentials:

```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

## Running the GUI

```bash
cd /path/to/LECTOR-NCF
python gui/main.py
```

## Features

### Dashboard Screen
- **Empresa Sidebar**: Browse and select companies
- **Factura Table**: View all invoices with status badges
  - 🟡 Pendiente (Pending)
  - 🟢 Revisada (Reviewed)  
  - ⚪ Exportada (Exported)
- **Filters**: View all, pending, or reviewed invoices
- **Search**: Find invoices by NCF number
- **Actions**: Edit or delete invoices directly from table

### Editor Screen
- **Image Viewer** (left panel):
  - Zoom in/out with mouse wheel or buttons
  - Rotate image 90 degrees
  - Pan when zoomed
  - Reset view
- **Form Editor** (right panel):
  - Edit NCF, RNC, Razón Social
  - Date picker for Fecha de Emisión
  - Amount fields with auto-calculation
  - OCR confidence indicators (🟢🟡🔴)
- **Navigation**: Move between invoices with arrow buttons
- **Keyboard Shortcuts**:
  - `Ctrl+S` - Save changes
  - `Ctrl+Enter` - Mark as reviewed
  - `Ctrl+←` - Previous invoice
  - `Ctrl+→` - Next invoice

### Exporter Screen
- **Step 1**: Select company
- **Step 2**: Select invoices to export (with search)
- **Step 3**: Choose format (CSV/JSON/Both)
- **Step 4**: Review and export
- **Option**: Mark as exported after export

## Architecture

```
gui/
├── main.py                    # Entry point
├── app.py                     # MainWindow with navigation
├── screens/                   # Main screens
│   ├── dashboard.py          # Invoice list & management
│   ├── editor.py             # Invoice editor with image
│   └── exporter.py           # Export wizard
├── widgets/                   # Reusable components
│   ├── empresa_list.py       # Company sidebar
│   ├── factura_table.py      # Invoice table
│   ├── image_viewer.py       # Image viewer with zoom
│   └── form_field.py         # Form field with confidence
└── utils/                     # Utilities
    ├── styles.py             # QSS stylesheet
    └── async_helper.py       # QThread workers
```

## Design Specifications

### Color Palette
- Primary Blue: `#1976D2`
- Success Green: `#4CAF50`
- Warning Orange: `#FF9800`
- Error Red: `#F44336`
- Pending Yellow: `#FFC107`
- Text Primary: `#212121`
- Background: `#F8F9FA`

### Typography
- Font: Segoe UI, Roboto, sans-serif
- Title: 24px bold
- Body: 14px
- Caption: 12px

## Troubleshooting

### ImportError: libEGL.so.1
Install required system libraries:
```bash
sudo apt-get install libegl1 libgl1
```

### Firebase not initialized
Make sure your `.env` file is configured with valid Firebase credentials.

### Image not loading
- Check that `imagen_original` field contains a valid URL or file path
- Ensure you have internet connection for remote images
- For local images, use absolute paths

## Development

### Adding new features
1. Create new widgets in `gui/widgets/`
2. Add screens in `gui/screens/`
3. Use `FirebaseWorkerPool` for async operations
4. Follow existing styling patterns

### Testing
```bash
# Test imports and initialization
python -c "from gui.app import LectorNCFApp; print('OK')"

# Run with offscreen platform (headless)
QT_QPA_PLATFORM=offscreen python gui/main.py
```

## License

See main project LICENSE file.
