"""
Diálogo de Configuración para LECTOR-NCF.
Permite configurar Firebase, Google Cloud, Twilio y rutas de la aplicación.
"""

import os
import json
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QGroupBox, QTabWidget,
    QFormLayout, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.utils.config_manager import config_manager


class ConfigDialog(QDialog):
    """
    Diálogo para configurar credenciales y parámetros de LECTOR-NCF.
    
    Secciones:
    - Firebase (Firestore + Storage)
    - Google Cloud Vision (OCR)
    - Twilio (WhatsApp)
    - Rutas de la aplicación
    """
    
    def __init__(self, parent=None, first_time=False):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuración de LECTOR-NCF")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        self.first_time = first_time
        
        self._init_ui()
        self._load_existing_config()
    
    def _init_ui(self):
        """Construye la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("⚙️ Configuración de LECTOR-NCF")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Descripción
        if self.first_time:
            desc = QLabel(
                "⚠️ Primera ejecución detectada.\n\n"
                "Configura las credenciales necesarias para usar LECTOR-NCF.\n"
                "Puedes modificar esta configuración después desde el menú 'Configuración'."
            )
            desc.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            desc = QLabel(
                "Actualiza las credenciales y configuración de la aplicación."
            )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_firebase_tab(), "🔥 Firebase")
        self.tabs.addTab(self._create_google_cloud_tab(), "☁️ Google Cloud")
        self.tabs.addTab(self._create_twilio_tab(), "📱 Twilio WhatsApp")
        self.tabs.addTab(self._create_app_tab(), "📁 Rutas de App")
        layout.addWidget(self.tabs)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if not self.first_time:
            btn_cancel = QPushButton("❌ Cancelar")
            btn_cancel.clicked.connect(self.reject)
            btn_layout.addWidget(btn_cancel)
        
        btn_test = QPushButton("🔍 Validar Credenciales")
        btn_test.clicked.connect(self._test_all_credentials)
        btn_layout.addWidget(btn_test)
        
        btn_save = QPushButton("💾 Guardar y Aplicar")
        btn_save.clicked.connect(self._save_and_accept)
        btn_save.setDefault(True)
        btn_save.setProperty("class", "primary")
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def _create_firebase_tab(self) -> QWidget:
        """Crea el tab de configuración de Firebase."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Credenciales
        cred_group = QGroupBox("Credenciales de Firebase")
        cred_layout = QFormLayout()
        
        # Archivo de credenciales
        cred_row = QHBoxLayout()
        self.firebase_cred_edit = QLineEdit()
        self.firebase_cred_edit.setPlaceholderText("Selecciona firebase-credentials.json")
        self.firebase_cred_edit.setReadOnly(True)
        cred_row.addWidget(self.firebase_cred_edit)
        
        btn_browse_firebase = QPushButton("📂 Seleccionar")
        btn_browse_firebase.clicked.connect(self._browse_firebase_credentials)
        cred_row.addWidget(btn_browse_firebase)
        
        cred_layout.addRow("Archivo de credenciales:", cred_row)
        
        # Project ID (readonly, auto-detectado)
        self.firebase_project_id_edit = QLineEdit()
        self.firebase_project_id_edit.setReadOnly(True)
        self.firebase_project_id_edit.setPlaceholderText("Auto-detectado del JSON")
        self.firebase_project_id_edit.setStyleSheet("background-color: #f0f0f0;")
        cred_layout.addRow("Project ID:", self.firebase_project_id_edit)
        
        # Database URL
        self.firebase_db_url_edit = QLineEdit()
        self.firebase_db_url_edit.setPlaceholderText("https://tu-proyecto-default-rtdb.firebaseio.com/")
        cred_layout.addRow("Database URL:", self.firebase_db_url_edit)
        
        # Storage Bucket
        self.firebase_bucket_edit = QLineEdit()
        self.firebase_bucket_edit.setPlaceholderText("tu-proyecto.firebasestorage.app")
        cred_layout.addRow("Storage Bucket:", self.firebase_bucket_edit)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Hint
        hint = QLabel(
            "💡 El Project ID, Database URL y Storage Bucket se detectan automáticamente\n"
            "al seleccionar el archivo de credenciales. Puedes modificarlos si es necesario."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(hint)
        
        layout.addStretch()
        return widget
    
    def _create_google_cloud_tab(self) -> QWidget:
        """Crea el tab de configuración de Google Cloud Vision."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Credenciales de Google Cloud Vision API")
        group_layout = QFormLayout()
        
        # Archivo de credenciales
        cred_row = QHBoxLayout()
        self.google_cloud_cred_edit = QLineEdit()
        self.google_cloud_cred_edit.setPlaceholderText("Selecciona google-cloud-credentials.json")
        self.google_cloud_cred_edit.setReadOnly(True)
        cred_row.addWidget(self.google_cloud_cred_edit)
        
        btn_browse_gc = QPushButton("📂 Seleccionar")
        btn_browse_gc.clicked.connect(self._browse_google_cloud_credentials)
        cred_row.addWidget(btn_browse_gc)
        
        group_layout.addRow("Archivo de credenciales:", cred_row)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Hint
        hint = QLabel(
            "💡 Estas credenciales se usan para el servicio de OCR (Google Cloud Vision API).\n"
            "Puedes usar el mismo archivo de Firebase si tiene los permisos necesarios."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(hint)
        
        # Botón para usar las mismas de Firebase
        btn_use_firebase = QPushButton("🔗 Usar credenciales de Firebase")
        btn_use_firebase.clicked.connect(self._use_firebase_credentials_for_gc)
        layout.addWidget(btn_use_firebase)
        
        layout.addStretch()
        return widget
    
    def _create_twilio_tab(self) -> QWidget:
        """Crea el tab de configuración de Twilio WhatsApp."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Credenciales de Twilio WhatsApp API")
        group_layout = QFormLayout()
        
        # Account SID
        self.twilio_sid_edit = QLineEdit()
        self.twilio_sid_edit.setPlaceholderText("ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        group_layout.addRow("Account SID:", self.twilio_sid_edit)
        
        # Auth Token (campo password)
        self.twilio_token_edit = QLineEdit()
        self.twilio_token_edit.setPlaceholderText("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.twilio_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        group_layout.addRow("Auth Token:", self.twilio_token_edit)
        
        # Checkbox para mostrar/ocultar token
        self.show_token_checkbox = QCheckBox("Mostrar Auth Token")
        self.show_token_checkbox.stateChanged.connect(self._toggle_token_visibility)
        group_layout.addRow("", self.show_token_checkbox)
        
        # WhatsApp Number
        self.twilio_number_edit = QLineEdit()
        self.twilio_number_edit.setPlaceholderText("whatsapp:+14155238886")
        group_layout.addRow("WhatsApp Number:", self.twilio_number_edit)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Hint
        hint = QLabel(
            "💡 Obtén estas credenciales desde tu cuenta de Twilio:\n"
            "Console > Account Info > Account SID y Auth Token\n"
            "Messaging > WhatsApp > Senders\n\n"
            "⚠️ Estos campos son opcionales. Solo configúralos si usas WhatsApp."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(hint)
        
        layout.addStretch()
        return widget
    
    def _create_app_tab(self) -> QWidget:
        """Crea el tab de configuración de rutas de la aplicación."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("Rutas de Almacenamiento")
        group_layout = QFormLayout()
        
        # Data folder
        self.data_folder_edit = QLineEdit()
        self.data_folder_edit.setPlaceholderText("./data")
        group_layout.addRow("Carpeta de datos:", self.data_folder_edit)
        
        # Export folder
        self.export_folder_edit = QLineEdit()
        self.export_folder_edit.setPlaceholderText("./data/exports")
        group_layout.addRow("Carpeta de exportaciones:", self.export_folder_edit)
        
        # Temp folder
        self.temp_folder_edit = QLineEdit()
        self.temp_folder_edit.setPlaceholderText("./data/temp")
        group_layout.addRow("Carpeta temporal:", self.temp_folder_edit)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Hint
        hint = QLabel(
            "💡 Estas rutas se usan para almacenar archivos de la aplicación.\n"
            "Se crearán automáticamente si no existen.\n"
            "Puedes usar rutas relativas (./data) o absolutas (D:/datos)."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(hint)
        
        layout.addStretch()
        return widget
    
    def _load_existing_config(self):
        """Carga la configuración existente en los campos."""
        # Firebase
        self.firebase_cred_edit.setText(config_manager.get_firebase_credentials_path())
        self.firebase_db_url_edit.setText(config_manager.get_firebase_database_url())
        self.firebase_bucket_edit.setText(config_manager.get_firebase_storage_bucket())
        self.firebase_project_id_edit.setText(config_manager.get_firebase_project_id())
        
        # Google Cloud
        self.google_cloud_cred_edit.setText(config_manager.get_google_cloud_credentials_path())
        
        # Twilio
        self.twilio_sid_edit.setText(config_manager.get_twilio_account_sid())
        self.twilio_token_edit.setText(config_manager.get_twilio_auth_token())
        self.twilio_number_edit.setText(config_manager.get_twilio_whatsapp_number())
        
        # App paths
        self.data_folder_edit.setText(config_manager.get_data_folder())
        self.export_folder_edit.setText(config_manager.get_export_folder())
        self.temp_folder_edit.setText(config_manager.get_temp_folder())
    
    def _browse_firebase_credentials(self):
        """Selecciona archivo de credenciales de Firebase."""
        start_dir = os.path.expanduser("~")
        current_path = self.firebase_cred_edit.text()
        if current_path and os.path.exists(os.path.dirname(current_path)):
            start_dir = os.path.dirname(current_path)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar credenciales de Firebase",
            start_dir,
            "Archivos JSON (*.json);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self.firebase_cred_edit.setText(file_path)
            self._auto_detect_firebase_info(file_path)
    
    def _auto_detect_firebase_info(self, file_path: str):
        """Auto-detecta Project ID y sugiere URLs basadas en credenciales."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cred_data = json.load(f)
                project_id = cred_data.get('project_id', '')
                
                if project_id:
                    self.firebase_project_id_edit.setText(project_id)
                    
                    # Sugerir URLs si están vacías
                    if not self.firebase_db_url_edit.text():
                        self.firebase_db_url_edit.setText(f"https://{project_id}-default-rtdb.firebaseio.com/")
                    
                    if not self.firebase_bucket_edit.text():
                        self.firebase_bucket_edit.setText(f"{project_id}.firebasestorage.app")
                    
                    QMessageBox.information(
                        self,
                        "✓ Credenciales detectadas",
                        f"Project ID: {project_id}\n\n"
                        "Las URLs se han completado automáticamente."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "No se pudo detectar el Project ID del archivo JSON."
                    )
        except json.JSONDecodeError:
            QMessageBox.warning(
                self,
                "Error",
                "El archivo seleccionado no es un JSON válido."
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error leyendo credenciales:\n{str(e)}")
    
    def _browse_google_cloud_credentials(self):
        """Selecciona archivo de credenciales de Google Cloud."""
        start_dir = os.path.expanduser("~")
        current_path = self.google_cloud_cred_edit.text()
        if current_path and os.path.exists(os.path.dirname(current_path)):
            start_dir = os.path.dirname(current_path)
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar credenciales de Google Cloud",
            start_dir,
            "Archivos JSON (*.json);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self.google_cloud_cred_edit.setText(file_path)
    
    def _use_firebase_credentials_for_gc(self):
        """Copia las credenciales de Firebase para Google Cloud."""
        firebase_path = self.firebase_cred_edit.text()
        if firebase_path:
            self.google_cloud_cred_edit.setText(firebase_path)
            QMessageBox.information(
                self,
                "✓ Credenciales copiadas",
                "Se usarán las mismas credenciales de Firebase para Google Cloud."
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Primero selecciona las credenciales de Firebase."
            )
    
    def _toggle_token_visibility(self, state):
        """Muestra u oculta el Auth Token."""
        if state == Qt.CheckState.Checked.value:
            self.twilio_token_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.twilio_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _test_all_credentials(self):
        """Valida todas las credenciales configuradas."""
        errors = []
        warnings = []
        
        # Validar Firebase (OBLIGATORIO)
        firebase_cred = self.firebase_cred_edit.text().strip()
        if not firebase_cred:
            errors.append("❌ Falta archivo de credenciales de Firebase")
        elif not os.path.exists(firebase_cred):
            errors.append("❌ El archivo de credenciales de Firebase no existe")
        else:
            # Validar que sea JSON válido
            try:
                with open(firebase_cred, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not data.get('project_id'):
                        errors.append("❌ El JSON de Firebase no tiene 'project_id'")
            except:
                errors.append("❌ El archivo de Firebase no es un JSON válido")
        
        if not self.firebase_db_url_edit.text().strip():
            errors.append("❌ Database URL de Firebase vacía")
        
        # Validar Google Cloud (OBLIGATORIO)
        gc_cred = self.google_cloud_cred_edit.text().strip()
        if not gc_cred:
            warnings.append("⚠️ No se configuraron credenciales de Google Cloud (se usarán las de Firebase)")
        elif not os.path.exists(gc_cred):
            errors.append("❌ El archivo de credenciales de Google Cloud no existe")
        
        # Validar Twilio (OPCIONAL)
        twilio_sid = self.twilio_sid_edit.text().strip()
        twilio_token = self.twilio_token_edit.text().strip()
        
        if twilio_sid and not twilio_token:
            warnings.append("⚠️ Twilio SID configurado pero falta Auth Token")
        elif twilio_token and not twilio_sid:
            warnings.append("⚠️ Twilio Auth Token configurado pero falta SID")
        
        # Mostrar resultados
        if errors:
            QMessageBox.critical(
                self,
                "❌ Errores de validación",
                "Se encontraron los siguientes errores:\n\n" + "\n".join(errors)
            )
        elif warnings:
            QMessageBox.warning(
                self,
                "⚠️ Advertencias",
                "\n".join(warnings) + "\n\nPuedes continuar pero algunas funciones pueden no estar disponibles."
            )
        else:
            QMessageBox.information(
                self,
                "✓ Validación exitosa",
                "Todas las credenciales están correctas.\n\n"
                "Haz clic en 'Guardar y Aplicar' para usar esta configuración."
            )
    
    def _save_and_accept(self):
        """Guarda la configuración y cierra el diálogo."""
        # Validar campos OBLIGATORIOS
        firebase_cred = self.firebase_cred_edit.text().strip()
        firebase_db_url = self.firebase_db_url_edit.text().strip()
        
        if not firebase_cred:
            QMessageBox.warning(self, "Error", "Selecciona las credenciales de Firebase.")
            self.tabs.setCurrentIndex(0)  # Ir al tab de Firebase
            return
        
        if not os.path.exists(firebase_cred):
            QMessageBox.warning(self, "Error", "El archivo de credenciales de Firebase no existe.")
            self.tabs.setCurrentIndex(0)
            return
        
        if not firebase_db_url:
            QMessageBox.warning(self, "Error", "Ingresa la Database URL de Firebase.")
            self.tabs.setCurrentIndex(0)
            return
        
        # Actualizar config
        config_manager.update_firebase_config(
            firebase_cred,
            self.firebase_project_id_edit.text().strip(),
            firebase_db_url,
            self.firebase_bucket_edit.text().strip()
        )
        
        # Google Cloud (usar Firebase si está vacío)
        gc_cred = self.google_cloud_cred_edit.text().strip()
        if not gc_cred:
            gc_cred = firebase_cred
        config_manager.update_google_cloud_config(gc_cred)
        
        # Twilio (opcional)
        config_manager.update_twilio_config(
            self.twilio_sid_edit.text().strip(),
            self.twilio_token_edit.text().strip(),
            self.twilio_number_edit.text().strip()
        )
        
        # Rutas de app
        config_manager.update_app_config(
            self.data_folder_edit.text().strip() or "./data",
            self.export_folder_edit.text().strip() or "./data/exports",
            self.temp_folder_edit.text().strip() or "./data/temp"
        )
        
        # Guardar
        if config_manager.save():
            QMessageBox.information(
                self,
                "✓ Configuración guardada",
                f"La configuración se guardó correctamente en:\n{config_manager.config_path.absolute()}\n\n"
                "Los cambios se aplicarán inmediatamente."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo guardar la configuración. Verifica los permisos del archivo."
            )