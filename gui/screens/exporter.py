"""
Exporter screen - Export wizard for facturas
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QTableWidget, QTableWidgetItem,
                             QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
                             QMessageBox, QFileDialog, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.utils import FirebaseWorkerPool
from app.firebase_handler import firebase_handler
from app.export_handler import export_handler
from app.models import Invoice, InvoiceAmounts, InvoiceMetadata


class ExporterScreen(QWidget):
    """Export wizard screen"""
    
    back_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_empresa_id = None
        self.empresas = []
        self.facturas = []
        self.selected_facturas = []
        self.worker_pool = FirebaseWorkerPool()
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Volver")
        back_btn.setProperty("class", "outline")
        back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(back_btn)
        
        title = QLabel("Exportar Facturas")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #212121;")
        header_layout.addWidget(title, 1)
        
        main_layout.addLayout(header_layout)
        
        # Step 1: Empresa selector
        step1 = self._create_step1()
        main_layout.addWidget(step1)
        
        # Step 2: Factura selection table
        step2 = self._create_step2()
        main_layout.addWidget(step2)
        
        # Step 3: Export configuration
        step3 = self._create_step3()
        main_layout.addWidget(step3)
        
        # Step 4: Summary and export
        step4 = self._create_step4()
        main_layout.addWidget(step4)
    
    def _create_step1(self) -> QWidget:
        """Create step 1: Empresa selector"""
        group = QGroupBox("Paso 1: Seleccionar Empresa")
        layout = QVBoxLayout(group)
        
        label = QLabel("Empresa:")
        layout.addWidget(label)
        
        self.empresa_combo = QComboBox()
        self.empresa_combo.currentIndexChanged.connect(self._on_empresa_changed)
        layout.addWidget(self.empresa_combo)
        
        return group
    
    def _create_step2(self) -> QWidget:
        """Create step 2: Factura selection"""
        group = QGroupBox("Paso 2: Seleccionar Facturas")
        layout = QVBoxLayout(group)
        
        # Select all checkbox
        select_all_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Seleccionar Todas")
        self.select_all_checkbox.toggled.connect(self._on_select_all)
        select_all_layout.addWidget(self.select_all_checkbox)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por NCF...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        select_all_layout.addWidget(self.search_input)
        select_all_layout.addStretch()
        
        layout.addLayout(select_all_layout)
        
        # Facturas table
        self.facturas_table = QTableWidget()
        self.facturas_table.setColumnCount(6)
        self.facturas_table.setHorizontalHeaderLabels([
            "☑", "NCF", "RNC", "Razón Social", "Fecha", "Total"
        ])
        self.facturas_table.setColumnWidth(0, 40)
        self.facturas_table.setColumnWidth(1, 140)
        self.facturas_table.setColumnWidth(2, 120)
        self.facturas_table.setColumnWidth(3, 250)
        self.facturas_table.setColumnWidth(4, 100)
        self.facturas_table.setColumnWidth(5, 120)
        self.facturas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.facturas_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.facturas_table)
        
        return group
    
    def _create_step3(self) -> QWidget:
        """Create step 3: Export configuration"""
        group = QGroupBox("Paso 3: Configuración de Exportación")
        layout = QVBoxLayout(group)
        
        # Format selection
        format_label = QLabel("Formato:")
        layout.addWidget(format_label)
        
        self.format_group = QButtonGroup()
        format_layout = QHBoxLayout()
        
        csv_radio = QRadioButton("CSV")
        csv_radio.setChecked(True)
        self.format_group.addButton(csv_radio, 1)
        format_layout.addWidget(csv_radio)
        
        json_radio = QRadioButton("JSON")
        self.format_group.addButton(json_radio, 2)
        format_layout.addWidget(json_radio)
        
        both_radio = QRadioButton("Ambos")
        self.format_group.addButton(both_radio, 3)
        format_layout.addWidget(both_radio)
        
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Mark as exported checkbox
        self.mark_exported_checkbox = QCheckBox("☑ Marcar como exportadas después")
        self.mark_exported_checkbox.setChecked(True)
        layout.addWidget(self.mark_exported_checkbox)
        
        return group
    
    def _create_step4(self) -> QWidget:
        """Create step 4: Summary and export"""
        group = QGroupBox("Paso 4: Resumen y Exportar")
        layout = QVBoxLayout(group)
        
        # Summary panel
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #F8F9FA; border-radius: 4px; padding: 16px;")
        summary_layout = QVBoxLayout(summary_frame)
        
        self.count_label = QLabel("Facturas seleccionadas: 0")
        self.count_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        summary_layout.addWidget(self.count_label)
        
        self.total_label = QLabel("Total monto: DOP 0.00")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        summary_layout.addWidget(self.total_label)
        
        layout.addWidget(summary_frame)
        
        # Export button
        self.export_btn = QPushButton("📤 EXPORTAR AHORA")
        self.export_btn.setProperty("class", "primary")
        self.export_btn.setFixedHeight(50)
        self.export_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.export_btn.clicked.connect(self._export_facturas)
        layout.addWidget(self.export_btn)
        
        return group
    
    def load_empresa(self, empresa_id: str):
        """Load empresa and its facturas ready for export"""
        self.current_empresa_id = empresa_id
        
        # Load empresas for combo
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=self._on_empresas_loaded,
            on_error=self._on_error
        )
    
    def _on_empresas_loaded(self, empresas: list):
        """Handle empresas loaded"""
        self.empresas = empresas
        self.empresa_combo.clear()
        
        for i, empresa in enumerate(empresas):
            # Get count of facturas ready to export
            empresa_id = empresa.get('id')
            nombre = empresa.get('nombre', 'Sin Nombre')
            
            # We'll show the count after loading facturas
            self.empresa_combo.addItem(nombre, empresa_id)
            
            # Select current empresa
            if empresa_id == self.current_empresa_id:
                self.empresa_combo.setCurrentIndex(i)
    
    def _on_empresa_changed(self, index: int):
        """Handle empresa selection change"""
        if index >= 0:
            empresa_id = self.empresa_combo.itemData(index)
            if empresa_id:
                self._load_facturas(empresa_id)
    
    def _load_facturas(self, empresa_id: str):
        """Load facturas ready for export"""
        self.current_empresa_id = empresa_id
        self.worker_pool.execute(
            firebase_handler.get_facturas_para_exportar,
            on_success=self._on_facturas_loaded,
            on_error=self._on_error,
            empresa_id
        )
    
    def _on_facturas_loaded(self, facturas: list):
        """Handle facturas loaded"""
        self.facturas = facturas
        self._populate_table()
        self._update_summary()
    
    def _populate_table(self):
        """Populate facturas table"""
        self.facturas_table.setRowCount(len(self.facturas))
        
        for row, factura in enumerate(self.facturas):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.toggled.connect(self._update_summary)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.facturas_table.setCellWidget(row, 0, checkbox_widget)
            
            # NCF
            ncf_item = QTableWidgetItem(factura.get('ncf', ''))
            ncf_item.setFlags(ncf_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.facturas_table.setItem(row, 1, ncf_item)
            
            # RNC
            rnc_item = QTableWidgetItem(factura.get('rnc', ''))
            rnc_item.setFlags(rnc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.facturas_table.setItem(row, 2, rnc_item)
            
            # Razón Social
            razon_item = QTableWidgetItem(factura.get('razon_social', ''))
            razon_item.setFlags(razon_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.facturas_table.setItem(row, 3, razon_item)
            
            # Fecha
            fecha_item = QTableWidgetItem(factura.get('fecha_emision', ''))
            fecha_item.setFlags(fecha_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.facturas_table.setItem(row, 4, fecha_item)
            
            # Total
            total = factura.get('total', 0) or 0
            total_item = QTableWidgetItem(f"DOP {total:,.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.facturas_table.setItem(row, 5, total_item)
    
    def _on_select_all(self, checked: bool):
        """Handle select all checkbox"""
        for row in range(self.facturas_table.rowCount()):
            checkbox_widget = self.facturas_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(checked)
    
    def _on_search(self, text: str):
        """Handle search"""
        search_text = text.lower()
        for row in range(self.facturas_table.rowCount()):
            ncf_item = self.facturas_table.item(row, 1)
            if ncf_item:
                show = search_text in ncf_item.text().lower()
                self.facturas_table.setRowHidden(row, not show)
    
    def _update_summary(self):
        """Update summary panel"""
        selected_count = 0
        total_amount = 0.0
        
        for row in range(self.facturas_table.rowCount()):
            checkbox_widget = self.facturas_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
                    if row < len(self.facturas):
                        total_amount += self.facturas[row].get('total', 0) or 0
        
        self.count_label.setText(f"Facturas seleccionadas: {selected_count}")
        self.total_label.setText(f"Total monto: DOP {total_amount:,.2f}")
    
    def _get_selected_facturas(self) -> list:
        """Get list of selected facturas"""
        selected = []
        for row in range(self.facturas_table.rowCount()):
            checkbox_widget = self.facturas_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked() and row < len(self.facturas):
                    selected.append(self.facturas[row])
        return selected
    
    def _export_facturas(self):
        """Export selected facturas"""
        selected = self._get_selected_facturas()
        
        if not selected:
            QMessageBox.warning(self, "Advertencia", 
                              "No hay facturas seleccionadas para exportar")
            return
        
        # Determine format
        format_id = self.format_group.checkedId()
        if format_id == 1:
            format_type = 'csv'
        elif format_id == 2:
            format_type = 'json'
        else:
            format_type = 'both'
        
        # Convert dict to Invoice objects
        invoices = []
        for factura_dict in selected:
            # Create Invoice object from dict
            invoice = Invoice(
                id=factura_dict.get('id', ''),
                fecha_procesamiento=datetime.now(),
                ncf=factura_dict.get('ncf'),
                rnc=factura_dict.get('rnc'),
                razon_social=factura_dict.get('razon_social'),
                fecha_emision=factura_dict.get('fecha_emision'),
                montos=InvoiceAmounts(
                    subtotal=factura_dict.get('subtotal'),
                    itbis=factura_dict.get('itbis'),
                    total=factura_dict.get('total'),
                    moneda=factura_dict.get('moneda', 'DOP')
                ),
                metadata=InvoiceMetadata(
                    imagen_original=factura_dict.get('imagen_original'),
                    confianza_ocr=factura_dict.get('confianza_ocr'),
                    origen=factura_dict.get('origen', 'whatsapp')
                )
            )
            invoices.append(invoice)
        
        try:
            # Export
            result = export_handler.export(invoices, format_type)
            
            # Show success message
            files_exported = []
            if 'csv' in result:
                files_exported.append(result['csv'])
            if 'json' in result:
                files_exported.append(result['json'])
            
            files_str = '\n'.join(files_exported)
            
            QMessageBox.information(
                self,
                "Éxito",
                f"✓ Exportadas {len(selected)} facturas\n\nArchivos:\n{files_str}"
            )
            
            # Mark as exported if checkbox is checked
            if self.mark_exported_checkbox.isChecked():
                self._mark_as_exported(selected)
            else:
                # Refresh the list
                self._load_facturas(self.current_empresa_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
    
    def _mark_as_exported(self, facturas: list):
        """Mark facturas as exported"""
        for factura in facturas:
            firebase_handler.mark_factura_exportada(
                self.current_empresa_id,
                factura.get('id')
            )
        
        # Refresh list
        self._load_facturas(self.current_empresa_id)
    
    def _on_error(self, error_msg: str):
        """Handle error"""
        QMessageBox.critical(self, "Error", f"Error: {error_msg}")


# Import QLineEdit which was missing
from PyQt6.QtWidgets import QLineEdit
