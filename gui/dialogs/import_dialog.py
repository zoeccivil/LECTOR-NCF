"""
Import Invoice Dialog - Manual OCR upload with improved UI
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QComboBox, QMessageBox,
                             QLineEdit, QFrame, QProgressBar, QFormLayout,
                             QDialogButtonBox, QWidget, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
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
        self.setMinimumSize(800, 750)
        
        # ✅ Stylesheet global más fuerte para forzar fondo blanco
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QWidget {
                background-color: transparent;
            }
            QLabel {
                background-color: transparent;
                color: #111827;
            }
            QScrollArea {
                background-color: #FFFFFF;
                border: none;
            }
            QFrame {
                background-color: transparent;
            }
        """)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        # Scroll area para contenido largo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF; }")
        
        # Widget contenedor
        container = QWidget()
        scroll.setWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # ✅ Header con icono y título
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("📥")
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)
        
        title = QLabel("Importar Factura Manualmente")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #E5E7EB; max-height: 1px;")
        layout.addWidget(line)
        
        # ✅ PASO 1: Seleccionar Empresa
        step1_container = self._create_step_container(
            "1",
            "Seleccionar Empresa",
            "Elige la empresa a la que pertenece esta factura"
        )
        layout.addWidget(step1_container)
        
        self.empresa_combo = QComboBox()
        self.empresa_combo.setMinimumHeight(48)
        self.empresa_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px 16px;
                background-color: #FFFFFF;
                font-size: 15px;
                color: #111827;
            }
            QComboBox:hover {
                border-color: #2563EB;
            }
            QComboBox:focus {
                border-color: #2563EB;
                background-color: #F0F9FF;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #6B7280;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                selection-background-color: #EFF6FF;
                selection-color: #1E40AF;
                color: #111827;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 40px;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F3F4F6;
            }
        """)
        for emp in self.empresas:
            self.empresa_combo.addItem(f"🏢 {emp['nombre']}", emp['id'])
        layout.addWidget(self.empresa_combo)
        
        layout.addSpacing(8)
        
        # ✅ PASO 2: Subir Imagen
        step2_container = self._create_step_container(
            "2",
            "Subir Imagen de Factura",
            "Selecciona una imagen JPG, PNG o PDF"
        )
        layout.addWidget(step2_container)
        
        upload_btn = QPushButton("📤  Seleccionar Imagen...")
        upload_btn.setMinimumHeight(52)
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        upload_btn.clicked.connect(self._select_image)
        layout.addWidget(upload_btn)
        
        # Image preview
        self.image_label = QLabel("No se ha seleccionado ninguna imagen")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(180)
        self.image_label.setStyleSheet("""
            border: 2px dashed #D1D5DB;
            border-radius: 12px;
            background-color: #F9FAFB;
            color: #9CA3AF;
            font-size: 14px;
            padding: 20px;
        """)
        layout.addWidget(self.image_label)
        
        layout.addSpacing(8)
        
        # ✅ PASO 3: Procesar OCR
        step3_container = self._create_step_container(
            "3",
            "Procesar con OCR",
            "Extrae automáticamente los datos de la factura"
        )
        layout.addWidget(step3_container)
        
        self.btn_process = QPushButton("🔍  Procesar OCR")
        self.btn_process.setEnabled(False)
        self.btn_process.setMinimumHeight(52)
        self.btn_process.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_process.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
                color: #9CA3AF;
            }
        """)
        self.btn_process.clicked.connect(self._process_ocr)
        layout.addWidget(self.btn_process)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(True)
        self.progress.setFormat("Procesando imagen con OCR...")
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                text-align: center;
                height: 32px;
                background-color: #F9FAFB;
                color: #374151;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress)
        
        # ✅ OCR results con mejor diseño
        self.results_container = QFrame()
        self.results_container.setVisible(False)
        self.results_container.setStyleSheet("""
            QFrame {
                background-color: #F0F9FF;
                border: 2px solid #3B82F6;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setSpacing(12)
        
        # Título de resultados
        results_title = QLabel("✓ OCR Procesado Exitosamente")
        results_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #059669;
            margin-bottom: 8px;
        """)
        results_layout.addWidget(results_title)
        
        # Label de resultados
        self.results_label = QLabel()
        self.results_label.setWordWrap(True)
        self.results_label.setTextFormat(Qt.TextFormat.RichText)
        self.results_label.setStyleSheet("""
            QLabel {
                color: #1F2937;
                font-size: 14px;
                line-height: 1.6;
                background-color: transparent;
                border: none;
                padding: 0;
            }
        """)
        results_layout.addWidget(self.results_label)
        
        layout.addWidget(self.results_container)
        
        # ✅ Botón editar
        self.btn_edit_ocr = QPushButton("✏️  Editar Datos OCR")
        self.btn_edit_ocr.setMinimumHeight(48)
        self.btn_edit_ocr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_ocr.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
            QPushButton:pressed {
                background-color: #B45309;
            }
        """)
        self.btn_edit_ocr.clicked.connect(self._edit_ocr_data)
        self.btn_edit_ocr.setVisible(False)
        layout.addWidget(self.btn_edit_ocr)
        
        layout.addStretch()
        
        # ✅ Footer con botones
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border-top: 1px solid #E5E7EB;
                padding: 0;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(32, 20, 32, 20)
        footer_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumWidth(140)
        btn_cancel.setMinimumHeight(48)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #374151;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F9FAFB;
                border-color: #D1D5DB;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(btn_cancel)
        
        self.btn_import = QPushButton("✓  Importar Factura")
        self.btn_import.setEnabled(False)
        self.btn_import.setMinimumWidth(180)
        self.btn_import.setMinimumHeight(48)
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #E5E7EB;
                color: #9CA3AF;
            }
        """)
        self.btn_import.clicked.connect(self._import_invoice)
        footer_layout.addWidget(self.btn_import)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(scroll)
        main_layout.addWidget(footer)
    
    def _create_step_container(self, step_number: str, title: str, description: str) -> QFrame:
        """Create a styled step container"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Step number badge
        badge = QLabel(step_number)
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("""
            QLabel {
                background-color: #2563EB;
                color: #FFFFFF;
                border-radius: 18px;
                font-size: 16px;
                font-weight: 700;
            }
        """)
        layout.addWidget(badge)
        
        # Title and description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #111827;
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 13px;
            color: #6B7280;
        """)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return container
    
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
                scaled_pixmap = pixmap.scaled(
                    500, 180, 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet("""
                    border: 2px solid #10B981;
                    border-radius: 12px;
                    background-color: #F9FAFB;
                    padding: 10px;
                """)
            else:
                filename = Path(file_path).name
                self.image_label.setText(f"📄 {filename}")
                self.image_label.setStyleSheet("""
                    border: 2px solid #10B981;
                    border-radius: 12px;
                    background-color: #F0FDF4;
                    color: #065F46;
                    font-size: 15px;
                    font-weight: 600;
                    padding: 20px;
                """)
            
            self.btn_process.setEnabled(True)
    
    def _process_ocr(self):
        """Process image with OCR"""
        if not self.image_path:
            return
        
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.btn_process.setEnabled(False)
            
            # Read image file
            with open(self.image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Process with OCR
            self.ocr_data = ocr_processor.extract_invoice_data(image_bytes)
            
            # Format data
            self._refresh_results_display()
            
            self.results_container.setVisible(True)
            self.btn_edit_ocr.setVisible(True)
            self.btn_import.setEnabled(True)
            
        except Exception as e:
            app_logger.error(f"OCR processing error: {e}")
            import traceback
            traceback.print_exc()
            
            # ✅ Mensaje de error con estilo personalizado
            self._show_message(
                "Error OCR",
                f"Error procesando imagen con OCR:\n\n{str(e)}\n\nVerifica que:\n"
                "1. La imagen sea legible\n"
                "2. Las credenciales de Google Cloud estén configuradas\n"
                "3. La API de Vision esté habilitada",
                QMessageBox.Icon.Critical
            )
        finally:
            self.progress.setVisible(False)
            self.btn_process.setEnabled(True)
    
    def _refresh_results_display(self):
        """Refresh the OCR results display"""
        if not self.ocr_data:
            return
        
        fecha = self.ocr_data.get('fecha_emision')
        if isinstance(fecha, datetime):
            fecha_str = fecha.strftime('%Y-%m-%d')
        else:
            fecha_str = str(fecha) if fecha else '<span style="color: #DC2626;">No detectado</span>'
        
        ncf = self.ocr_data.get('ncf') or '<span style="color: #DC2626;">No detectado</span>'
        rnc = self.ocr_data.get('rnc') or '<span style="color: #DC2626;">No detectado</span>'
        razon_social = self.ocr_data.get('razon_social') or '<span style="color: #DC2626;">No detectado</span>'
        
        subtotal = self.ocr_data.get('subtotal')
        itbis = self.ocr_data.get('itbis')
        total = self.ocr_data.get('total')
        confianza = self.ocr_data.get('confianza_ocr', 0)
        
        subtotal_str = f"<strong>DOP {subtotal:,.2f}</strong>" if subtotal else '<span style="color: #DC2626;">No detectado</span>'
        itbis_str = f"<strong>DOP {itbis:,.2f}</strong>" if itbis else '<span style="color: #DC2626;">No detectado</span>'
        total_str = f'<span style="color: #16A34A; font-size: 18px; font-weight: 700;">DOP {total:,.2f}</span>' if total else '<span style="color: #DC2626;">No detectado</span>'
        
        results_text = f"""
<table style='width: 100%; border-collapse: collapse; font-family: system-ui;'>
<tr style='border-bottom: 1px solid #E5E7EB;'>
    <td style='padding: 10px 0; font-weight: 600; color: #6B7280; width: 140px;'>NCF:</td>
    <td style='padding: 10px 0; color: #1F2937;'>{ncf}</td>
</tr>
<tr style='border-bottom: 1px solid #E5E7EB;'>
    <td style='padding: 10px 0; font-weight: 600; color: #6B7280;'>RNC:</td>
    <td style='padding: 10px 0; color: #1F2937;'>{rnc}</td>
</tr>
<tr style='border-bottom: 1px solid #E5E7EB;'>
    <td style='padding: 10px 0; font-weight: 600; color: #6B7280;'>Razón Social:</td>
    <td style='padding: 10px 0; color: #1F2937;'>{razon_social}</td>
</tr>
<tr style='border-bottom: 1px solid #E5E7EB;'>
    <td style='padding: 10px 0; font-weight: 600; color: #6B7280;'>Fecha:</td>
    <td style='padding: 10px 0; color: #1F2937;'>{fecha_str}</td>
</tr>
<tr style='border-bottom: 1px solid #E5E7EB;'>
    <td style='padding: 10px 0; font-weight: 600; color: #6B7280;'>Subtotal:</td>
    <td style='padding: 10px 0;'>{subtotal_str}</td>
</tr>
<tr style='border-bottom: 1px solid #E5E7EB;'>
    <td style='padding: 10px 0; font-weight: 600; color: #6B7280;'>ITBIS (18%):</td>
    <td style='padding: 10px 0;'>{itbis_str}</td>
</tr>
<tr>
    <td style='padding: 12px 0; font-weight: 700; color: #111827; font-size: 15px;'>TOTAL:</td>
    <td style='padding: 12px 0;'>{total_str}</td>
</tr>
</table>

<div style='margin-top: 16px; padding: 12px; background-color: #DBEAFE; border-radius: 8px; border-left: 4px solid #3B82F6;'>
    <span style='color: #1E40AF; font-size: 13px;'>
        <strong>Confianza OCR:</strong> {confianza*100:.1f}%
    </span>
</div>
"""
        
        self.results_label.setText(results_text)
    
    def _edit_ocr_data(self):
        """Allow editing OCR data before importing"""
        if not self.ocr_data:
            return
        
        dialog = EditOCRDialog(self.ocr_data, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.ocr_data = dialog.get_data()
            self._refresh_results_display()
            
            # ✅ Mensaje de éxito con estilo personalizado
            self._show_message(
                "Datos Actualizados",
                "Los datos OCR han sido actualizados correctamente",
                QMessageBox.Icon.Information
            )
    
    def _import_invoice(self):
        """Import invoice to database"""
        if not self.ocr_data:
            return
        
        try:
            empresa_id = self.empresa_combo.currentData()
            
            ncf = self.ocr_data.get('ncf') or ''
            total = float(self.ocr_data.get('total') or 0)
            
            # ✅ Validación de NCF con diálogo personalizado
            if not ncf:
                reply = self._show_question(
                    "Campo faltante",
                    "No se detectó el NCF.\n\n¿Deseas importar la factura de todas formas?\n"
                    "Podrás editarla después."
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # ✅ Validación de Total con diálogo personalizado
            if total == 0:
                reply = self._show_question(
                    "Total no detectado",
                    "No se detectó el monto total.\n\n¿Deseas importar de todas formas?"
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            invoice = {
                'company_id': int(empresa_id.replace('comp_', '')),
                'ncf': ncf,
                'rnc': self.ocr_data.get('rnc') or '',
                'razon_social': self.ocr_data.get('razon_social') or '',
                'fecha_emision': self.ocr_data.get('fecha_emision') or datetime.now(),
                'subtotal': float(self.ocr_data.get('subtotal') or 0),
                'itbis': float(self.ocr_data.get('itbis') or 0),
                'total': total,
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
            
            doc_id = firebase_handler.save_ocr_invoice(invoice, empresa_id, invoice['whatsapp_message_id'])
            
            app_logger.info(f"Invoice imported manually: {doc_id}")
            
            # ✅ Mensaje de éxito HTML formateado
            ncf_display = invoice['ncf'] or '<i style="color: #9CA3AF;">(vacío - editar después)</i>'
            success_message = f"""
    <div style='font-family: system-ui;'>
        <p style='font-size: 15px; margin-bottom: 16px;'>La factura se importó correctamente</p>
        
        <table style='width: 100%; border-collapse: collapse;'>
            <tr>
                <td style='padding: 6px 0; color: #6B7280; font-weight: 600;'>NCF:</td>
                <td style='padding: 6px 0;'>{ncf_display}</td>
            </tr>
            <tr>
                <td style='padding: 6px 0; color: #6B7280; font-weight: 600;'>Total:</td>
                <td style='padding: 6px 0; color: #16A34A; font-weight: 700; font-size: 16px;'>DOP {invoice['total']:,.2f}</td>
            </tr>
        </table>
        
        <p style='font-size: 13px; color: #6B7280; margin-top: 16px; padding-top: 12px; border-top: 1px solid #E5E7EB;'>
            Revisa la factura en la pestaña <strong>Pendientes</strong>
        </p>
    </div>
    """
            
            self._show_message(
                "✓ Factura Importada",
                success_message,
                QMessageBox.Icon.Information
            )
            
            self.invoice_imported.emit()
            self.accept()
            
        except Exception as e:
            app_logger.error(f"Import error: {e}")
            import traceback
            traceback.print_exc()
            
            # ✅ Mensaje de error con estilo personalizado
            self._show_message(
                "Error al Importar",
                f"No se pudo importar la factura:\n\n{str(e)}",
                QMessageBox.Icon.Critical
            )



    # ========================================
    # MÉTODOS HELPER PARA MENSAJES PERSONALIZADOS
    # ========================================
    
    def _show_message(self, title: str, message: str, icon: QMessageBox.Icon):
        """Show message dialog with custom styling"""
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setTextFormat(Qt.TextFormat.RichText)
        
        # ✅ Estilo según tipo de mensaje
        if icon == QMessageBox.Icon.Information:
            button_color = "#10B981"
            button_hover = "#059669"
        elif icon == QMessageBox.Icon.Critical:
            button_color = "#DC2626"
            button_hover = "#B91C1C"
        elif icon == QMessageBox.Icon.Warning:
            button_color = "#F59E0B"
            button_hover = "#D97706"
        else:
            button_color = "#2563EB"
            button_hover = "#1D4ED8"
        
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: #FFFFFF;
            }}
            QMessageBox QLabel {{
                color: #111827;
                background-color: transparent;
                min-width: 400px;
                font-size: 14px;
                padding: 8px;
            }}
            QMessageBox QPushButton {{
                background-color: {button_color};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
                min-height: 36px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {button_hover};
            }}
        """)
        
        msg.exec()
    
    def _show_question(self, title: str, message: str) -> QMessageBox.StandardButton:
        """Show question dialog with custom styling"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        # Personalizar texto de botones
        yes_btn = msg.button(QMessageBox.StandardButton.Yes)
        no_btn = msg.button(QMessageBox.StandardButton.No)
        yes_btn.setText("Sí, importar")
        no_btn.setText("No, cancelar")
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #111827;
                background-color: transparent;
                min-width: 400px;
                font-size: 14px;
                padding: 8px;
            }
            QMessageBox QPushButton {
                background-color: #FFFFFF;
                color: #374151;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 130px;
                min-height: 36px;
            }
            QMessageBox QPushButton:hover {
                background-color: #F9FAFB;
                border-color: #D1D5DB;
            }
            QMessageBox QPushButton:default {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
            }
            QMessageBox QPushButton:default:hover {
                background-color: #1D4ED8;
            }
        """)
        
        return msg.exec()



class EditOCRDialog(QDialog):
    """Dialog for editing OCR extracted data"""
    
    def __init__(self, ocr_data: dict, parent=None):
        super().__init__(parent)
        self.ocr_data = ocr_data.copy()
        
        self.setWindowTitle("Editar Datos OCR")
        self.setMinimumWidth(600)
        self.setModal(True)
        
        # ✅ Fondo blanco
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
        """)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # ✅ Header
        header_layout = QHBoxLayout()
        
        icon = QLabel("✏️")
        icon.setStyleSheet("font-size: 28px;")
        header_layout.addWidget(icon)
        
        title = QLabel("Editar Datos OCR")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #111827;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        desc = QLabel("Corrige los datos extraídos por el OCR antes de importar la factura")
        desc.setStyleSheet("""
            font-size: 14px;
            color: #6B7280;
            margin-bottom: 8px;
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #E5E7EB; max-height: 1px;")
        layout.addWidget(line)
        
        # ✅ Form layout con labels
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        input_style = """
            QLineEdit {
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                background-color: #FFFFFF;
                color: #111827;
            }
            QLineEdit:focus {
                border-color: #2563EB;
                background-color: #F0F9FF;
            }
        """
        
        label_style = """
            font-size: 14px;
            font-weight: 600;
            color: #374151;
        """
        
        # NCF
        ncf_label = QLabel("NCF:")
        ncf_label.setStyleSheet(label_style)
        self.ncf_edit = QLineEdit(self.ocr_data.get('ncf') or '')
        self.ncf_edit.setPlaceholderText("B0100000175")
        self.ncf_edit.setStyleSheet(input_style)
        form_layout.addRow(ncf_label, self.ncf_edit)
        
        # RNC
        rnc_label = QLabel("RNC:")
        rnc_label.setStyleSheet(label_style)
        self.rnc_edit = QLineEdit(self.ocr_data.get('rnc') or '')
        self.rnc_edit.setPlaceholderText("130866171")
        self.rnc_edit.setStyleSheet(input_style)
        form_layout.addRow(rnc_label, self.rnc_edit)
        
        # Razón Social
        razon_label = QLabel("Razón Social:")
        razon_label.setStyleSheet(label_style)
        self.razon_edit = QLineEdit(self.ocr_data.get('razon_social') or '')
        self.razon_edit.setPlaceholderText("EMPRESA SRL")
        self.razon_edit.setStyleSheet(input_style)
        form_layout.addRow(razon_label, self.razon_edit)
        
        # Subtotal
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setStyleSheet(label_style)
        self.subtotal_edit = QLineEdit(str(self.ocr_data.get('subtotal') or '0'))
        self.subtotal_edit.setPlaceholderText("0.00")
        self.subtotal_edit.setStyleSheet(input_style)
        form_layout.addRow(subtotal_label, self.subtotal_edit)
        
        # ITBIS
        itbis_label = QLabel("ITBIS:")
        itbis_label.setStyleSheet(label_style)
        self.itbis_edit = QLineEdit(str(self.ocr_data.get('itbis') or '0'))
        self.itbis_edit.setPlaceholderText("0.00")
        self.itbis_edit.setStyleSheet(input_style)
        form_layout.addRow(itbis_label, self.itbis_edit)
        
        # Total
        total_label = QLabel("Total:")
        total_label.setStyleSheet(label_style)
        self.total_edit = QLineEdit(str(self.ocr_data.get('total') or '0'))
        self.total_edit.setPlaceholderText("0.00")
        self.total_edit.setStyleSheet(input_style)
        form_layout.addRow(total_label, self.total_edit)
        
        layout.addLayout(form_layout)
        
        layout.addStretch()
        
        # ✅ Botones grandes
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumSize(140, 48)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #374151;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F9FAFB;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("✓  Guardar")
        btn_save.setMinimumSize(140, 48)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def _save(self):
        """Save edited data"""
        try:
            self.ocr_data['ncf'] = self.ncf_edit.text().strip()
            self.ocr_data['rnc'] = self.rnc_edit.text().strip()
            self.ocr_data['razon_social'] = self.razon_edit.text().strip()
            self.ocr_data['subtotal'] = float(self.subtotal_edit.text() or 0)
            self.ocr_data['itbis'] = float(self.itbis_edit.text() or 0)
            self.ocr_data['total'] = float(self.total_edit.text() or 0)
            
            self.accept()
        except ValueError:
            # ✅ Mensaje de error con estilo personalizado
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Error de Validación")
            msg.setText("Los montos deben ser números válidos.\n\nUsa formato: 1234.56")
            
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                }
                QMessageBox QLabel {
                    color: #111827;
                    background-color: transparent;
                    min-width: 350px;
                    font-size: 14px;
                    padding: 8px;
                }
                QMessageBox QPushButton {
                    background-color: #F59E0B;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 100px;
                    min-height: 36px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #D97706;
                }
            """)
            
            msg.exec()
    
    def get_data(self) -> dict:
        """Get edited data"""
        return self.ocr_data