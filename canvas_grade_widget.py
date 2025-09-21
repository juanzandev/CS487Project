#!/usr/bin/env python3
"""
Canvas Grade Widget - PySide6 Desktop Widget
Displays Canvas courses and grades in a desktop widget
"""

import sys
import requests
import json
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QScrollArea, QFrame, QDialog,
                               QLineEdit, QTextEdit, QMessageBox, QFormLayout, QComboBox)
from PySide6.QtCore import Qt, QPoint, QTimer, QThread, Signal, QUrl
from PySide6.QtGui import QFont, QPalette, QPixmap, QPainter, QPen, QBrush
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Theme definitions
THEMES = {
    'auto': {
        'name': 'Auto (System)',
        'description': 'Follow system theme'
    },
    'light': {
        'name': 'Light',
        'bg_primary': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'bg_tertiary': '#e3f2fd',
        'text_primary': '#000000',
        'text_secondary': '#666666',
        'text_accent': '#1976D2',
        'border': '#2196F3',
        'border_light': '#dddddd',
        'success': '#2E7D32',
        'warning': '#F57C00',
        'error': '#D32F2F',
        'error_dark': '#B71C1C'
    },
    'dark': {
        'name': 'Dark',
        'bg_primary': '#2b2b2b',
        'bg_secondary': '#1e1e1e',
        'bg_tertiary': '#404040',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'text_accent': '#64B5F6',
        'border': '#64B5F6',
        'border_light': '#555555',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'error_dark': '#D32F2F'
    },
    'nord': {
        'name': 'Nord',
        'bg_primary': '#2E3440',
        'bg_secondary': '#3B4252',
        'bg_tertiary': '#434C5E',
        'text_primary': '#ECEFF4',
        'text_secondary': '#D8DEE9',
        'text_accent': '#88C0D0',
        'border': '#88C0D0',
        'border_light': '#4C566A',
        'success': '#A3BE8C',
        'warning': '#EBCB8B',
        'error': '#BF616A',
        'error_dark': '#B48EAD'
    }
}


def get_system_theme():
    """Detect system theme preference"""
    try:
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check if the window background is dark
            bg_color = palette.color(QPalette.Window)
            if bg_color.lightness() < 128:
                return 'dark'
            else:
                return 'light'
    except:
        pass
    return 'light'


def load_theme_config():
    """Load theme configuration from config.py"""
    try:
        # Read config.py directly from file system, not cached import
        config_path = 'config.py'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()

            # Parse the THEME value from the file
            for line in config_content.split('\n'):
                line = line.strip()
                if line.startswith('THEME = '):
                    # Extract the theme value
                    theme_value = line.split('THEME = ')[1].strip()
                    # Remove quotes if present
                    theme_value = theme_value.strip('"\'')
                    print(f"Loaded theme from config.py: {theme_value}")
                    return theme_value

        # Fallback: try import if file reading fails
        from config import THEME
        print(f"Loaded theme from import fallback: {THEME}")
        return THEME
    except Exception as e:
        print(f"Error loading theme config: {e}")
        return 'auto'


def save_theme_config(theme):
    """Save theme configuration to config.py"""
    try:
        config_path = 'config.py'
        print(f"Saving theme '{theme}' to {os.path.abspath(config_path)}")

        # Read existing config
        config_content = ""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()
            print(
                f"Read existing config content: {len(config_content)} characters")

        # Update or add theme setting
        if 'THEME = ' in config_content:
            lines = config_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('THEME = '):
                    old_value = line
                    lines[i] = f'THEME = "{theme}"'
                    print(f"Updated theme line: {old_value} -> {lines[i]}")
                    break
            config_content = '\n'.join(lines)
        else:
            config_content += f'\nTHEME = "{theme}"\n'
            print(f"Added new theme line: THEME = \"{theme}\"")

        with open(config_path, 'w') as f:
            f.write(config_content)
        print(
            f"Successfully saved theme config to {os.path.abspath(config_path)}")
        return True
    except Exception as e:
        print(f"Error saving theme config: {e}")
        return False


def get_theme_styles(theme_name=None):
    """Get CSS styles for the specified theme"""
    if theme_name is None:
        theme_name = load_theme_config()

    if theme_name == 'auto':
        theme_name = get_system_theme()

    if theme_name not in THEMES or theme_name == 'auto':
        theme_name = 'light'

    theme = THEMES[theme_name]

    return {
        'main_widget': f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['bg_secondary']},
                    stop:0.3 {theme['bg_primary']},
                    stop:1 {theme['bg_secondary']});
                color: {theme['text_primary']};
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['border']}, stop:0.5 {theme['border_light']}, stop:1 {theme['border']});
                border-radius: 12px;
            }}
            QPushButton:not(#settingsButton):not(#refreshButton):not(#closeButton) {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['bg_primary']},
                    stop:1 {theme['bg_tertiary']});
                color: {theme['text_primary']};
                border: 1px solid {theme['border_light']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: 500;
            }}
            QPushButton:not(#settingsButton):not(#refreshButton):not(#closeButton):hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['bg_tertiary']},
                    stop:1 {theme['bg_primary']});
                border: 1px solid {theme['border']};
            }}
            QPushButton:not(#settingsButton):not(#refreshButton):not(#closeButton):pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['border_light']},
                    stop:1 {theme['bg_tertiary']});
            }}
            QPushButton#settingsButton, QPushButton#refreshButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(245, 248, 252, 0.9));
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 6px;
                font-size: 13px;
                color: #4A90E2;
                font-weight: normal;
                text-align: center;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton#settingsButton:hover, QPushButton#refreshButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(74, 144, 226, 0.08),
                    stop:1 rgba(74, 144, 226, 0.15));
                border: 1px solid rgba(74, 144, 226, 0.6);
                color: #2E5C8A;
            }}
            QPushButton#closeButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(252, 245, 245, 0.9));
                border: 1px solid rgba(211, 47, 47, 0.3);
                border-radius: 6px;
                font-size: 18px;
                font-weight: normal;
                color: #d32f2f;
                text-align: center;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton#closeButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(211, 47, 47, 0.08),
                    stop:1 rgba(211, 47, 47, 0.15));
                border: 1px solid rgba(211, 47, 47, 0.6);
                color: #B71C1C;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QLabel {{
                border: none;
                color: {theme['text_primary']};
            }}
        """,
        'course_widget': f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['bg_primary']},
                    stop:0.5 {theme['bg_secondary']},
                    stop:1 {theme['bg_primary']});
                color: {theme['text_primary']};
                border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['border_light']}, 
                    stop:0.5 {theme['border']}, 
                    stop:1 {theme['border_light']});
                border-radius: 8px;
                margin: 3px;
                padding: 8px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme['bg_secondary']},
                    stop:0.5 {theme['bg_tertiary']},
                    stop:1 {theme['bg_secondary']});
                border: 1px solid {theme['border']};
            }}
            QLabel {{
                border: none;
                color: {theme['text_primary']};
                font-weight: 500;
            }}
        """,
        'dialog': f"""
            QDialog {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
            }}
            QLabel {{
                color: {theme['text_primary']};
                border: none;
            }}
            QLineEdit {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border_light']};
                border-radius: 3px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['border']};
            }}
            QTextEdit {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border_light']};
                border-radius: 3px;
            }}
            QPushButton {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border_light']};
                border-radius: 3px;
                padding: 8px 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {theme['border_light']};
            }}
            QComboBox {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border_light']};
                border-radius: 3px;
                padding: 5px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 2px solid {theme['border']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border_light']};
                selection-background-color: {theme['bg_tertiary']};
            }}
        """,
        'title': f"""
            color: {theme['text_accent']};
            font-size: 16px;
            font-weight: bold;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(74, 144, 226, 0.1),
                stop:0.5 rgba(255, 255, 255, 0.05),
                stop:1 rgba(74, 144, 226, 0.1));
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid rgba(74, 144, 226, 0.2);
        """,
        'close_button': f"""
            QPushButton {{
                color: {theme['error']};
                background-color: {theme['bg_primary']};
                font-weight: bold;
                font-size: 14px;
                border: 1px solid {theme['border_light']};
            }}
            QPushButton:hover {{
                background-color: {theme['error']};
                color: {theme['bg_primary']};
            }}
        """,
        'status_text': f"color: {theme['text_secondary']};",
        'success_text': f"color: {theme['success']};",
        'error_text': f"color: {theme['error']};",
        'grade_colors': {
            'A': theme['success'],
            'B': theme['warning'],
            'C': theme['error'],
            'F': theme['error_dark']
        }
    }

# Configuration handling


def load_config():
    """Load configuration from config.py if it exists"""
    try:
        from config import CANVAS_BASE_URL, API_TOKEN
        # Validate that config is not the default values
        if API_TOKEN == "your_api_token_here" or CANVAS_BASE_URL == "https://your-school.instructure.com":
            return None, None
        return CANVAS_BASE_URL, API_TOKEN
    except ImportError:
        return None, None


def save_config(canvas_url, api_token, theme=None):
    """Save configuration to config.py"""
    # Load existing theme if not provided
    if theme is None:
        theme = load_theme_config()

    config_content = f'''# Canvas API Configuration
CANVAS_BASE_URL = "{canvas_url}"
API_TOKEN = "{api_token}"
THEME = "{theme}"
'''

    try:
        with open('config.py', 'w') as f:
            f.write(config_content)
        return True
    except Exception:
        return False


class SetupDialog(QDialog):
    """Dialog for initial Canvas API setup"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas_url = None
        self.api_token = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Canvas Grade Widget Setup")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint |
                            Qt.CustomizeWindowHint)

        layout = QVBoxLayout()

        # Welcome text
        welcome_label = QLabel("Welcome to Canvas Grade Widget!")
        welcome_label.setFont(QFont("Arial", 14, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        # Use theme-aware accent color
        current_theme = load_theme_config()
        if current_theme == 'auto':
            current_theme = get_system_theme()
        if current_theme not in THEMES or current_theme == 'auto':
            current_theme = 'light'
        theme_colors = THEMES[current_theme]
        welcome_label.setStyleSheet(
            f"color: {theme_colors['text_accent']}; margin: 10px;")

        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(120)
        instructions.setHtml("""
        <p>To get started, you'll need:</p>
        <ol>
        <li><b>Canvas URL:</b> Your institution's Canvas website (e.g., https://iit.instructure.com)</li>
        <li><b>API Token:</b> Your personal Canvas API token</li>
        </ol>
        <p><b>To get an API token:</b><br>
        1. Log into Canvas<br>
        2. Go to Account → Settings<br>
        3. Scroll to "Approved Integrations"<br>
        4. Click "+ New Access Token"<br>
        5. Copy the generated token</p>
        """)

        # Form
        form_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://your-school.instructure.com")
        self.url_input.textChanged.connect(self.validate_inputs)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Paste your API token here")
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.textChanged.connect(self.validate_inputs)

        # Show/hide token button
        self.show_token_btn = QPushButton("👁")
        self.show_token_btn.setFixedSize(30, 30)
        self.show_token_btn.clicked.connect(self.toggle_token_visibility)

        token_layout = QHBoxLayout()
        token_layout.addWidget(self.token_input)
        token_layout.addWidget(self.show_token_btn)

        form_layout.addRow("Canvas URL:", self.url_input)
        form_layout.addRow("API Token:", token_layout)

        # Test connection button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setEnabled(False)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save & Continue")
        self.save_btn.clicked.connect(self.save_and_continue)
        self.save_btn.setEnabled(False)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.save_btn)

        # Add to main layout
        layout.addWidget(welcome_label)
        layout.addWidget(instructions)
        layout.addLayout(form_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_token_visibility(self):
        """Toggle token visibility"""
        if self.token_input.echoMode() == QLineEdit.Password:
            self.token_input.setEchoMode(QLineEdit.Normal)
            self.show_token_btn.setText("🙈")
        else:
            self.token_input.setEchoMode(QLineEdit.Password)
            self.show_token_btn.setText("👁")

    def validate_inputs(self):
        """Enable test button when both inputs have content"""
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()

        has_content = len(url) > 0 and len(token) > 0
        self.test_btn.setEnabled(has_content)

        # Reset status when inputs change
        if has_content:
            self.status_label.setText("")
            self.save_btn.setEnabled(False)

    def test_connection(self):
        """Test Canvas API connection"""
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()

        if not url.startswith('http'):
            url = 'https://' + url

        self.status_label.setText("Testing connection...")
        self.test_btn.setEnabled(False)

        try:
            # Test API call
            api_url = f"{url}/api/v1/courses"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            params = {"per_page": 1}

            response = requests.get(
                api_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                self.status_label.setText("✅ Connection successful!")
                self.status_label.setStyleSheet("color: green;")
                self.save_btn.setEnabled(True)
                self.canvas_url = url
                self.api_token = token
            elif response.status_code == 401:
                self.status_label.setText("❌ Invalid API token")
                self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setText(
                    f"❌ Error: HTTP {response.status_code}")
                self.status_label.setStyleSheet("color: red;")

        except requests.exceptions.Timeout:
            self.status_label.setText("❌ Connection timeout")
            self.status_label.setStyleSheet("color: red;")
        except requests.exceptions.RequestException:
            self.status_label.setText("❌ Unable to connect to Canvas")
            self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

        self.test_btn.setEnabled(True)

    def save_and_continue(self):
        """Save configuration and close dialog"""
        if save_config(self.canvas_url, self.api_token):
            self.accept()
        else:
            QMessageBox.critical(
                self, "Error", "Failed to save configuration!")


class SettingsDialog(QDialog):
    """Dialog for changing Canvas API settings"""

    def __init__(self, current_url, current_token, parent=None):
        super().__init__(parent)
        self.canvas_url = current_url
        self.api_token = current_token
        self.original_theme = load_theme_config()  # Store original theme
        self.initUI()
        self.apply_theme()

    def apply_theme(self):
        """Apply theme to dialog"""
        styles = get_theme_styles()
        self.setStyleSheet(styles['dialog'])

    def initUI(self):
        self.setWindowTitle("Canvas Settings")
        self.setFixedSize(450, 350)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Update Canvas Settings")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        styles = get_theme_styles()
        title_label.setStyleSheet(f"margin: 10px; {styles['title']}")

        # Form
        form_layout = QFormLayout()

        self.url_input = QLineEdit(self.canvas_url)
        self.url_input.textChanged.connect(self.validate_inputs)

        self.token_input = QLineEdit(self.api_token)
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.textChanged.connect(self.validate_inputs)

        # Show/hide token button
        self.show_token_btn = QPushButton("👁")
        self.show_token_btn.setFixedSize(30, 30)
        self.show_token_btn.clicked.connect(self.toggle_token_visibility)

        token_layout = QHBoxLayout()
        token_layout.addWidget(self.token_input)
        token_layout.addWidget(self.show_token_btn)

        # Theme selection
        self.theme_combo = QComboBox()
        for theme_key, theme_info in THEMES.items():
            self.theme_combo.addItem(theme_info['name'], theme_key)

        # Set current theme
        current_theme = load_theme_config()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break

        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

        form_layout.addRow("Canvas URL:", self.url_input)
        form_layout.addRow("API Token:", token_layout)
        form_layout.addRow("Theme:", self.theme_combo)

        # Test connection button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_and_continue)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(self.save_btn)

        # Add to main layout
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_theme_changed(self):
        """Handle theme change"""
        try:
            selected_theme = self.theme_combo.currentData()

            # First save theme to config.py
            if save_theme_config(selected_theme):
                print(f"Theme saved to config.py: {selected_theme}")

                # Apply theme to settings dialog
                self.apply_theme()

                # Notify parent to update theme if it exists
                if self.parent():
                    # Apply comprehensive theme change using a single shot timer to prevent crashes
                    QTimer.singleShot(
                        100, lambda: self.apply_comprehensive_theme_change(self.parent()))
            else:
                raise Exception("Failed to save theme to config.py")

        except Exception as e:
            print(f"Error changing theme: {e}")
            QMessageBox.warning(self, "Theme Change Error",
                                f"There was an error changing the theme: {str(e)}\nPlease check that config.py is writable.")

    def apply_comprehensive_theme_change(self, main_widget):
        """Apply comprehensive theme changes to main widget"""
        try:
            # Prevent simultaneous theme changes
            if hasattr(main_widget, 'theme_applying') and main_widget.theme_applying:
                print("Theme change already in progress, skipping...")
                return

            main_widget.theme_applying = True

            # Apply theme to main widget
            main_widget.apply_theme()

            # Refresh courses with new theme
            if hasattr(main_widget, 'display_courses'):
                main_widget.display_courses()

            # Update status
            if hasattr(main_widget, 'status_label'):
                main_widget.status_label.setText(
                    f"Theme updated successfully! Last updated: {main_widget.get_current_time()}")

        except Exception as e:
            print(f"Error applying comprehensive theme change: {e}")
        finally:
            if hasattr(main_widget, 'theme_applying'):
                main_widget.theme_applying = False

    def toggle_token_visibility(self):
        """Toggle token visibility"""
        if self.token_input.echoMode() == QLineEdit.Password:
            self.token_input.setEchoMode(QLineEdit.Normal)
            self.show_token_btn.setText("🙈")
        else:
            self.token_input.setEchoMode(QLineEdit.Password)
            self.show_token_btn.setText("👁")

    def validate_inputs(self):
        """Reset status when inputs change"""
        self.status_label.setText("")

    def test_connection(self):
        """Test Canvas API connection"""
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()

        if not url.startswith('http'):
            url = 'https://' + url

        self.status_label.setText("Testing connection...")
        self.test_btn.setEnabled(False)

        try:
            # Test API call
            api_url = f"{url}/api/v1/courses"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            params = {"per_page": 1}

            response = requests.get(
                api_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                self.status_label.setText("✅ Connection successful!")
                self.status_label.setStyleSheet("color: green;")
                self.canvas_url = url
                self.api_token = token
            elif response.status_code == 401:
                self.status_label.setText("❌ Invalid API token")
                self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setText(
                    f"❌ Error: HTTP {response.status_code}")
                self.status_label.setStyleSheet("color: red;")

        except requests.exceptions.Timeout:
            self.status_label.setText("❌ Connection timeout")
            self.status_label.setStyleSheet("color: red;")
        except requests.exceptions.RequestException:
            self.status_label.setText("❌ Unable to connect to Canvas")
            self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

        self.test_btn.setEnabled(True)

    def save_and_continue(self):
        """Save configuration and close dialog"""
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()
        theme = self.theme_combo.currentData()

        if not url.startswith('http'):
            url = 'https://' + url

        if save_config(url, token, theme):
            self.canvas_url = url
            self.api_token = token

            # Check if theme changed
            theme_changed = theme != self.original_theme

            # Store parent reference before accepting dialog
            parent_widget = self.parent()
            self.accept()

            # Apply theme changes immediately without restart
            if parent_widget:
                # Force immediate theme refresh
                QTimer.singleShot(100, lambda: self.apply_all_theme_changes(
                    parent_widget, theme_changed))
        else:
            QMessageBox.critical(
                self, "Error", "Failed to save configuration!")

    def apply_all_theme_changes(self, main_widget, theme_changed):
        """Apply theme changes to all components without restart"""
        # Prevent simultaneous theme changes that could cause crashes
        if hasattr(main_widget, 'theme_applying') and main_widget.theme_applying:
            print("Theme change already in progress, skipping...")
            return

        try:
            main_widget.theme_applying = True
            print(f"Applying theme changes, theme_changed: {theme_changed}")

            # Step 1: Apply theme to main widget
            main_widget.apply_theme()

            # Step 2: Force refresh all existing course widgets
            # Clear all existing course widgets first
            if hasattr(main_widget, 'courses_layout') and main_widget.courses_layout:
                for i in reversed(range(main_widget.courses_layout.count())):
                    item = main_widget.courses_layout.itemAt(i)
                    if item:
                        child = item.widget()
                        if child:
                            child.setParent(None)
                            child.deleteLater()

                # Step 3: Recreate course widgets with new theme
                if hasattr(main_widget, 'courses') and main_widget.courses:
                    for course in main_widget.courses:
                        course_widget = CourseWidget(course)
                        main_widget.courses_layout.addWidget(course_widget)

                # Add stretch to push courses to top
                main_widget.courses_layout.addStretch()

            # Step 4: Apply theme to all buttons and controls
            # Refresh button
            if hasattr(main_widget, 'refresh_button'):
                styles = get_theme_styles()
                main_widget.refresh_button.setStyleSheet(styles['main_widget'])

            # Step 5: Update the status
            if hasattr(main_widget, 'status_label'):
                main_widget.status_label.setText(
                    f"Theme updated successfully! Last updated: {main_widget.get_current_time()}")

            # Step 6: Force widget update
            main_widget.update()
            main_widget.repaint()

            print("Theme changes applied successfully")

        except Exception as e:
            print(f"Error applying theme: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: show message that manual restart may be needed
            QMessageBox.information(
                None, "Theme Updated",
                f"Theme has been saved but there was an error applying it: {str(e)}\nPlease restart the application to see the changes."
            )
        finally:
            # Always reset the flag
            if hasattr(main_widget, 'theme_applying'):
                main_widget.theme_applying = False


class CanvasAPIWorker(QThread):
    """Worker thread for Canvas API calls to prevent UI freezing"""
    courses_fetched = Signal(list)
    profile_fetched = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, canvas_url, api_token):
        super().__init__()
        self.canvas_url = canvas_url
        self.api_token = api_token
        self._stop_requested = False

    def run(self):
        try:
            if self._stop_requested:
                return

            # Fetch user profile information
            profile = self.get_user_profile()
            if profile and not self._stop_requested:
                self.profile_fetched.emit(profile)

            courses = self.get_canvas_courses()
            if courses and not self._stop_requested:
                # Fetch grades for each course
                for course in courses:
                    if self._stop_requested:
                        return
                    grade_info = self.get_course_grade(course['id'])
                    course['grade_info'] = grade_info
                self.courses_fetched.emit(courses)
            else:
                self.error_occurred.emit("Failed to fetch courses")
        except Exception as e:
            if not self._stop_requested:
                self.error_occurred.emit(f"Error: {str(e)}")

    def stop(self):
        """Request the thread to stop"""
        self._stop_requested = True

    def get_canvas_courses(self):
        """Fetches all courses from Canvas API"""
        url = f"{self.canvas_url}/api/v1/courses"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        params = {
            "enrollment_state": "active",
            "include": ["term"],
            "per_page": 100
        }

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    def get_course_grade(self, course_id):
        """Fetches grade for a specific course"""
        url = f"{self.canvas_url}/api/v1/courses/{course_id}/enrollments"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        params = {
            "type": ["StudentEnrollment"],
            "include": ["grades"],
            "user_id": "self"
        }

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                enrollments = response.json()
                if enrollments and len(enrollments) > 0:
                    grades = enrollments[0].get('grades', {})
                    return {
                        'current_score': grades.get('current_score'),
                        'current_grade': grades.get('current_grade'),
                        'final_score': grades.get('final_score'),
                        'final_grade': grades.get('final_grade')
                    }
        except Exception:
            pass
        return None

    def get_user_profile(self):
        """Fetches current user profile information"""
        url = f"{self.canvas_url}/api/v1/users/self/profile"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                profile_data = response.json()
                return {
                    'name': profile_data.get('name', 'Student'),
                    'short_name': profile_data.get('short_name', ''),
                    'avatar_url': profile_data.get('avatar_url', ''),
                    'id': profile_data.get('id', '')
                }
        except Exception as e:
            print(f"Error fetching user profile: {e}")
        return None


class CourseWidget(QFrame):
    """Widget to display a single course with grade"""

    def __init__(self, course_data):
        super().__init__()
        self.course_data = course_data
        self.initUI()

    def initUI(self):
        self.setFrameStyle(QFrame.Box)
        # Apply theme styles
        styles = get_theme_styles()
        self.setStyleSheet(styles['course_widget'])

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)

        # Course name
        name = self.course_data.get('name', 'Unknown Course')
        if len(name) > 50:  # Truncate long names
            name = name[:47] + "..."

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_label.setWordWrap(True)
        # Use theme-aware text color - get current theme colors
        current_theme = load_theme_config()
        if current_theme == 'auto':
            current_theme = get_system_theme()
        if current_theme not in THEMES or current_theme == 'auto':
            current_theme = 'light'
        theme_colors = THEMES[current_theme]
        name_label.setStyleSheet(
            f"border: none; color: {theme_colors['text_primary']};")

        # Term information only (course name is already displayed above)
        term = "Unknown term"
        if 'term' in self.course_data and self.course_data['term']:
            term = self.course_data['term'].get('name', 'Unknown term')

        info_label = QLabel(term)
        info_label.setFont(QFont("Arial", 8))
        info_label.setStyleSheet(
            f"color: {theme_colors['text_secondary']}; border: none;")

        # Grade information
        grade_label = self.create_grade_label()

        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addWidget(grade_label)

        self.setLayout(layout)

    def create_grade_label(self):
        """Create grade label with appropriate styling"""
        # Get current theme colors
        current_theme = load_theme_config()
        if current_theme == 'auto':
            current_theme = get_system_theme()
        if current_theme not in THEMES or current_theme == 'auto':
            current_theme = 'light'
        theme_colors = THEMES[current_theme]

        grade_info = self.course_data.get('grade_info')

        if not grade_info:
            grade_label = QLabel("Grade: Not available")
            grade_label.setStyleSheet(
                f"color: {theme_colors['text_secondary']}; font-size: 9px;")
            return grade_label

        # Determine what grade to show
        current_score = grade_info.get('current_score')
        current_grade = grade_info.get('current_grade')
        final_score = grade_info.get('final_score')
        final_grade = grade_info.get('final_grade')

        if current_score is not None:
            grade_text = f"Current: {current_score:.1f}%"
            if current_grade:
                grade_text += f" ({current_grade})"
            score = current_score
        elif final_score is not None:
            grade_text = f"Final: {final_score:.1f}%"
            if final_grade:
                grade_text += f" ({final_grade})"
            score = final_score
        else:
            grade_label = QLabel("Grade: No grade yet")
            grade_label.setStyleSheet(
                f"color: {theme_colors['text_secondary']}; font-size: 9px;")
            return grade_label

        grade_label = QLabel(grade_text)
        grade_label.setFont(QFont("Arial", 9, QFont.Bold))

        # Color coding based on grade using theme colors
        styles = get_theme_styles()
        if score >= 90:
            color = styles['grade_colors']['A']
        elif score >= 80:
            color = styles['grade_colors']['B']
        elif score >= 70:
            color = styles['grade_colors']['C']
        else:
            color = styles['grade_colors']['F']

        grade_label.setStyleSheet(
            f"color: {color}; font-size: 9px; border: none;")

        return grade_label


class ProfileWidget(QWidget):
    """Widget to display student profile information"""

    def __init__(self):
        super().__init__()
        self.profile_data = None
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)
        self.initUI()

    def initUI(self):
        # Add elegant styling to the profile widget
        self.setStyleSheet("""
            ProfileWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.8),
                    stop:1 rgba(240, 245, 251, 0.8));
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 8px;
                padding: 5px;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Profile picture (circular)
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(40, 40)
        # Elegant circular border with gradient effect
        self.avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4A90E2, stop:0.5 #7BB3F0, stop:1 #4A90E2);
                border-radius: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        self.set_default_avatar()
        layout.addWidget(self.avatar_label)

        # Student name
        self.name_label = QLabel("Loading...")
        self.name_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                font-size: 13px;
                color: #2c3e50;
                background: transparent;
                padding: 2px 8px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.name_label)

        layout.addStretch()
        self.setLayout(layout)

    def set_default_avatar(self):
        """Set a default avatar when no image is available"""
        pixmap = QPixmap(40, 40)
        pixmap.fill(Qt.lightGray)

        # Draw a simple person icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.darkGray, 2))
        painter.setBrush(QBrush(Qt.white))

        # Draw circle background
        painter.drawEllipse(2, 2, 36, 36)

        # Draw simple person icon
        painter.setPen(QPen(Qt.darkGray, 3))
        # Head
        painter.drawEllipse(15, 10, 10, 10)
        # Body
        painter.drawEllipse(12, 22, 16, 12)

        painter.end()

        # Make it circular
        circular_pixmap = self.make_circular(pixmap)
        self.avatar_label.setPixmap(circular_pixmap)

    def make_circular(self, pixmap):
        """Convert a pixmap to circular shape"""
        size = min(pixmap.width(), pixmap.height())
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.transparent)

        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create circular clipping region
        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        # Draw the original pixmap within the circular clipping region
        painter.drawPixmap(0, 0, size, size, pixmap)
        painter.end()

        return circular_pixmap

    def update_profile(self, profile_data):
        """Update the profile widget with user data"""
        self.profile_data = profile_data

        # Update name
        name = profile_data.get('name', 'Student')
        self.name_label.setText(name)

        # Load avatar if available
        avatar_url = profile_data.get('avatar_url', '')
        if avatar_url:
            self.load_avatar(avatar_url)
        else:
            self.set_default_avatar()

    def load_avatar(self, url):
        """Load avatar image from URL"""
        try:
            request = QNetworkRequest(QUrl(url))
            self.network_manager.get(request)
        except Exception as e:
            print(f"Error loading avatar: {e}")
            self.set_default_avatar()

    def on_image_loaded(self, reply):
        """Handle loaded image data"""
        try:
            # Fix Qt6 API - use NetworkError enum
            from PySide6.QtNetwork import QNetworkReply
            if reply.error() == QNetworkReply.NetworkError.NoError:
                data = reply.readAll()
                pixmap = QPixmap()
                if pixmap.loadFromData(data):
                    # Scale and make circular with fixed masking
                    scaled_pixmap = pixmap.scaled(
                        40, 40, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    circular_pixmap = self.make_circular(scaled_pixmap)
                    self.avatar_label.setPixmap(circular_pixmap)
                    self.avatar_label.setVisible(True)
                    # Keep elegant border when image is loaded
                    self.avatar_label.setStyleSheet("""
                        QLabel {
                            border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #4A90E2, stop:0.5 #7BB3F0, stop:1 #4A90E2);
                            border-radius: 20px;
                        }
                    """)
                else:
                    self.set_default_avatar()
            else:
                self.set_default_avatar()
                self.set_default_avatar()
        except Exception as e:
            print(f"Error processing avatar image: {e}")
            import traceback
            traceback.print_exc()
            self.set_default_avatar()
        finally:
            reply.deleteLater()


class CanvasGradeWidget(QWidget):
    """Main desktop widget for Canvas grades"""

    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.courses = []
        self.canvas_url = None
        self.api_token = None
        self.theme_applying = False  # Flag to prevent simultaneous theme changes
        self.current_applied_theme = None  # Track currently applied theme
        self.profile_widget = None  # Profile widget for user info

        # Load configuration or show setup
        if not self.load_configuration():
            self.show_setup_dialog()

        self.initUI()
        self.apply_theme()
        self.setup_refresh_timer()
        self.refresh_data()

    def apply_theme(self):
        """Apply current theme to the widget and all its components"""
        # Read theme from config.py directly
        current_theme_from_config = load_theme_config()

        # Only apply theme if it actually changed
        if self.current_applied_theme == current_theme_from_config:
            print(
                f"Theme unchanged ({current_theme_from_config}), skipping application")
            return

        print(
            f"Applying theme change: {self.current_applied_theme} -> {current_theme_from_config}")

        # Get styles for the theme from config
        styles = get_theme_styles(current_theme_from_config)

        # Apply main widget styles
        self.setStyleSheet(styles['main_widget'])

        # Control button styles are now handled in the main stylesheet with object names

        # Apply styles to status label if it exists
        if hasattr(self, 'status_label'):
            self.status_label.setStyleSheet(
                f"font-size: 10px; border: none; {styles['status_text']}")

        # Update the current applied theme
        self.current_applied_theme = current_theme_from_config

        # Force update
        self.update()
        self.repaint()

        print(f"Theme applied successfully: {current_theme_from_config}")

    def load_configuration(self):
        """Load Canvas configuration"""
        self.canvas_url, self.api_token = load_config()
        return self.canvas_url is not None and self.api_token is not None

    def show_setup_dialog(self):
        """Show setup dialog for first-time configuration"""
        setup_dialog = SetupDialog(self)
        if setup_dialog.exec() == QDialog.Accepted:
            self.canvas_url = setup_dialog.canvas_url
            self.api_token = setup_dialog.api_token
        else:
            # User cancelled setup, exit application
            sys.exit(0)

    def show_settings_dialog(self):
        """Show settings dialog to update configuration"""
        settings_dialog = SettingsDialog(self.canvas_url, self.api_token, self)
        if settings_dialog.exec() == QDialog.Accepted:
            self.canvas_url = settings_dialog.canvas_url
            self.api_token = settings_dialog.api_token
            # Refresh data with new settings
            self.refresh_data()

    def initUI(self):
        # Window properties for desktop widget behavior
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint
        )

        self.setGeometry(100, 100, 350, 500)
        self.setWindowOpacity(0.96)

        # Add drop shadow effect
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

        # Theme will be applied by apply_theme() method

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Header with title and controls
        header_layout = QHBoxLayout()

        title_label = QLabel("Canvas Grades")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        styles = get_theme_styles()
        title_label.setStyleSheet(f"border: none; {styles['title']}")

        # Settings button
        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(28, 28)
        self.settings_button.clicked.connect(self.show_settings_dialog)
        self.settings_button.setToolTip("Canvas Settings")

        # Refresh button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedSize(28, 28)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setToolTip("Refresh grades")

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(28, 28)
        self.close_button.clicked.connect(self.close)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.close_button)

        # Profile widget (student name and picture)
        self.profile_widget = ProfileWidget()

        # Status label
        self.status_label = QLabel("Loading courses...")
        self.status_label.setStyleSheet(
            f"font-size: 10px; border: none; {styles['status_text']}")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Scroll area for courses
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.courses_container = QWidget()
        self.courses_layout = QVBoxLayout(self.courses_container)
        self.courses_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.courses_container)

        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.profile_widget)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def setup_refresh_timer(self):
        """Setup automatic refresh every 10 minutes"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(600000)  # 10 minutes

    def refresh_data(self):
        """Refresh course data from Canvas"""
        # Check for theme changes in config.py
        self.check_theme_changes()

        if not self.canvas_url or not self.api_token:
            self.status_label.setText("Configuration missing")
            return

        self.status_label.setText("Refreshing courses...")
        self.refresh_button.setEnabled(False)

        # Start API worker thread with current configuration
        self.api_worker = CanvasAPIWorker(self.canvas_url, self.api_token)
        self.api_worker.courses_fetched.connect(self.on_courses_fetched)
        self.api_worker.profile_fetched.connect(self.on_profile_fetched)
        self.api_worker.error_occurred.connect(self.on_error)
        self.api_worker.start()

    def on_courses_fetched(self, courses):
        """Handle successful course fetch"""
        self.courses = courses
        self.display_courses()
        self.status_label.setText(f"Last updated: {self.get_current_time()}")
        self.refresh_button.setEnabled(True)

    def on_profile_fetched(self, profile_data):
        """Handle successful profile fetch"""
        if self.profile_widget and profile_data:
            self.profile_widget.update_profile(profile_data)
            print(f"Profile updated: {profile_data.get('name', 'Unknown')}")
            print(
                f"ProfileWidget after update - size: {self.profile_widget.size()}, visible: {self.profile_widget.isVisible()}")
            print(f"ProfileWidget geometry: {self.profile_widget.geometry()}")

    def on_error(self, error_message):
        """Handle API error"""
        self.status_label.setText(f"Error: {error_message}")
        self.refresh_button.setEnabled(True)

    def display_courses(self):
        """Display courses in the widget"""
        # Clear existing courses
        for i in reversed(range(self.courses_layout.count())):
            child = self.courses_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add course widgets
        for course in self.courses:
            course_widget = CourseWidget(course)
            self.courses_layout.addWidget(course_widget)

        # Add stretch to push courses to top
        self.courses_layout.addStretch()

    def get_current_time(self):
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M")

    def check_theme_changes(self):
        """Check if theme has changed in config.py and apply if needed"""
        try:
            current_config_theme = load_theme_config()
            print(
                f"Theme check: config={current_config_theme}, applied={self.current_applied_theme}")

            if current_config_theme != self.current_applied_theme:
                print(
                    f"Theme changed detected: {self.current_applied_theme} -> {current_config_theme}")
                self.apply_theme()
                # Also refresh course widgets with new theme
                self.display_courses()
                if hasattr(self, 'status_label'):
                    self.status_label.setText(
                        f"Theme auto-updated to {current_config_theme}! Last updated: {self.get_current_time()}")
        except Exception as e:
            print(f"Error checking theme changes: {e}")

    def closeEvent(self, event):
        """Handle application close event"""
        print("Application closing - cleaning up resources...")

        # Stop refresh timer if it exists
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
            print("Refresh timer stopped")

        # Stop and wait for API worker thread to finish
        if hasattr(self, 'api_worker') and self.api_worker.isRunning():
            print("Stopping API worker thread...")
            self.api_worker.stop()  # Request graceful stop
            self.api_worker.quit()
            # Wait up to 3 seconds for thread to finish
            self.api_worker.wait(3000)
            if self.api_worker.isRunning():
                print("Force terminating API worker thread...")
                self.api_worker.terminate()  # Force terminate if still running
            else:
                print("API worker thread stopped gracefully")

        # Stop any running QTimers
        for child in self.findChildren(QTimer):
            if child.isActive():
                child.stop()
                print(f"Stopped timer: {child}")

        # Clear any dialog references
        if hasattr(self, 'setup_dialog'):
            self.setup_dialog = None
        if hasattr(self, 'settings_dialog'):
            self.settings_dialog = None

        print("Resource cleanup completed")
        event.accept()

        # Force application exit to prevent background processes
        app = QApplication.instance()
        if app:
            print("Calling QApplication.quit()")
            app.quit()

        # Additional cleanup to ensure complete exit
        import sys
        print("Calling sys.exit()")
        sys.exit(0)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - \
                self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse movement for dragging"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def main():
    import signal

    app = QApplication(sys.argv)

    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\nShutting down gracefully...")
        app.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Create and show the widget
    widget = CanvasGradeWidget()
    widget.show()

    # Make sure it starts below other windows
    widget.lower()

    # Run the application
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
