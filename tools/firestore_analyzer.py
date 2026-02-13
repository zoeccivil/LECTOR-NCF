"""
FIRESTORE ANALYZER - Herramienta de Auditoría y Análisis
Analiza la estructura completa de Firestore y genera recomendaciones.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar,
    QGroupBox, QFormLayout, QMessageBox, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Imports de Firebase
import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreAnalyzerWorker(QThread):
    """Worker thread para analizar Firestore sin bloquear la UI."""
    
    progress = pyqtSignal(int, str)  # (porcentaje, mensaje)
    finished = pyqtSignal(dict)  # Resultado del análisis
    error = pyqtSignal(str)
    
    def __init__(self, cred_path: str):
        super().__init__()
        self.cred_path = cred_path
        self.db = None
    
    def run(self):
        """Ejecuta el análisis completo."""
        try:
            # Inicializar Firebase
            self.progress.emit(10, "Inicializando Firebase...")
            
            # Cerrar app existente si hay
            try:
                firebase_admin.delete_app(firebase_admin.get_app())
            except:
                pass
            
            cred = credentials.Certificate(self.cred_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            
            self.progress.emit(20, "Conexión establecida. Escaneando colecciones...")
            
            # Analizar estructura
            analysis = self.analyze_firestore()
            
            self.progress.emit(100, "Análisis completado")
            self.finished.emit(analysis)
            
        except Exception as e:
            self.error.emit(f"Error durante el análisis: {str(e)}")
    
    def analyze_firestore(self) -> Dict[str, Any]:
        """Analiza la estructura completa de Firestore."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "credential_path": self.cred_path,
            "collections": {},
            "statistics": {
                "total_collections": 0,
                "total_documents": 0,
                "total_subcollections": 0
            },
            "schema": {},
            "recommendations": []
        }
        
        # Obtener todas las colecciones raíz
        self.progress.emit(30, "Obteniendo colecciones raíz...")
        collections = self.db.collections()
        
        collection_list = list(collections)
        result["statistics"]["total_collections"] = len(collection_list)
        
        # Analizar cada colección
        for idx, collection in enumerate(collection_list):
            collection_name = collection.id
            progress = 30 + int((idx / len(collection_list)) * 60)
            self.progress.emit(progress, f"Analizando colección: {collection_name}")
            
            collection_data = self.analyze_collection(collection)
            result["collections"][collection_name] = collection_data
            result["statistics"]["total_documents"] += collection_data["document_count"]
        
        # Generar esquema
        self.progress.emit(90, "Generando esquema de datos...")
        result["schema"] = self.generate_schema(result["collections"])
        
        # Generar recomendaciones
        self.progress.emit(95, "Generando recomendaciones...")
        result["recommendations"] = self.generate_recommendations(result)
        
        return result
    
    def analyze_collection(self, collection) -> Dict[str, Any]:
        """Analiza una colección específica."""
        data = {
            "name": collection.id,
            "document_count": 0,
            "sample_documents": [],
            "field_types": {},
            "subcollections": {}
        }
        
        # Obtener todos los documentos
        docs = collection.stream()
        
        for idx, doc in enumerate(docs):
            data["document_count"] += 1
            doc_data = doc.to_dict()
            
            # Guardar primeros 5 docs como sample
            if idx < 5:
                data["sample_documents"].append({
                    "id": doc.id,
                    "data": doc_data
                })
            
            # Analizar tipos de campos
            for field, value in doc_data.items():
                field_type = type(value).__name__
                if field not in data["field_types"]:
                    data["field_types"][field] = {}
                
                if field_type not in data["field_types"][field]:
                    data["field_types"][field][field_type] = 0
                
                data["field_types"][field][field_type] += 1
            
            # Analizar subcolecciones (solo del primer doc)
            if idx == 0:
                subcollections = doc.reference.collections()
                for subcol in subcollections:
                    subcol_data = self.analyze_collection(subcol)
                    data["subcollections"][subcol.id] = subcol_data
        
        return data
    
    def generate_schema(self, collections: Dict) -> Dict[str, Any]:
        """Genera un esquema legible de la estructura."""
        schema = {}
        
        for col_name, col_data in collections.items():
            schema[col_name] = {
                "document_count": col_data["document_count"],
                "fields": {}
            }
            
            # Determinar tipo más común para cada campo
            for field, types in col_data["field_types"].items():
                most_common_type = max(types, key=types.get)
                schema[col_name]["fields"][field] = {
                    "type": most_common_type,
                    "occurrences": sum(types.values())
                }
            
            # Agregar subcolecciones
            if col_data["subcollections"]:
                schema[col_name]["subcollections"] = {}
                for subcol_name, subcol_data in col_data["subcollections"].items():
                    schema[col_name]["subcollections"][subcol_name] = {
                        "document_count": subcol_data["document_count"],
                        "fields": {
                            field: {
                                "type": max(types, key=types.get),
                                "occurrences": sum(types.values())
                            }
                            for field, types in subcol_data["field_types"].items()
                        }
                    }
        
        return schema
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        # Verificar estructura esperada para LECTOR-NCF
        if "empresas" in analysis["collections"]:
            empresas = analysis["collections"]["empresas"]
            recommendations.append(
                f"✅ Colección 'empresas' encontrada ({empresas['document_count']} documentos)"
            )
        else:
            recommendations.append(
                "⚠️ No se encontró colección 'empresas'. Necesitarás crearla para usar LECTOR-NCF."
            )
        
        if "facturas" in analysis["collections"]:
            facturas = analysis["collections"]["facturas"]
            recommendations.append(
                f"✅ Colección 'facturas' encontrada ({facturas['document_count']} documentos)"
            )
            
            # Verificar subcolecciones
            if facturas.get("subcollections"):
                recommendations.append(
                    f"📁 Facturas tiene {len(facturas['subcollections'])} subcolecciones"
                )
        else:
            recommendations.append(
                "⚠️ No se encontró colección 'facturas'. Esta es la colección principal del sistema."
            )
        
        # Analizar campos de facturas
        if "facturas" in analysis["schema"]:
            factura_fields = analysis["schema"]["facturas"]["fields"]
            required_fields = ["ncf", "rnc", "total", "fecha_emision"]
            
            for field in required_fields:
                if field in factura_fields:
                    recommendations.append(f"✅ Campo requerido '{field}' presente")
                else:
                    recommendations.append(f"❌ Campo requerido '{field}' FALTA")
        
        # Estadísticas generales
        stats = analysis["statistics"]
        recommendations.append(
            f"\n📊 RESUMEN:\n"
            f"   - Colecciones: {stats['total_collections']}\n"
            f"   - Documentos totales: {stats['total_documents']}"
        )
        
        return recommendations


class FirestoreAnalyzerGUI(QMainWindow):
    """Interfaz gráfica del analizador de Firestore."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 Firestore Analyzer - LECTOR-NCF")
        self.setMinimumSize(1200, 800)
        
        self.cred_path = ""
        self.analysis_result = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Construye la interfaz."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("🔍 Firestore Analyzer")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        desc = QLabel(
            "Analiza la estructura completa de tu proyecto Firebase Firestore\n"
            "y obtén recomendaciones para migrar a LECTOR-NCF"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #757575; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Selector de credenciales
        cred_group = QGroupBox("1. Seleccionar Credenciales")
        cred_layout = QHBoxLayout()
        
        self.cred_label = QLabel("No seleccionado")
        self.cred_label.setStyleSheet("color: #999;")
        cred_layout.addWidget(self.cred_label)
        
        btn_select = QPushButton("📂 Seleccionar JSON")
        btn_select.clicked.connect(self._select_credentials)
        cred_layout.addWidget(btn_select)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Botón analizar
        self.btn_analyze = QPushButton("🔍 ANALIZAR FIRESTORE")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setMinimumHeight(50)
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.btn_analyze.clicked.connect(self._start_analysis)
        layout.addWidget(self.btn_analyze)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Tabs de resultados
        self.result_tabs = QTabWidget()
        self.result_tabs.setVisible(False)
        
        # Tab 1: Resumen
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.result_tabs.addTab(self.summary_text, "📊 Resumen")
        
        # Tab 2: Estructura en árbol
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Colección/Documento", "Detalles"])
        self.result_tabs.addTab(self.tree_widget, "🌲 Estructura")
        
        # Tab 3: Esquema JSON
        self.schema_text = QTextEdit()
        self.schema_text.setReadOnly(True)
        self.schema_text.setStyleSheet("font-family: 'Courier New'; font-size: 11px;")
        self.result_tabs.addTab(self.schema_text, "📋 Esquema JSON")
        
        # Tab 4: Recomendaciones
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.result_tabs.addTab(self.recommendations_text, "💡 Recomendaciones")
        
        layout.addWidget(self.result_tabs)
        
        # Botones de exportación
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.btn_export_json = QPushButton("💾 Exportar Análisis (JSON)")
        self.btn_export_json.setVisible(False)
        self.btn_export_json.clicked.connect(self._export_json)
        export_layout.addWidget(self.btn_export_json)
        
        self.btn_export_report = QPushButton("📄 Exportar Reporte (TXT)")
        self.btn_export_report.setVisible(False)
        self.btn_export_report.clicked.connect(self._export_report)
        export_layout.addWidget(self.btn_export_report)
        
        layout.addLayout(export_layout)
    
    def _select_credentials(self):
        """Selecciona archivo de credenciales."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar credenciales de Firebase",
            os.path.expanduser("~"),
            "Archivos JSON (*.json)"
        )
        
        if file_path:
            self.cred_path = file_path
            self.cred_label.setText(f"✅ {os.path.basename(file_path)}")
            self.cred_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.btn_analyze.setEnabled(True)
    
    def _start_analysis(self):
        """Inicia el análisis en thread separado."""
        self.btn_analyze.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Iniciando análisis...")
        
        # Crear worker thread
        self.worker = FirestoreAnalyzerWorker(self.cred_path)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_analysis_complete)
        self.worker.error.connect(self._on_error)
        self.worker.start()
    
    def _on_progress(self, percent: int, message: str):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)
    
    def _on_analysis_complete(self, result: Dict):
        """Procesa el resultado del análisis."""
        self.analysis_result = result
        
        # Ocultar progress
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Mostrar tabs
        self.result_tabs.setVisible(True)
        self.btn_export_json.setVisible(True)
        self.btn_export_report.setVisible(True)
        
        # Poblar resumen
        self._populate_summary(result)
        
        # Poblar árbol
        self._populate_tree(result)
        
        # Poblar esquema
        self.schema_text.setPlainText(
            json.dumps(result["schema"], indent=2, ensure_ascii=False)
        )
        
        # Poblar recomendaciones
        self.recommendations_text.setPlainText(
            "\n".join(result["recommendations"])
        )
        
        # Re-habilitar botón
        self.btn_analyze.setEnabled(True)
        
        QMessageBox.information(
            self,
            "✅ Análisis completado",
            f"Se analizaron {result['statistics']['total_collections']} colecciones "
            f"con {result['statistics']['total_documents']} documentos totales."
        )
    
    def _populate_summary(self, result: Dict):
        """Puebla el tab de resumen."""
        stats = result["statistics"]
        
        summary = f"""
<h2>📊 Resumen del Análisis</h2>
<p><b>Fecha:</b> {result['timestamp']}</p>
<p><b>Archivo de credenciales:</b> {os.path.basename(result['credential_path'])}</p>

<h3>Estadísticas Generales</h3>
<ul>
<li><b>Colecciones raíz:</b> {stats['total_collections']}</li>
<li><b>Documentos totales:</b> {stats['total_documents']}</li>
</ul>

<h3>Colecciones Encontradas</h3>
<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: #1976D2; color: white;">
<th>Colección</th>
<th>Documentos</th>
<th>Campos</th>
<th>Subcolecciones</th>
</tr>
"""
        
        for col_name, col_data in result["collections"].items():
            summary += f"""
<tr>
<td><b>{col_name}</b></td>
<td>{col_data['document_count']}</td>
<td>{len(col_data['field_types'])}</td>
<td>{len(col_data['subcollections'])}</td>
</tr>
"""
        
        summary += "</table>"
        
        self.summary_text.setHtml(summary)
    
    def _populate_tree(self, result: Dict):
        """Puebla el árbol de estructura."""
        self.tree_widget.clear()
        
        for col_name, col_data in result["collections"].items():
            col_item = QTreeWidgetItem([
                col_name,
                f"{col_data['document_count']} documentos"
            ])
            
            # Agregar campos
            fields_item = QTreeWidgetItem(["📋 Campos", ""])
            for field, types in col_data["field_types"].items():
                type_str = ", ".join([f"{t}({c})" for t, c in types.items()])
                QTreeWidgetItem(fields_item, [field, type_str])
            col_item.addChild(fields_item)
            
            # Agregar subcolecciones
            if col_data["subcollections"]:
                subcol_item = QTreeWidgetItem(["📁 Subcolecciones", ""])
                for subcol_name, subcol_data in col_data["subcollections"].items():
                    sub_item = QTreeWidgetItem([
                        subcol_name,
                        f"{subcol_data['document_count']} documentos"
                    ])
                    subcol_item.addChild(sub_item)
                col_item.addChild(subcol_item)
            
            self.tree_widget.addTopLevelItem(col_item)
        
        self.tree_widget.expandAll()
    
    def _on_error(self, error_msg: str):
        """Maneja errores."""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.btn_analyze.setEnabled(True)
        
        QMessageBox.critical(
            self,
            "Error",
            f"Ocurrió un error durante el análisis:\n\n{error_msg}"
        )
    
    def _export_json(self):
        """Exporta el análisis completo a JSON."""
        if not self.analysis_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar análisis",
            f"firestore_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Archivos JSON (*.json)"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_result, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "✅ Exportado", f"Análisis guardado en:\n{file_path}")
    
    def _export_report(self):
        """Exporta un reporte legible en texto."""
        if not self.analysis_result:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte",
            f"firestore_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Archivos de texto (*.txt)"
        )
        
        if file_path:
            report = f"""
FIRESTORE ANALYSIS REPORT
========================
Generated: {self.analysis_result['timestamp']}
Credentials: {self.analysis_result['credential_path']}

STATISTICS
----------
Collections: {self.analysis_result['statistics']['total_collections']}
Documents: {self.analysis_result['statistics']['total_documents']}

COLLECTIONS
-----------
"""
            
            for col_name, col_data in self.analysis_result["collections"].items():
                report += f"\n📁 {col_name}\n"
                report += f"   Documents: {col_data['document_count']}\n"
                report += f"   Fields:\n"
                for field, types in col_data["field_types"].items():
                    report += f"      - {field}: {types}\n"
            
            report += "\n\nRECOMMENDATIONS\n"
            report += "---------------\n"
            report += "\n".join(self.analysis_result["recommendations"])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            QMessageBox.information(self, "✅ Exportado", f"Reporte guardado en:\n{file_path}")


def main():
    """Entry point."""
    app = QApplication(sys.argv)
    
    # Estilos globales
    app.setStyleSheet("""
        QMainWindow {
            background-color: #F8F9FA;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #E0E0E0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)
    
    window = FirestoreAnalyzerGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()