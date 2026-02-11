"""
Editor screen - Factura editor with image viewer and form
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
                             QPushButton, QLabel, QLineEdit, QDoubleSpinBox,
                             QDateEdit, QScrollArea, QCheckBox, QMessageBox,
                             QGroupBox, QFrame)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import pyqtSignal, Qt, QDate
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.widgets import ImageViewer, FormField
from gui.utils import FirebaseWorkerPool
from app.firebase_handler import firebase_handler


class EditorScreen(QWidget):
    """Factura editor screen"""
    
    back_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_empresa_id = None
        self.current_factura_id = None
        self.current_factura = None
        self.facturas_list = []  # For navigation
        self.current_index = -1
        self.worker_pool = FirebaseWorkerPool()
        self._init_ui()
        self._setup_shortcuts()
    
    def _init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Splitter with image viewer and form
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Image viewer (60%)
        self.image_viewer = ImageViewer()
        splitter.addWidget(self.image_viewer)
        
        # Right: Form (40%)
        form_widget = self._create_form()
        splitter.addWidget(form_widget)
        
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter)
        
        # Navigation footer
        footer = self._create_footer()
        main_layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Create header bar"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #E0E0E0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Back button
        back_btn = QPushButton("← Volver")
        back_btn.setProperty("class", "outline")
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        # Title
        self.title_label = QLabel("Editor de Factura")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #212121;")
        header_layout.addWidget(self.title_label, 1)
        
        return header
    
    def _create_form(self) -> QWidget:
        """Create form widget"""
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: white; }")
        
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(16)
        
        # Form header
        form_header = QLabel("Datos de la Factura")
        form_header.setStyleSheet("font-size: 16px; font-weight: 600; color: #212121;")
        form_layout.addWidget(form_header)
        
        # NCF field
        ncf_label = QLabel("NCF:")
        form_layout.addWidget(ncf_label)
        self.ncf_input = QLineEdit()
        self.ncf_input.setFont(self.ncf_input.font())
        form_layout.addWidget(self.ncf_input)
        
        # RNC field
        rnc_label = QLabel("RNC:")
        form_layout.addWidget(rnc_label)
        self.rnc_input = QLineEdit()
        form_layout.addWidget(self.rnc_input)
        
        # Razón Social field
        razon_label = QLabel("Razón Social:")
        form_layout.addWidget(razon_label)
        self.razon_input = QLineEdit()
        form_layout.addWidget(self.razon_input)
        
        # Fecha Emisión field
        fecha_label = QLabel("Fecha de Emisión:")
        form_layout.addWidget(fecha_label)
        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addWidget(self.fecha_input)
        
        # Montos section
        montos_group = QGroupBox("Montos")
        montos_layout = QVBoxLayout(montos_group)
        
        # Subtotal
        subtotal_label = QLabel("Subtotal (DOP):")
        montos_layout.addWidget(subtotal_label)
        self.subtotal_input = QDoubleSpinBox()
        self.subtotal_input.setDecimals(2)
        self.subtotal_input.setMaximum(999999999.99)
        self.subtotal_input.valueChanged.connect(self._on_amount_changed)
        montos_layout.addWidget(self.subtotal_input)
        
        # ITBIS
        itbis_label = QLabel("ITBIS (DOP):")
        montos_layout.addWidget(itbis_label)
        self.itbis_input = QDoubleSpinBox()
        self.itbis_input.setDecimals(2)
        self.itbis_input.setMaximum(999999999.99)
        self.itbis_input.valueChanged.connect(self._on_amount_changed)
        montos_layout.addWidget(self.itbis_input)
        
        # Total
        total_label = QLabel("Total (DOP):")
        montos_layout.addWidget(total_label)
        self.total_input = QDoubleSpinBox()
        self.total_input.setDecimals(2)
        self.total_input.setMaximum(999999999.99)
        montos_layout.addWidget(self.total_input)
        
        # Auto-calculate checkbox
        self.auto_calc_checkbox = QCheckBox("✓ Calcular automáticamente")
        self.auto_calc_checkbox.setChecked(True)
        montos_layout.addWidget(self.auto_calc_checkbox)
        
        form_layout.addWidget(montos_group)
        
        # Action buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Save button
        save_btn = QPushButton("💾 Guardar Cambios")
        save_btn.setProperty("class", "primary")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_changes)
        buttons_layout.addWidget(save_btn)
        
        # Mark as reviewed button
        review_btn = QPushButton("✓ Marcar como Revisada")
        review_btn.setProperty("class", "success")
        review_btn.setFixedHeight(40)
        review_btn.clicked.connect(self._mark_reviewed)
        buttons_layout.addWidget(review_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.setProperty("class", "error")
        delete_btn.setFixedHeight(40)
        delete_btn.clicked.connect(self._delete_factura)
        buttons_layout.addWidget(delete_btn)
        
        form_layout.addLayout(buttons_layout)
        form_layout.addStretch()
        
        scroll.setWidget(form_container)
        return scroll
    
    def _create_footer(self) -> QWidget:
        """Create navigation footer"""
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet("background-color: white; border-top: 1px solid #E0E0E0;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        # Previous button
        self.prev_btn = QPushButton("◀ Anterior")
        self.prev_btn.setProperty("class", "outline")
        self.prev_btn.clicked.connect(self._previous_factura)
        footer_layout.addWidget(self.prev_btn)
        
        footer_layout.addStretch()
        
        # Position label
        self.position_label = QLabel("1 de 1")
        self.position_label.setStyleSheet("color: #757575;")
        footer_layout.addWidget(self.position_label)
        
        footer_layout.addStretch()
        
        # Next button
        self.next_btn = QPushButton("Siguiente ▶")
        self.next_btn.setProperty("class", "outline")
        self.next_btn.clicked.connect(self._next_factura)
        footer_layout.addWidget(self.next_btn)
        
        return footer
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_changes)
        QShortcut(QKeySequence("Ctrl+Return"), self, self._mark_reviewed)
        QShortcut(QKeySequence("Ctrl+Left"), self, self._previous_factura)
        QShortcut(QKeySequence("Ctrl+Right"), self, self._next_factura)
    
    def load_factura(self, empresa_id: str, factura_id: str):
        """Load factura data"""
        self.current_empresa_id = empresa_id
        self.current_factura_id = factura_id
        
        # Load factura
        self.worker_pool.execute(
            lambda: firebase_handler.get_factura(empresa_id, factura_id),
            on_success=self._on_factura_loaded,
            on_error=self._on_error
        )
        
        # Load all facturas for navigation
        self.worker_pool.execute(
            lambda: firebase_handler.get_facturas_by_empresa(empresa_id),
            on_success=self._on_facturas_list_loaded,
            on_error=self._on_error
        )
    
    def _on_factura_loaded(self, factura: dict):
        """Handle factura data loaded"""
        if not factura:
            QMessageBox.warning(self, "Error", "No se pudo cargar la factura")
            return
        
        self.current_factura = factura
        
        # Update title
        ncf = factura.get('ncf', 'Sin NCF')
        self.title_label.setText(f"Editar Factura #{ncf}")
        
        # Populate form
        self.ncf_input.setText(factura.get('ncf', ''))
        self.rnc_input.setText(factura.get('rnc', ''))
        self.razon_input.setText(factura.get('razon_social', ''))
        
        # Date
        fecha_str = factura.get('fecha_emision', '')
        if fecha_str:
            try:
                date_parts = fecha_str.split('-')
                if len(date_parts) == 3:
                    qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                    self.fecha_input.setDate(qdate)
            except:
                pass
        
        # Amounts
        self.subtotal_input.setValue(factura.get('subtotal', 0) or 0)
        self.itbis_input.setValue(factura.get('itbis', 0) or 0)
        self.total_input.setValue(factura.get('total', 0) or 0)
        
        # Load image
        imagen_url = factura.get('imagen_original', '')
        if imagen_url:
            # If it's a relative path, you might need to construct full URL
            # For now, assuming it's a full URL or local path
            if imagen_url.startswith('http'):
                self.image_viewer.load_image_from_url(imagen_url)
            else:
                # Try as local file path
                self.image_viewer.load_image_from_path(imagen_url)
        else:
            self.image_viewer.show_placeholder("Sin imagen disponible")
    
    def _on_facturas_list_loaded(self, facturas: list):
        """Handle facturas list loaded for navigation"""
        self.facturas_list = facturas
        
        # Find current index
        for i, f in enumerate(facturas):
            if f.get('id') == self.current_factura_id:
                self.current_index = i
                break
        
        self._update_navigation()
    
    def _update_navigation(self):
        """Update navigation buttons and label"""
        total = len(self.facturas_list)
        current = self.current_index + 1
        
        self.position_label.setText(f"{current} de {total}")
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < total - 1)
    
    def _previous_factura(self):
        """Navigate to previous factura"""
        if self.current_index > 0:
            self.current_index -= 1
            next_factura = self.facturas_list[self.current_index]
            self.load_factura(self.current_empresa_id, next_factura.get('id'))
    
    def _next_factura(self):
        """Navigate to next factura"""
        if self.current_index < len(self.facturas_list) - 1:
            self.current_index += 1
            next_factura = self.facturas_list[self.current_index]
            self.load_factura(self.current_empresa_id, next_factura.get('id'))
    
    def _on_amount_changed(self):
        """Handle amount change for auto-calculation"""
        if self.auto_calc_checkbox.isChecked():
            subtotal = self.subtotal_input.value()
            itbis = self.itbis_input.value()
            self.total_input.setValue(subtotal + itbis)
    
    def _save_changes(self):
        """Save factura changes"""
        if not self.current_empresa_id or not self.current_factura_id:
            return
        
        # Validate amounts
        subtotal = self.subtotal_input.value()
        itbis = self.itbis_input.value()
        total = self.total_input.value()
        
        if abs((subtotal + itbis) - total) > 0.01 and not self.auto_calc_checkbox.isChecked():
            reply = QMessageBox.question(
                self,
                "Advertencia",
                f"La suma Subtotal + ITBIS ({subtotal + itbis:.2f}) no coincide con el Total ({total:.2f}).\n\n"
                "¿Desea guardar de todas formas?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Prepare updates
        updates = {
            'ncf': self.ncf_input.text(),
            'rnc': self.rnc_input.text(),
            'razon_social': self.razon_input.text(),
            'fecha_emision': self.fecha_input.date().toString("yyyy-MM-dd"),
            'subtotal': subtotal,
            'itbis': itbis,
            'total': total,
        }
        
        # Save to Firebase
        self.worker_pool.execute(
            lambda: firebase_handler.update_factura(self.current_empresa_id, self.current_factura_id, updates),
            on_success=lambda success: self._on_save_complete(success),
            on_error=self._on_error
        )
    
    def _mark_reviewed(self):
        """Mark factura as reviewed"""
        if not self.current_empresa_id or not self.current_factura_id:
            return
        
        # First save any changes
        self._save_changes()
        
        # Then mark as reviewed
        self.worker_pool.execute(
            lambda: firebase_handler.mark_factura_revisada(self.current_empresa_id, self.current_factura_id),
            on_success=lambda success: self._on_review_complete(success),
            on_error=self._on_error
        )
    
    def _delete_factura(self):
        """Delete current factura"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de que desea eliminar esta factura?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.worker_pool.execute(
                lambda: firebase_handler.delete_factura(self.current_empresa_id, self.current_factura_id),
                on_success=lambda success: self._on_delete_complete(success),
                on_error=self._on_error
            )
    
    def _on_save_complete(self, success: bool):
        """Handle save completion"""
        if success:
            QMessageBox.information(self, "Éxito", "Cambios guardados correctamente")
        else:
            QMessageBox.warning(self, "Error", "No se pudieron guardar los cambios")
    
    def _on_review_complete(self, success: bool):
        """Handle review completion"""
        if success:
            QMessageBox.information(self, "Éxito", "Factura marcada como revisada")
        else:
            QMessageBox.warning(self, "Error", "No se pudo marcar como revisada")
    
    def _on_delete_complete(self, success: bool):
        """Handle delete completion"""
        if success:
            QMessageBox.information(self, "Éxito", "Factura eliminada correctamente")
            self.back_requested.emit()
        else:
            QMessageBox.warning(self, "Error", "No se pudo eliminar la factura")
    
    def _on_error(self, error_msg: str):
        """Handle error"""
        QMessageBox.critical(self, "Error", f"Error: {error_msg}")
