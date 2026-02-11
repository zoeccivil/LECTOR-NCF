# LECTOR-NCF

Sistema de Lectura OCR de Facturas NCF desde WhatsApp para República Dominicana.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Descripción

**LECTOR-NCF** es una aplicación Python completa que recibe fotos de facturas desde WhatsApp, procesa las imágenes con Google Cloud Vision OCR, extrae información de facturas NCF (Número de Comprobante Fiscal) de República Dominicana, y exporta los datos en formato CSV/JSON para integración con sistemas existentes.

### Características Principales

✅ **Recepción WhatsApp**: Webhook FastAPI integrado con Twilio  
✅ **OCR de Alta Precisión**: Google Cloud Vision API  
✅ **Extracción Inteligente**: Parser especializado para facturas dominicanas  
✅ **Validación**: NCF, RNC y coherencia matemática  
✅ **Exportación**: CSV y JSON con estructura optimizada  
✅ **Respuestas Automáticas**: Confirmaciones y resultados por WhatsApp  
✅ **Docker Ready**: Contenedorización completa  
✅ **Documentación Completa**: Guías de configuración paso a paso  

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11 o superior
- Cuenta de Google Cloud con Vision API habilitada
- Cuenta de Twilio con WhatsApp Business API
- Docker (opcional, para deployment)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/zoeccivil/LECTOR-NCF.git
cd LECTOR-NCF
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Ejecutar la aplicación**
```bash
python -m app.main
# O con uvicorn:
uvicorn app.main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`

## 📊 Datos Extraídos

El sistema extrae los siguientes campos de facturas dominicanas:

- **NCF** (Número de Comprobante Fiscal): B01, B02, B14, B15, etc.
- **RNC** (Registro Nacional del Contribuyente): 9-11 dígitos
- **Razón Social/Proveedor**: Nombre de la empresa
- **Fecha de Emisión**: Fecha de la factura
- **Subtotal**: Monto antes de impuestos
- **ITBIS**: Impuesto (18%)
- **Total**: Monto total

## 📱 Uso con WhatsApp

1. Configurar webhook en Twilio apuntando a `https://tu-dominio.com/webhook/whatsapp`
2. Enviar foto de factura al número WhatsApp configurado
3. Recibir confirmación automática
4. Sistema procesa y responde con resultados

### Respuestas Automáticas

- ✅ **Confirmación**: "Factura recibida, procesando..."
- ✅ **Éxito**: "Factura NCF: B0100000123 - Monto: RD$1,500.00 - Procesada correctamente"
- ❌ **Error**: "No se pudo leer la factura. Por favor, envía una foto más clara."

## 📁 Estructura del Proyecto

```
LECTOR-NCF/
├── app/
│   ├── main.py                 # Servidor FastAPI con webhook
│   ├── ocr_processor.py        # Google Cloud Vision OCR
│   ├── ncf_parser.py           # Extractor de datos NCF
│   ├── whatsapp_handler.py     # Manejo de mensajes Twilio
│   ├── export_handler.py       # Exportación CSV/JSON
│   ├── models.py               # Modelos Pydantic
│   └── utils/
│       ├── validators.py       # Validación NCF/RNC
│       ├── image_processor.py  # Optimización de imágenes
│       ├── config.py           # Configuración
│       └── logger.py           # Sistema de logs
├── data/
│   ├── exports/               # Archivos CSV/JSON generados
│   ├── temp/                  # Imágenes temporales
│   └── processed/             # Histórico de facturas
├── tests/
│   ├── test_validators.py
│   ├── test_ncf_parser.py
│   └── test_ocr.py
├── docs/
│   ├── SETUP.md
│   ├── GOOGLE_CLOUD.md
│   ├── TWILIO_WHATSAPP.md
│   └── FIREBASE.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuración

Ver archivos de documentación detallada:

- [SETUP.md](docs/SETUP.md) - Guía de instalación completa
- [GOOGLE_CLOUD.md](docs/GOOGLE_CLOUD.md) - Configuración de Google Cloud Vision
- [TWILIO_WHATSAPP.md](docs/TWILIO_WHATSAPP.md) - Configuración de Twilio WhatsApp
- [FIREBASE.md](docs/FIREBASE.md) - Integración con Firebase (opcional)

## 🐳 Docker

### Construcción
```bash
docker build -t lector-ncf .
```

### Ejecución
```bash
docker-compose up -d
```

## 🧪 Pruebas

Ejecutar tests:
```bash
pytest tests/ -v
```

Ejecutar con cobertura:
```bash
pytest tests/ --cov=app --cov-report=html
```

## 📤 Formatos de Exportación

### CSV
```csv
fecha_procesamiento,ncf,rnc,razon_social,fecha_emision,subtotal,itbis,total,imagen_original
2026-02-11 10:30:00,B0100000123,123456789,EMPRESA EJEMPLO SRL,2026-02-10,1271.19,228.81,1500.00,factura_20260211_103000.jpg
```

### JSON
```json
{
  "facturas": [
    {
      "id": "uuid-generated",
      "fecha_procesamiento": "2026-02-11T10:30:00Z",
      "ncf": "B0100000123",
      "rnc": "123456789",
      "razon_social": "EMPRESA EJEMPLO SRL",
      "montos": {
        "subtotal": 1271.19,
        "itbis": 228.81,
        "total": 1500.00
      }
    }
  ]
}
```

## 🔒 Seguridad

- ✅ Validación de formatos NCF y RNC según DGII
- ✅ Validación de coherencia matemática
- ✅ Detección de duplicados por NCF
- ✅ Limpieza automática de imágenes temporales
- ✅ Variables de entorno para credenciales sensibles

## 📈 Rendimiento

- **OCR**: >90% de precisión en facturas claras
- **Procesamiento**: ~3-5 segundos por factura
- **Formatos soportados**: JPG, PNG, HEIC

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Autores

- **LECTOR-NCF Team** - *Desarrollo inicial*

## 🙏 Agradecimientos

- Google Cloud Vision API
- Twilio WhatsApp Business API
- FastAPI Framework
- Comunidad Python RD

## 📞 Soporte

Para soporte, por favor abrir un issue en GitHub o contactar al equipo de desarrollo.

## 🗺️ Roadmap

- [ ] Integración directa con Firebase
- [ ] Dashboard web para visualización
- [ ] Machine Learning para mejorar extracción
- [ ] Soporte multi-idioma
- [ ] Procesamiento por lotes
- [ ] API REST completa para consultas

---

**Made with ❤️ in República Dominicana 🇩🇴**
