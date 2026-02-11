# LECTOR-NCF GUI

Aplicación desktop PyQt6 para gestión de facturas NCF procesadas por OCR.

## Instalación

```bash
pip install -r gui/requirements_gui.txt
```

## Uso

```bash
python gui/main.py
```

## Configuración

Asegúrate de tener configurado:
- Firebase credentials en `.env`
- Variable `GOOGLE_APPLICATION_CREDENTIALS`
- Variable `FIREBASE_DATABASE_URL`

## Shortcuts de Teclado

### Editor de Facturas
- `Ctrl+S` - Guardar cambios
- `Ctrl+Enter` - Marcar como revisada
- `Ctrl+←` - Factura anterior
- `Ctrl+→` - Factura siguiente
- `Ctrl+Q` - Salir de la aplicación

## Estructura

```
gui/
├── main.py              # Entry point (QApplication)
├── app.py               # MainWindow con QStackedWidget
├── screens/             # Pantallas principales
│   ├── dashboard.py     # Lista de facturas
│   ├── editor.py        # Editor con imagen + formulario
│   └── exporter.py      # Exportador wizard
├── widgets/             # Componentes reutilizables
│   ├── empresa_list.py  # Sidebar de empresas
│   ├── factura_table.py # Tabla de facturas
│   ├── image_viewer.py  # Visor con zoom
│   └── form_field.py    # Input + indicador confianza OCR
└── utils/               # Helpers y estilos
    ├── styles.py        # QSS global stylesheet
    └── async_helper.py  # QThread para llamadas Firebase
```

## Características

- ✅ Conexión a Firebase Firestore
- ✅ Vista de empresas y facturas
- ✅ Editor visual con imagen y formulario
- ✅ Indicadores de confianza OCR
- ✅ Filtros por estado (Pendientes/Revisadas/Exportadas)
- ✅ Exportación a CSV/JSON
- ✅ Operaciones asíncronas (sin freeze de UI)
- ✅ Shortcuts de teclado
- ✅ Validación de datos
