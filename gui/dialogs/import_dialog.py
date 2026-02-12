"""
Import Invoice Dialog - Manual OCR upload
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QComboBox, QMessageBox,
                             QLineEdit, QFrame, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from pathlib import Path
import shutil
from datetime import datetime

from app.ocr_processor import ocr_processor
from app.firebase_handler import firebase_handler
from app.utils.logger import app_logger


class ImportInvoiceDialog(QDialog):
    """Dialog for manual invoice import with OCR"""
    
    invoice_imported = pyqtSignal()
    
    def __init__(self, empresas: list, parent=None):
        super().__init__(parent)
        self.empresas = empresas
        self.image_path = None
        self.ocr_data = None
        
        self.setWindowTitle("Importar Factura con OCR")
        self.setMinimumSize(700, 600)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Title
        title = QLabel("Importar Factura Manualmente")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        """)
        layout.addWidget(title)
        
        # Step 1: Select empresa
        step1 = QLabel("1. Seleccionar Empresa")
        step1.setStyleSheet("font-size: 16px; font-weight: 600; color: #111827;")
        layout.addWidget(step1)
        
        self.empresa_combo = QComboBox()
        self.empresa_combo.setMinimumHeight(44)
        self.empresa_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px 14px;
                background-color: #FFFFFF;
                font-size: 14px;
                color: #111827;
            }
            QComboBox:hover {
                border-color: #9CA3AF;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                selection-background-color: #EFF6FF;
                selection-color: #2563EB;
                color: #111827;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 6px 12px;
            }
        """)
        for emp in self.empresas:
            self.empresa_combo.addItem(emp['nombre'], emp['id'])
        layout.addWidget(self.empresa_combo)
        
        # Step 2: Upload image
        step2 = QLabel("2. Subir Imagen de Factura")
        step2.setStyleSheet("font-size: 16px; font-weight: 600; color: #111827;")
        layout.addWidget(step2)
        
        upload_btn = QPushButton("📤 Seleccionar Imagen...")
        upload_btn.setMinimumHeight(50)
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        upload_btn.clicked.connect(self._select_image)
        layout.addWidget(upload_btn)
        
        # Image preview
        self.image_label = QLabel("No se ha seleccionado ninguna imagen")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(150)
        self.image_label.setStyleSheet("""
            border: 2px dashed #D1D5DB;
            border-radius: 8px;
            background-color: #F9FAFB;
            color: #6B7280;
            font-size: 14px;
        """)
        layout.addWidget(self.image_label)
        
        # Step 3: Process OCR
        step3 = QLabel("3. Procesar con OCR")
        step3.setStyleSheet("font-size: 16px; font-weight: 600; color: #111827;")
        layout.addWidget(step3)
        
        self.btn_process = QPushButton("🔍 Procesar OCR")
        self.btn_process.setEnabled(False)
        self.btn_process.setMinimumHeight(50)
        self.btn_process.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
            }
        """)
        self.btn_process.clicked.connect(self._process_ocr)
        layout.addWidget(self.btn_process)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                text-align: center;
                height: 24px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
            }
        """)
        layout.addWidget(self.progress)
        
        # OCR results
        self.results_label = QLabel("")
        self.results_label.setStyleSheet("""
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 8px;
            padding: 16px;
            color: #1E40AF;
            font-size: 13px;
        """)
        self.results_label.setWordWrap(True)
        self.results_label.setVisible(False)
        layout.addWidget(self.results_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumWidth(120)
        btn_cancel.setMinimumHeight(44)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        self.btn_import = QPushButton("✓ Importar Factura")
        self.btn_import.setEnabled(False)
        self.btn_import.setMinimumWidth(160)
        self.btn_import.setMinimumHeight(44)
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
            }
        """)
        self.btn_import.clicked.connect(self._import_invoice)
        btn_layout.addWidget(self.btn_import)
        
        layout.addLayout(btn_layout)
    
    def _select_image(self):
        """Select image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen de Factura",
            "",
            "Images (*.png *.jpg *.jpeg *.pdf);;All Files (*)"
        )
        
        if file_path:
            self.image_path = file_path
            
            # Show preview
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(400, 150, Qt.AspectRatioMode.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText(f"Archivo seleccionado:\n{Path(file_path).name}")
            
            self.btn_process.setEnabled(True)
    
    def _process_ocr(self):
        """Process image with OCR"""
        if not self.image_path:
            return
        
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)  # Indeterminate
            self.btn_process.setEnabled(False)
            
            # Read image file
            with open(self.image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Process with OCR
            self.ocr_data = ocr_processor.extract_invoice_data(image_bytes)
            
            # Show results
            fecha = self.ocr_data.get('fecha_emision')
            if isinstance(fecha, datetime):
                fecha_str = fecha.strftime('%Y-%m-%d')
            else:
                fecha_str = str(fecha) if fecha else 'No detectado'
            
            results_text = f"""
✓ OCR Procesado Exitosamente

NCF: {self.ocr_data.get('ncf') or 'No detectado'}
RNC: {self.ocr_data.get('rnc') or 'No detectado'}
Razón Social: {self.ocr_data.get('razon_social') or 'No detectado'}
Fecha: {fecha_str}
Subtotal: DOP {self.ocr_data.get('subtotal', 0):,.2f}
ITBIS: DOP {self.ocr_data.get('itbis', 0):,.2f}
Total: DOP {self.ocr_data.get('total', 0):,.2f}

Confianza OCR: {self.ocr_data.get('confianza_ocr', 0)*100:.1f}%
            """.strip()
            
            self.results_label.setText(results_text)
            self.results_label.setVisible(True)
            
            self.btn_import.setEnabled(True)
            
        except Exception as e:
            app_logger.error(f"OCR processing error: {e}")
            QMessageBox.critical(
                self,
                "Error OCR",
                f"Error procesando imagen con OCR:\n{str(e)}\n\nVerifica que:\n"
                "1. La imagen sea legible\n"
                "2. Las credenciales de Google Cloud estén configuradas\n"
                "3. La API de Vision esté habilitada"
            )
        finally:
            self.progress.setVisible(False)
            self.btn_process.setEnabled(True)
    
    def _import_invoice(self):
        """Import invoice to database"""
        if not self.ocr_data:
            return
        
        try:
            empresa_id = self.empresa_combo.currentData()
            
            # Prepare invoice data
            invoice = {
                'company_id': int(empresa_id.replace('comp_', '')),
                'ncf': self.ocr_data.get('ncf') or '',
                'rnc': self.ocr_data.get('rnc') or '',
                'razon_social': self.ocr_data.get('razon_social') or '',
                'fecha_emision': self.ocr_data.get('fecha_emision') or datetime.now(),
                'subtotal': float(self.ocr_data.get('subtotal') or 0),
                'itbis': float(self.ocr_data.get('itbis') or 0),
                'total': float(self.ocr_data.get('total') or 0),
                'imagen_original': self.image_path,
                'whatsapp_message_id': f'manual_{datetime.now().timestamp()}',
                'processed_at': datetime.now(),
                'confianza_ocr': float(self.ocr_data.get('confianza_ocr') or 0.85),
                'revisada': False,
                'exportada': False,
                'estado': 'pendiente',
                '_manual_import': True,
                '_texto_ocr': self.ocr_data.get('texto_completo', '')
            }
            
            # Save to Firebase
            doc_id = firebase_handler.save_ocr_invoice(invoice, empresa_id, invoice['whatsapp_message_id'])
            
            app_logger.info(f"Invoice imported manually: {doc_id}")
            
            QMessageBox.information(
                self,
                "Éxito",
                f"✓ Factura importada correctamente\n\n"
                f"NCF: {invoice['ncf']}\n"
                f"Total: DOP {invoice['total']:,.2f}\n\n"
                f"Revisa la factura en la pestaña 'Pendientes'"
            )
            
            self.invoice_imported.emit()
            self.accept()
            
        except Exception as e:
            app_logger.error(f"Import error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error importando factura:\n{str(e)}"
            )