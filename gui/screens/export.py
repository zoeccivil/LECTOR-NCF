"""
Export screen - Redesigned with better styling and visibility
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                             QCheckBox, QRadioButton, QButtonGroup, QLineEdit,
                             QHeaderView, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.utils import FirebaseWorkerPool
from app.firebase_handler import firebase_handler
from app.export_handler import export_handler


class ExporterScreen(QWidget):
    """Export screen - Redesigned"""
    
    back_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_pool = FirebaseWorkerPool()
        self.empresas = []
        self.facturas = []
        self.selected_facturas = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        # Main container with background
        self.setStyleSheet("""
            QWidget {
                background-color: #F9FAFB;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Back button
        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #2563EB;
                font-size: 15px;
                font-weight: 600;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #EFF6FF;
                border-radius: 8px;
            }
        """)
        btn_back.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(btn_back)
        
        header_layout.addStretch()
        
        # Title
        title = QLabel("Exportar Facturas")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #111827;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Step 1: Empresa
        step1 = self._create_step_widget(
            "1", 
            "Seleccionar Empresa",
            self._create_empresa_selector()
        )
        layout.addWidget(step1)
        
        # Step 2: Facturas
        step2 = self._create_step_widget(
            "2",
            "Seleccionar Facturas",
            self._create_facturas_table()
        )
        layout.addWidget(step2)
        
        # Step 3: Formato
        step3 = self._create_step_widget(
            "3",
            "Configuración de Exportación",
            self._create_format_selector()
        )
        layout.addWidget(step3)
        
        # Step 4: Summary
        step4 = self._create_step_widget(
            "4",
            "Resumen y Exportar",
            self._create_summary()
        )
        layout.addWidget(step4)
        
        layout.addStretch()
        
        # Export button
        self.btn_export = QPushButton("📤 EXPORTAR AHORA")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setMinimumHeight(56)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
        """)
        self.btn_export.clicked.connect(self._on_export)
        layout.addWidget(self.btn_export)
    
    def _create_step_widget(self, number: str, title: str, content: QWidget) -> QWidget:
        """Create step container"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)
        
        # Step header
        header_layout = QHBoxLayout()
        
        # Step number badge
        badge = QLabel(number)
        badge.setFixedSize(36, 36)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("""
            background-color: #2563EB;
            color: #FFFFFF;
            border-radius: 18px;
            font-size: 18px;
            font-weight: 700;
        """)
        header_layout.addWidget(badge)
        
        # Step title
        step_title = QLabel(title)
        step_title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #111827;
            margin-left: 4px;
        """)
        header_layout.addWidget(step_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(content)
        
        return container
    
    def _create_empresa_selector(self) -> QWidget:
        """Create empresa selector"""
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        label = QLabel("Empresa:")
        label.setStyleSheet("""
            font-size: 14px;
            color: #374151;
            font-weight: 600;
            background-color: transparent;
        """)
        layout.addWidget(label)
        
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
            QComboBox::drop-down {
                border: none;
                width: 30px;
                background-color: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #6B7280;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                selection-background-color: #EFF6FF;
                selection-color: #2563EB;
                color: #111827;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 6px 12px;
                color: #111827;
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F3F4F6;
                color: #111827;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #EFF6FF;
                color: #2563EB;
            }
        """)
        self.empresa_combo.currentIndexChanged.connect(self._on_empresa_changed)
        layout.addWidget(self.empresa_combo)
        
        return widget
    
    def _create_facturas_table(self) -> QWidget:
        """Create facturas table"""
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        # ✅ AGREGAR INDICADOR
        info_label = QLabel("✓ Solo facturas REVISADAS (listas para exportar)")
        info_label.setStyleSheet("""
            background-color: #D1FAE5;
            color: #065F46;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid #10B981;
        """)
        layout.addWidget(info_label)
        
        # Select all + Search
        controls_layout = QHBoxLayout()
        
        
        self.chk_select_all = QCheckBox("Seleccionar Todas")
        self.chk_select_all.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #374151;
                font-weight: 600;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #D1D5DB;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        self.chk_select_all.stateChanged.connect(self._on_select_all)
        controls_layout.addWidget(self.chk_select_all)
        
        controls_layout.addStretch()
        
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Buscar por NCF...")
        search_box.setMinimumWidth(280)
        search_box.setMinimumHeight(40)
        search_box.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                color: #111827;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
        """)
        search_box.textChanged.connect(self._on_search_facturas)
        controls_layout.addWidget(search_box)
        
        layout.addLayout(controls_layout)
        
        # Table
        self.facturas_table = QTableWidget()
        self.facturas_table.setColumnCount(6)
        self.facturas_table.setHorizontalHeaderLabels(['☑', 'NCF', 'RNC', 'RAZÓN SOCIAL', 'FECHA', 'TOTAL'])
        self.facturas_table.verticalHeader().setVisible(False)
        self.facturas_table.setAlternatingRowColors(True)
        self.facturas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.facturas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.facturas_table.verticalHeader().setDefaultSectionSize(48)
        
        # Headers
        header = self.facturas_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.facturas_table.setColumnWidth(0, 60)
        
        # Styles
        self.facturas_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
            }
            QTableWidget::item {
                padding: 10px 12px;
                color: #111827;
                font-size: 13px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #374151;
                padding: 12px 10px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """)
        
        layout.addWidget(self.facturas_table)
        
        return widget
    
    def _create_format_selector(self) -> QWidget:
        """Create format selector"""
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Format label
        format_label = QLabel("Formato:")
        format_label.setStyleSheet("""
            font-size: 14px;
            color: #374151;
            font-weight: 600;
            background-color: transparent;
        """)
        layout.addWidget(format_label)
        
        # Radio buttons
        format_layout = QHBoxLayout()
        
        self.format_group = QButtonGroup()
        
        self.radio_csv = QRadioButton("CSV")
        self.radio_csv.setChecked(True)
        self.radio_csv.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #111827;
                background-color: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #D1D5DB;
                border-radius: 9px;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        self.format_group.addButton(self.radio_csv)
        format_layout.addWidget(self.radio_csv)
        
        self.radio_json = QRadioButton("JSON")
        self.radio_json.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #111827;
                background-color: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #D1D5DB;
                border-radius: 9px;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        self.format_group.addButton(self.radio_json)
        format_layout.addWidget(self.radio_json)
        
        self.radio_both = QRadioButton("Ambos")
        self.radio_both.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #111827;
                background-color: transparent;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #D1D5DB;
                border-radius: 9px;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        self.format_group.addButton(self.radio_both)
        format_layout.addWidget(self.radio_both)
        
        format_layout.addStretch()
        
        layout.addLayout(format_layout)
        
        # Mark exported checkbox
        self.chk_mark_exported = QCheckBox("Marcar como exportadas después")
        self.chk_mark_exported.setChecked(True)
        self.chk_mark_exported.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #374151;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #D1D5DB;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        layout.addWidget(self.chk_mark_exported)
        
        return widget
    
    def _create_summary(self) -> QWidget:
        """Create summary widget"""
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self.lbl_count = QLabel("Facturas seleccionadas: 0")
        self.lbl_count.setStyleSheet("""
            font-size: 16px;
            color: #111827;
            font-weight: 600;
            background-color: transparent;
        """)
        layout.addWidget(self.lbl_count)
        
        self.lbl_total = QLabel("Total monto: DOP 0.00")
        self.lbl_total.setStyleSheet("""
            font-size: 16px;
            color: #111827;
            font-weight: 600;
            background-color: transparent;
        """)
        layout.addWidget(self.lbl_total)
        
        return widget
    
    def load_empresas(self):
        """Load empresas"""
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=self._on_empresas_loaded,
            on_error=lambda e: QMessageBox.critical(self, "Error", str(e))
        )

    def load_for_empresa(self, empresa_id: str):
        """
        Load exporter in automatic mode for specific empresa.
        Pre-loads only reviewed invoices ready for export.
        """
        # First load all empresas
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=lambda empresas: self._on_empresas_loaded_auto(empresas, empresa_id),
            on_error=lambda e: QMessageBox.critical(self, "Error", str(e))
        )

    def _on_empresas_loaded_auto(self, empresas, empresa_id: str):
        """Handle empresas loaded in auto mode"""
        self.empresas = empresas
        self.empresa_combo.clear()
        
        # Populate combo
        for emp in empresas:
            self.empresa_combo.addItem(emp['nombre'], emp['id'])
        
        # Pre-select empresa
        for i in range(self.empresa_combo.count()):
            if self.empresa_combo.itemData(i) == empresa_id:
                self.empresa_combo.setCurrentIndex(i)
                break
        
        # Disable empresa selector (locked to this empresa)
        self.empresa_combo.setEnabled(False)
        self.empresa_combo.setStyleSheet(self.empresa_combo.styleSheet() + """
            QComboBox:disabled {
                background-color: #F3F4F6;
                color: #6B7280;
            }
        """)

    def set_empresa(self, empresa_id: str):
        """Pre-select empresa in combo box"""
        for i in range(self.empresa_combo.count()):
            if self.empresa_combo.itemData(i) == empresa_id:
                self.empresa_combo.setCurrentIndex(i)
                break

    def _on_empresas_loaded(self, empresas):
        """Handle empresas loaded"""
        self.empresas = empresas
        self.empresa_combo.clear()
        for emp in empresas:
            self.empresa_combo.addItem(emp['nombre'], emp['id'])


        
    def _on_empresa_changed(self, index):
        """Handle empresa changed"""
        if index < 0:
            return
        
        empresa_id = self.empresa_combo.currentData()
        if empresa_id:
            self._load_facturas(empresa_id)
    
    def _load_facturas(self, empresa_id):
        """Load facturas for empresa - ONLY REVIEWED invoices"""
        if hasattr(firebase_handler, 'get_ocr_facturas_by_empresa'):
            # ✅ SOLO facturas revisadas (listas para exportar)
            fetch_func = lambda: firebase_handler.get_ocr_facturas_by_empresa(
                empresa_id, 
                estado='revisada'
            )
        else:
            # Fallback para sistema legacy
            fetch_func = lambda: firebase_handler.get_facturas_para_exportar(empresa_id)
        
        self.worker_pool.execute(
            fetch_func,
            on_success=self._on_facturas_loaded,
            on_error=lambda e: QMessageBox.critical(self, "Error", str(e))
        )
    
    def _on_facturas_loaded(self, facturas):
        """Handle facturas loaded"""
        self.facturas = facturas
        self._populate_facturas_table()
    
    def _populate_facturas_table(self):
        """Populate facturas table"""
        self.facturas_table.setRowCount(0)
        
        for factura in self.facturas:
            row = self.facturas_table.rowCount()
            self.facturas_table.insertRow(row)
            
            # Checkbox
            chk = QCheckBox()
            chk.setProperty('factura_id', factura['id'])
            chk.setStyleSheet("""
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #D1D5DB;
                    border-radius: 4px;
                    background-color: #FFFFFF;
                }
                QCheckBox::indicator:checked {
                    background-color: #2563EB;
                    border-color: #2563EB;
                }
            """)
            chk.stateChanged.connect(self._update_summary)
            chk_widget = QWidget()
            chk_widget.setStyleSheet("background-color: transparent;")
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.facturas_table.setCellWidget(row, 0, chk_widget)
            
            # NCF
            ncf_item = QTableWidgetItem(factura.get('ncf', ''))
            ncf_item.setForeground(QColor('#2563EB'))
            font_ncf = ncf_item.font()
            font_ncf.setWeight(QFont.Weight.Medium)
            ncf_item.setFont(font_ncf)
            self.facturas_table.setItem(row, 1, ncf_item)
            
            # RNC
            rnc_item = QTableWidgetItem(factura.get('rnc', ''))
            rnc_item.setForeground(QColor('#111827'))
            self.facturas_table.setItem(row, 2, rnc_item)
            
            # Razón Social
            razon_item = QTableWidgetItem(factura.get('razon_social', ''))
            razon_item.setForeground(QColor('#111827'))
            self.facturas_table.setItem(row, 3, razon_item)
            
            # Fecha
            fecha_item = QTableWidgetItem(factura.get('fecha_emision', ''))
            fecha_item.setForeground(QColor('#111827'))
            self.facturas_table.setItem(row, 4, fecha_item)
            
            # Total
            total = factura.get('total', 0)
            total_item = QTableWidgetItem(f"DOP {total:,.2f}")
            total_item.setForeground(QColor('#111827'))
            font_total = total_item.font()
            font_total.setWeight(QFont.Weight.Bold)
            total_item.setFont(font_total)
            self.facturas_table.setItem(row, 5, total_item)
        
        self._update_summary()
    
    def _on_select_all(self, state):
        """Handle select all"""
        for row in range(self.facturas_table.rowCount()):
            chk_widget = self.facturas_table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk:
                    chk.setChecked(state == Qt.CheckState.Checked.value)
    
    def _on_search_facturas(self, text):
        """Handle search"""
        search = text.lower()
        for row in range(self.facturas_table.rowCount()):
            ncf_item = self.facturas_table.item(row, 1)
            if ncf_item:
                show = search in ncf_item.text().lower()
                self.facturas_table.setRowHidden(row, not show and len(search) > 0)
    
    def _update_summary(self):
        """Update summary"""
        count = 0
        total = 0.0
        
        for row in range(self.facturas_table.rowCount()):
            chk_widget = self.facturas_table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk and chk.isChecked():
                    count += 1
                    # Get total from table
                    total_item = self.facturas_table.item(row, 5)
                    if total_item:
                        total_text = total_item.text().replace('DOP', '').replace(',', '').strip()
                        try:
                            total += float(total_text)
                        except:
                            pass
        
        self.lbl_count.setText(f"Facturas seleccionadas: {count}")
        self.lbl_total.setText(f"Total monto: DOP {total:,.2f}")
        
        self.btn_export.setEnabled(count > 0)
    
    def _on_export(self):
        """Handle export"""
        # Get selected facturas
        selected = []
        for row in range(self.facturas_table.rowCount()):
            chk_widget = self.facturas_table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk and chk.isChecked():
                    factura_id = chk.property('factura_id')
                    factura = next((f for f in self.facturas if f['id'] == factura_id), None)
                    if factura:
                        # ✅ Validar que esté revisada
                        if factura.get('estado') != 'revisada':
                            QMessageBox.warning(
                                self,
                                "Factura no revisada",
                                f"La factura {factura.get('ncf', 'N/A')} no está revisada.\n\n"
                                "Solo se pueden exportar facturas revisadas."
                            )
                            return
                        selected.append(factura)
        
        if not selected:
            QMessageBox.warning(self, "Advertencia", "No hay facturas seleccionadas")
            return
        
        
        # Get format
        format_type = 'csv'
        if self.radio_json.isChecked():
            format_type = 'json'
        elif self.radio_both.isChecked():
            format_type = 'both'
        
        # Export
        try:
            empresa_id = self.empresa_combo.currentData()
            result = export_handler.export_facturas(
                facturas=selected,
                empresa_id=empresa_id,
                export_format=format_type
            )
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Facturas exportadas correctamente:\n{result['file_path']}"
            )
            
            # Mark as exported if checkbox is checked
            if self.chk_mark_exported.isChecked():
                for factura in selected:
                    if hasattr(firebase_handler, 'mark_ocr_factura_exportada'):
                        firebase_handler.mark_ocr_factura_exportada(factura['id'])
                    else:
                        firebase_handler.mark_factura_exportada(empresa_id, factura['id'])
            
            self.back_requested.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{str(e)}")