"""
Export screen - Redesigned with compact header and prominent table
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                             QCheckBox, QRadioButton, QButtonGroup, QLineEdit,
                             QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gui.utils import FirebaseWorkerPool
from app.firebase_handler import firebase_handler
from app.export_handler import export_handler


class ExporterScreen(QWidget):
    """Export screen - Redesigned with compact header"""
    
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
        # Main container
        self.setStyleSheet("background-color: #F9FAFB;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header (compact)
        header = self._create_header()
        layout.addWidget(header)
        
        # Table area (main focus)
        table_container = self._create_table_container()
        layout.addWidget(table_container, 1)  # Stretch to fill
    
    def _create_header(self) -> QWidget:
        """Create compact header with all controls"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-bottom: 2px solid #E5E7EB;
            }
        """)
        header.setFixedHeight(140)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(32, 20, 32, 20)
        header_layout.setSpacing(16)
        
        # Row 1: Title + Back button
        row1 = QHBoxLayout()
        
        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #2563EB;
                font-size: 14px;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #EFF6FF;
                border-radius: 6px;
            }
        """)
        btn_back.clicked.connect(self.back_requested.emit)
        row1.addWidget(btn_back)
        
        row1.addStretch()
        
        title = QLabel("Exportar Facturas Revisadas")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            background-color: transparent;
        """)
        row1.addWidget(title)
        
        row1.addStretch()
        
        # Export button (icon style)
        self.btn_export = QPushButton("📤")
        self.btn_export.setToolTip("Exportar facturas seleccionadas")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setFixedSize(48, 48)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 24px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
            }
        """)
        self.btn_export.clicked.connect(self._on_export)
        self.btn_export.setEnabled(False)
        row1.addWidget(self.btn_export)
        
        header_layout.addLayout(row1)
        
        # Row 2: Empresa + Format + Summary (compact)
        row2 = QHBoxLayout()
        row2.setSpacing(32)
        
        # Empresa selector (compact)
        empresa_container = QWidget()
        empresa_container.setStyleSheet("background-color: transparent;")
        empresa_layout = QHBoxLayout(empresa_container)
        empresa_layout.setContentsMargins(0, 0, 0, 0)
        empresa_layout.setSpacing(8)
        
        emp_label = QLabel("Empresa:")
        emp_label.setStyleSheet("""
            font-size: 13px;
            color: #6B7280;
            font-weight: 500;
            background-color: transparent;
        """)
        empresa_layout.addWidget(emp_label)
        
        self.empresa_combo = QComboBox()
        self.empresa_combo.setMinimumWidth(220)
        self.empresa_combo.setFixedHeight(36)
        self.empresa_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px 12px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #111827;
            }
            QComboBox:hover {
                border-color: #9CA3AF;
            }
            QComboBox:disabled {
                background-color: #F3F4F6;
                color: #6B7280;
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
        self.empresa_combo.currentIndexChanged.connect(self._on_empresa_changed)
        empresa_layout.addWidget(self.empresa_combo)
        
        row2.addWidget(empresa_container)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("background-color: #E5E7EB;")
        sep1.setFixedWidth(1)
        row2.addWidget(sep1)
        
        # Format selector (compact)
        format_container = QWidget()
        format_container.setStyleSheet("background-color: transparent;")
        format_layout = QHBoxLayout(format_container)
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.setSpacing(12)
        
        fmt_label = QLabel("Formato:")
        fmt_label.setStyleSheet("""
            font-size: 13px;
            color: #6B7280;
            font-weight: 500;
            background-color: transparent;
        """)
        format_layout.addWidget(fmt_label)
        
        self.format_group = QButtonGroup()
        
        self.radio_csv = QRadioButton("CSV")
        self.radio_csv.setChecked(True)
        self.radio_csv.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                color: #111827;
                background-color: transparent;
            }
        """)
        self.format_group.addButton(self.radio_csv)
        format_layout.addWidget(self.radio_csv)
        
        self.radio_json = QRadioButton("JSON")
        self.radio_json.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                color: #111827;
                background-color: transparent;
            }
        """)
        self.format_group.addButton(self.radio_json)
        format_layout.addWidget(self.radio_json)
        
        self.radio_both = QRadioButton("Ambos")
        self.radio_both.setStyleSheet("""
            QRadioButton {
                font-size: 13px;
                color: #111827;
                background-color: transparent;
            }
        """)
        self.format_group.addButton(self.radio_both)
        format_layout.addWidget(self.radio_both)
        
        row2.addWidget(format_container)
        
        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet("background-color: #E5E7EB;")
        sep2.setFixedWidth(1)
        row2.addWidget(sep2)
        
        # Summary (compact)
        summary_container = QWidget()
        summary_container.setStyleSheet("background-color: transparent;")
        summary_layout = QVBoxLayout(summary_container)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(2)
        
        self.lbl_count = QLabel("Seleccionadas: 0")
        self.lbl_count.setStyleSheet("""
            font-size: 13px;
            color: #111827;
            font-weight: 600;
            background-color: transparent;
        """)
        summary_layout.addWidget(self.lbl_count)
        
        self.lbl_total = QLabel("Total: DOP 0.00")
        self.lbl_total.setStyleSheet("""
            font-size: 13px;
            color: #2563EB;
            font-weight: 700;
            background-color: transparent;
        """)
        summary_layout.addWidget(self.lbl_total)
        
        row2.addWidget(summary_container)
        
        row2.addStretch()
        
        # Mark as exported checkbox
        self.chk_mark_exported = QCheckBox("Marcar como exportadas")
        self.chk_mark_exported.setChecked(True)
        self.chk_mark_exported.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #374151;
                background-color: transparent;
            }
        """)
        row2.addWidget(self.chk_mark_exported)
        
        header_layout.addLayout(row2)
        
        return header
    
    def _create_table_container(self) -> QWidget:
        """Create main table container"""
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)
        
        # Info banner
        info_banner = QLabel("✓ Solo facturas REVISADAS (listas para exportar)")
        info_banner.setStyleSheet("""
            background-color: #D1FAE5;
            color: #065F46;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            border: 1px solid #10B981;
        """)
        layout.addWidget(info_banner)
        
        # Search + Select All
        controls_layout = QHBoxLayout()
        
        self.chk_select_all = QCheckBox("Seleccionar Todas")
        self.chk_select_all.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #111827;
                font-weight: 600;
            }
        """)
        self.chk_select_all.stateChanged.connect(self._on_select_all)
        controls_layout.addWidget(self.chk_select_all)
        
        controls_layout.addStretch()
        
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Buscar por NCF, RNC o Razón Social...")
        search_box.setMinimumWidth(320)
        search_box.setFixedHeight(40)
        search_box.setStyleSheet("""
            QLineEdit {
                padding: 10px 16px;
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
        self.facturas_table.setColumnCount(8)  # ✅ 8 columnas (agregamos TOTAL)
        self.facturas_table.setHorizontalHeaderLabels([
            '☑', 'NCF', 'RNC', 'RAZÓN SOCIAL', 'FECHA', 'SUBTOTAL', 'ITBIS', 'TOTAL'
        ])
        self.facturas_table.verticalHeader().setVisible(False)
        self.facturas_table.setAlternatingRowColors(True)
        self.facturas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.facturas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.facturas_table.verticalHeader().setDefaultSectionSize(52)
        
        # Headers
        header = self.facturas_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        self.facturas_table.setColumnWidth(0, 60)
        
        # Styles
        self.facturas_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                gridline-color: #F3F4F6;
            }
            QTableWidget::item {
                padding: 12px;
                color: #111827;
                font-size: 14px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #374151;
                padding: 14px 12px;
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
        
        return container
    
    def load_empresas(self):
        """Load empresas"""
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=self._on_empresas_loaded,
            on_error=lambda e: QMessageBox.critical(self, "Error", str(e))
        )
    
    def load_for_empresa(self, empresa_id: str):
        """Load exporter in automatic mode for specific empresa"""
        self.worker_pool.execute(
            firebase_handler.get_empresas,
            on_success=lambda empresas: self._on_empresas_loaded_auto(empresas, empresa_id),
            on_error=lambda e: QMessageBox.critical(self, "Error", str(e))
        )
    
    def _on_empresas_loaded(self, empresas):
        """Handle empresas loaded"""
        self.empresas = empresas
        self.empresa_combo.clear()
        for emp in empresas:
            self.empresa_combo.addItem(emp['nombre'], emp['id'])
    
    def _on_empresas_loaded_auto(self, empresas, empresa_id: str):
        """Handle empresas loaded in auto mode"""
        self.empresas = empresas
        self.empresa_combo.clear()
        
        for emp in empresas:
            self.empresa_combo.addItem(emp['nombre'], emp['id'])
        
        # ✅ Pre-select empresa pero NO bloquear (permitir cambiar)
        for i in range(self.empresa_combo.count()):
            if self.empresa_combo.itemData(i) == empresa_id:
                self.empresa_combo.setCurrentIndex(i)
                break
        
        # ✅ NO DESHABILITAR - permitir cambio de empresa
        # self.empresa_combo.setEnabled(False)  ← ELIMINAR ESTA LÍNEA
    
    def set_empresa(self, empresa_id: str):
        """Pre-select empresa"""
        for i in range(self.empresa_combo.count()):
            if self.empresa_combo.itemData(i) == empresa_id:
                self.empresa_combo.setCurrentIndex(i)
                break
    
    def _on_empresa_changed(self, index):
        """Handle empresa changed"""
        if index < 0:
            return
        
        empresa_id = self.empresa_combo.currentData()
        if empresa_id:
            self._load_facturas(empresa_id)
    
    def _load_facturas(self, empresa_id):
        """Load facturas for empresa - ONLY REVIEWED"""
        if hasattr(firebase_handler, 'get_ocr_facturas_by_empresa'):
            fetch_func = lambda: firebase_handler.get_ocr_facturas_by_empresa(
                empresa_id, 
                estado='revisada'
            )
        else:
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
            
            # Subtotal
            subtotal = float(factura.get('subtotal', 0))
            subtotal_item = QTableWidgetItem(f"DOP {subtotal:,.2f}")
            subtotal_item.setForeground(QColor('#6B7280'))
            subtotal_item.setData(Qt.ItemDataRole.UserRole, subtotal)  # ✅ Guardar valor numérico
            self.facturas_table.setItem(row, 5, subtotal_item)
            
            # ITBIS
            itbis = float(factura.get('itbis', 0))
            itbis_item = QTableWidgetItem(f"DOP {itbis:,.2f}")
            itbis_item.setForeground(QColor('#EA580C'))
            itbis_item.setData(Qt.ItemDataRole.UserRole, itbis)  # ✅ Guardar valor numérico
            self.facturas_table.setItem(row, 6, itbis_item)
            
            # ✅ TOTAL (columna 7)
            total = float(factura.get('total', 0))
            total_item = QTableWidgetItem(f"DOP {total:,.2f}")
            total_item.setForeground(QColor('#111827'))
            total_item.setData(Qt.ItemDataRole.UserRole, total)  # ✅ Guardar valor numérico
            font_total = total_item.font()
            font_total.setWeight(QFont.Weight.Bold)
            total_item.setFont(font_total)
            self.facturas_table.setItem(row, 7, total_item)
        
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
            rnc_item = self.facturas_table.item(row, 2)
            razon_item = self.facturas_table.item(row, 3)
            
            show = False
            if ncf_item and search in ncf_item.text().lower():
                show = True
            elif rnc_item and search in rnc_item.text().lower():
                show = True
            elif razon_item and search in razon_item.text().lower():
                show = True
            
            if not search:
                show = True
            
            self.facturas_table.setRowHidden(row, not show)
    
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
                    # ✅ Obtener total de la columna 7 (usando UserRole)
                    total_item = self.facturas_table.item(row, 7)
                    if total_item:
                        # Usar el valor numérico guardado
                        total_value = total_item.data(Qt.ItemDataRole.UserRole)
                        if total_value is not None:
                            total += float(total_value)
        
        self.lbl_count.setText(f"Seleccionadas: {count}")
        self.lbl_total.setText(f"Total: DOP {total:,.2f}")
        
        self.btn_export.setEnabled(count > 0)
    
    def _on_export(self):
        """Handle export"""
        selected = []
        for row in range(self.facturas_table.rowCount()):
            chk_widget = self.facturas_table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk and chk.isChecked():
                    factura_id = chk.property('factura_id')
                    factura = next((f for f in self.facturas if f['id'] == factura_id), None)
                    if factura:
                        if factura.get('estado') != 'revisada':
                            QMessageBox.warning(
                                self,
                                "Factura no revisada",
                                f"La factura {factura.get('ncf', 'N/A')} no está revisada."
                            )
                            return
                        selected.append(factura)
        
        if not selected:
            QMessageBox.warning(self, "Advertencia", "No hay facturas seleccionadas")
            return
        
        format_type = 'csv'
        if self.radio_json.isChecked():
            format_type = 'json'
        elif self.radio_both.isChecked():
            format_type = 'both'
        
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
                f"✓ {len(selected)} facturas exportadas correctamente\n\n"
                f"Archivo: {result['file_path']}"
            )
            
            if self.chk_mark_exported.isChecked():
                for factura in selected:
                    if hasattr(firebase_handler, 'mark_ocr_factura_exportada'):
                        firebase_handler.mark_ocr_factura_exportada(factura['id'])
                    else:
                        firebase_handler.mark_factura_exportada(empresa_id, factura['id'])
            
            self.back_requested.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{str(e)}")