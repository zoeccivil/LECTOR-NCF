"""
Visual configuration dialog for LECTOR-NCF credentials
"""
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt


class ConfigDialog(QDialog):
    """Configuration dialog with tabs for Firebase, Google Cloud, Twilio, and Paths"""
    
    def __init__(self, parent=None, first_time=False):
        super().__init__(parent)
        self.first_time = first_time
        self.setWindowTitle("⚙️ Configuración de Credenciales" + (" (Requerido)" if first_time else ""))
        self.setMinimumSize(700, 600)
        
        # Load existing config
        from gui.utils.config_manager import config_manager
        self.config_manager = config_manager
        self.config = self.config_manager.config.copy()
        
        self._init_ui()
        self._load_values()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📋 Configuración de Credenciales y Rutas")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Firebase Tab
        firebase_tab = self._create_firebase_tab()
        tabs.addTab(firebase_tab, "🔥 Firebase")
        
        # Google Cloud Tab
        google_tab = self._create_google_cloud_tab()
        tabs.addTab(google_tab, "☁️ Google Cloud")
        
        # Twilio Tab
        twilio_tab = self._create_twilio_tab()
        tabs.addTab(twilio_tab, "📱 Twilio")
        
        # App Paths Tab
        paths_tab = self._create_paths_tab()
        tabs.addTab(paths_tab, "📁 Rutas")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.validate_btn = QPushButton("✅ Validar Credenciales")
        self.validate_btn.clicked.connect(self._validate_credentials)
        button_layout.addWidget(self.validate_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Guardar y Reiniciar" if not self.first_time else "💾 Guardar y Continuar")
        save_btn.clicked.connect(self._save_and_accept)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_firebase_tab(self):
        """Create Firebase configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Credentials group
        cred_group = QGroupBox("Credenciales Firebase")
        cred_layout = QFormLayout()
        
        # Credentials path
        cred_path_layout = QHBoxLayout()
        self.firebase_creds_input = QLineEdit()
        self.firebase_creds_input.setPlaceholderText("Ruta al archivo JSON de credenciales...")
        cred_path_layout.addWidget(self.firebase_creds_input)
        
        browse_creds_btn = QPushButton("📂 Buscar")
        browse_creds_btn.clicked.connect(lambda: self._browse_file(
            self.firebase_creds_input,
            "Seleccionar archivo de credenciales Firebase",
            "JSON files (*.json)"
        ))
        cred_path_layout.addWidget(browse_creds_btn)
        
        cred_layout.addRow("Archivo de credenciales:", cred_path_layout)
        
        # Auto-detect button
        detect_btn = QPushButton("🔍 Auto-detectar Project ID")
        detect_btn.clicked.connect(self._auto_detect_firebase)
        cred_layout.addRow("", detect_btn)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Configuration group
        config_group = QGroupBox("Configuración Firebase")
        config_layout = QFormLayout()
        
        self.firebase_project_id_input = QLineEdit()
        self.firebase_project_id_input.setPlaceholderText("mi-proyecto-firebase")
        config_layout.addRow("Project ID:", self.firebase_project_id_input)
        
        self.firebase_db_url_input = QLineEdit()
        self.firebase_db_url_input.setPlaceholderText("https://mi-proyecto-default-rtdb.firebaseio.com/")
        config_layout.addRow("Database URL:", self.firebase_db_url_input)
        
        self.firebase_storage_input = QLineEdit()
        self.firebase_storage_input.setPlaceholderText("mi-proyecto.appspot.com")
        config_layout.addRow("Storage Bucket:", self.firebase_storage_input)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_google_cloud_tab(self):
        """Create Google Cloud configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Google Cloud Vision")
        form = QFormLayout()
        
        # Credentials path
        cred_path_layout = QHBoxLayout()
        self.google_creds_input = QLineEdit()
        self.google_creds_input.setPlaceholderText("Ruta al archivo JSON de credenciales...")
        cred_path_layout.addWidget(self.google_creds_input)
        
        browse_btn = QPushButton("📂 Buscar")
        browse_btn.clicked.connect(lambda: self._browse_file(
            self.google_creds_input,
            "Seleccionar archivo de credenciales Google Cloud",
            "JSON files (*.json)"
        ))
        cred_path_layout.addWidget(browse_btn)
        
        form.addRow("Archivo de credenciales:", cred_path_layout)
        
        info_label = QLabel(
            "ℹ️ Las credenciales de Google Cloud Vision se usan para OCR.\n"
            "Puede usar el mismo archivo que Firebase si tiene ambos servicios."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        form.addRow("", info_label)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_twilio_tab(self):
        """Create Twilio configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Twilio WhatsApp")
        form = QFormLayout()
        
        self.twilio_sid_input = QLineEdit()
        self.twilio_sid_input.setPlaceholderText("ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        form.addRow("Account SID:", self.twilio_sid_input)
        
        self.twilio_token_input = QLineEdit()
        self.twilio_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.twilio_token_input.setPlaceholderText("Tu Auth Token...")
        form.addRow("Auth Token:", self.twilio_token_input)
        
        self.twilio_number_input = QLineEdit()
        self.twilio_number_input.setPlaceholderText("whatsapp:+14155238886")
        form.addRow("WhatsApp Number:", self.twilio_number_input)
        
        info_label = QLabel(
            "ℹ️ Las credenciales de Twilio son opcionales.\n"
            "Se usan para enviar notificaciones por WhatsApp."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        form.addRow("", info_label)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_paths_tab(self):
        """Create application paths configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Rutas de la Aplicación")
        form = QFormLayout()
        
        self.data_folder_input = QLineEdit()
        self.data_folder_input.setPlaceholderText("./data")
        form.addRow("Carpeta de datos:", self.data_folder_input)
        
        self.export_folder_input = QLineEdit()
        self.export_folder_input.setPlaceholderText("./data/exports")
        form.addRow("Carpeta de exportaciones:", self.export_folder_input)
        
        self.temp_folder_input = QLineEdit()
        self.temp_folder_input.setPlaceholderText("./data/temp")
        form.addRow("Carpeta temporal:", self.temp_folder_input)
        
        info_label = QLabel(
            "ℹ️ Las rutas pueden ser absolutas o relativas.\n"
            "Las carpetas se crearán automáticamente si no existen."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        form.addRow("", info_label)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _browse_file(self, line_edit, title, file_filter):
        """Open file dialog and set the path in line_edit"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            title,
            "",
            file_filter
        )
        if filename:
            line_edit.setText(filename)
            # Auto-detect if it's Firebase credentials
            if line_edit == self.firebase_creds_input:
                self._auto_detect_firebase()
    
    def _auto_detect_firebase(self):
        """Auto-detect Firebase project ID from credentials file"""
        creds_path = self.firebase_creds_input.text().strip()
        if not creds_path or not os.path.exists(creds_path):
            QMessageBox.warning(
                self,
                "Advertencia",
                "Primero seleccione un archivo de credenciales válido."
            )
            return
        
        try:
            with open(creds_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            
            project_id = creds.get('project_id', '')
            if project_id:
                self.firebase_project_id_input.setText(project_id)
                
                # Auto-fill database URL if not set
                if not self.firebase_db_url_input.text():
                    db_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
                    self.firebase_db_url_input.setText(db_url)
                
                # Auto-fill storage bucket if not set
                if not self.firebase_storage_input.text():
                    storage = f"{project_id}.appspot.com"
                    self.firebase_storage_input.setText(storage)
                
                QMessageBox.information(
                    self,
                    "✅ Éxito",
                    f"Project ID detectado: {project_id}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "No se encontró 'project_id' en el archivo de credenciales."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al leer el archivo de credenciales:\n{str(e)}"
            )
    
    def _validate_credentials(self):
        """Validate the credentials"""
        errors = []
        warnings = []
        
        # Validate Firebase
        fb_creds = self.firebase_creds_input.text().strip()
        if fb_creds:
            if not os.path.exists(fb_creds):
                errors.append("❌ Archivo de credenciales Firebase no existe")
            else:
                try:
                    with open(fb_creds, 'r', encoding='utf-8') as f:
                        json.load(f)
                except:
                    errors.append("❌ Archivo de credenciales Firebase no es un JSON válido")
        else:
            warnings.append("⚠️ Credenciales Firebase no configuradas")
        
        # Validate Google Cloud
        gc_creds = self.google_creds_input.text().strip()
        if gc_creds:
            if not os.path.exists(gc_creds):
                errors.append("❌ Archivo de credenciales Google Cloud no existe")
            else:
                try:
                    with open(gc_creds, 'r', encoding='utf-8') as f:
                        json.load(f)
                except:
                    errors.append("❌ Archivo de credenciales Google Cloud no es un JSON válido")
        else:
            warnings.append("⚠️ Credenciales Google Cloud no configuradas")
        
        # Validate Twilio (optional)
        if not self.twilio_sid_input.text().strip():
            warnings.append("⚠️ Twilio Account SID no configurado (opcional)")
        
        # Show results
        if errors:
            QMessageBox.critical(
                self,
                "❌ Errores de validación",
                "\n".join(errors)
            )
        elif warnings:
            QMessageBox.warning(
                self,
                "⚠️ Advertencias",
                "\n".join(warnings) + "\n\nPuede continuar, pero algunas funcionalidades pueden no estar disponibles."
            )
        else:
            QMessageBox.information(
                self,
                "✅ Validación exitosa",
                "Todas las credenciales son válidas."
            )
    
    def _load_values(self):
        """Load values from config into form"""
        # Firebase
        fb = self.config.get("firebase", {})
        self.firebase_creds_input.setText(fb.get("credentials_path", ""))
        self.firebase_project_id_input.setText(fb.get("project_id", ""))
        self.firebase_db_url_input.setText(fb.get("database_url", ""))
        self.firebase_storage_input.setText(fb.get("storage_bucket", ""))
        
        # Google Cloud
        gc = self.config.get("google_cloud", {})
        self.google_creds_input.setText(gc.get("credentials_path", ""))
        
        # Twilio
        tw = self.config.get("twilio", {})
        self.twilio_sid_input.setText(tw.get("account_sid", ""))
        self.twilio_token_input.setText(tw.get("auth_token", ""))
        self.twilio_number_input.setText(tw.get("whatsapp_number", ""))
        
        # App paths
        app = self.config.get("app", {})
        self.data_folder_input.setText(app.get("data_folder", "./data"))
        self.export_folder_input.setText(app.get("export_folder", "./data/exports"))
        self.temp_folder_input.setText(app.get("temp_folder", "./data/temp"))
    
    def _save_and_accept(self):
        """Save configuration and accept dialog"""
        # Update config with form values
        self.config["firebase"] = {
            "credentials_path": self.firebase_creds_input.text().strip(),
            "project_id": self.firebase_project_id_input.text().strip(),
            "database_url": self.firebase_db_url_input.text().strip(),
            "storage_bucket": self.firebase_storage_input.text().strip()
        }
        
        self.config["google_cloud"] = {
            "credentials_path": self.google_creds_input.text().strip()
        }
        
        self.config["twilio"] = {
            "account_sid": self.twilio_sid_input.text().strip(),
            "auth_token": self.twilio_token_input.text().strip(),
            "whatsapp_number": self.twilio_number_input.text().strip()
        }
        
        self.config["app"] = {
            "data_folder": self.data_folder_input.text().strip(),
            "export_folder": self.export_folder_input.text().strip(),
            "temp_folder": self.temp_folder_input.text().strip()
        }
        
        # Save to file
        self.config_manager.config = self.config
        if self.config_manager.save():
            QMessageBox.information(
                self,
                "✅ Guardado",
                "Configuración guardada correctamente."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "❌ Error",
                "No se pudo guardar la configuración."
            )
