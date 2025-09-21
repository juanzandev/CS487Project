#!/usr/bin/env python3
"""
Test Qt image loading for Canvas profile picture
This will help debug Qt-specific image loading issues
"""

import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from config import CANVAS_BASE_URL, API_TOKEN


class ProfileImageTest(QWidget):
    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)
        self.initUI()
        self.test_image_loading()

    def initUI(self):
        self.setWindowTitle("Profile Image Test")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        # Test with local file first
        self.local_image_label = QLabel("Local Image Test:")
        layout.addWidget(self.local_image_label)

        self.local_avatar_label = QLabel()
        self.local_avatar_label.setFixedSize(100, 100)
        self.local_avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2196F3;
                border-radius: 50px;
                background-color: #f0f0f0;
            }
        """)
        layout.addWidget(self.local_avatar_label)

        # Test with network loading
        self.network_image_label = QLabel("Network Image Test:")
        layout.addWidget(self.network_image_label)

        self.network_avatar_label = QLabel()
        self.network_avatar_label.setFixedSize(100, 100)
        self.network_avatar_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2196F3;
                border-radius: 50px;
                background-color: #f0f0f0;
            }
        """)
        layout.addWidget(self.network_avatar_label)

        # Status label
        self.status_label = QLabel("Starting tests...")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def make_circular(self, pixmap):
        """Convert a pixmap to circular shape"""
        size = min(pixmap.width(), pixmap.height())
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.transparent)

        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create circular clipping path
        painter.drawEllipse(0, 0, size, size)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

        # Draw the original pixmap within the circular area
        painter.drawPixmap(0, 0, size, size, pixmap)
        painter.end()

        return circular_pixmap

    def test_local_image(self):
        """Test loading the locally downloaded image"""
        try:
            print("Testing local image loading...")
            pixmap = QPixmap("profile_picture.jpg")

            if pixmap.isNull():
                print("❌ Failed to load local image")
                self.local_image_label.setText("Local Image: FAILED")
                return False
            else:
                print(
                    f"✅ Local image loaded: {pixmap.width()}x{pixmap.height()}")

                # Scale and make circular
                scaled_pixmap = pixmap.scaled(
                    100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                circular_pixmap = self.make_circular(scaled_pixmap)
                self.local_avatar_label.setPixmap(circular_pixmap)

                self.local_image_label.setText(
                    f"Local Image: SUCCESS ({pixmap.width()}x{pixmap.height()})")
                return True

        except Exception as e:
            print(f"❌ Exception loading local image: {e}")
            self.local_image_label.setText(f"Local Image: ERROR - {e}")
            return False

    def test_network_image(self):
        """Test loading image from network"""
        try:
            print("Testing network image loading...")

            # Get profile data first
            url = f"{CANVAS_BASE_URL}/api/v1/users/self/profile"
            headers = {
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                profile_data = response.json()
                avatar_url = profile_data.get('avatar_url', '')

                if avatar_url:
                    print(f"Got avatar URL: {avatar_url}")
                    request = QNetworkRequest(QUrl(avatar_url))
                    self.network_manager.get(request)
                    self.status_label.setText("Loading network image...")
                    return True
                else:
                    print("❌ No avatar URL found")
                    self.network_image_label.setText("Network Image: No URL")
                    return False
            else:
                print(f"❌ API request failed: {response.status_code}")
                self.network_image_label.setText(
                    f"Network Image: API Error {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Exception in network test: {e}")
            self.network_image_label.setText(f"Network Image: ERROR - {e}")
            return False

    def on_image_loaded(self, reply):
        """Handle loaded network image data"""
        try:
            if reply.error() == reply.NoError:
                data = reply.readAll()
                pixmap = QPixmap()

                print(f"Received {len(data)} bytes from network")

                if pixmap.loadFromData(data):
                    print(
                        f"✅ Network image loaded: {pixmap.width()}x{pixmap.height()}")

                    # Scale and make circular
                    scaled_pixmap = pixmap.scaled(
                        100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    circular_pixmap = self.make_circular(scaled_pixmap)
                    self.network_avatar_label.setPixmap(circular_pixmap)

                    self.network_image_label.setText(
                        f"Network Image: SUCCESS ({pixmap.width()}x{pixmap.height()})")
                    self.status_label.setText("✅ All tests completed!")
                else:
                    print("❌ Failed to load image from network data")
                    self.network_image_label.setText(
                        "Network Image: Data Load Failed")
                    self.status_label.setText("❌ Network image data invalid")
            else:
                error_msg = reply.errorString()
                print(f"❌ Network error: {error_msg}")
                self.network_image_label.setText(
                    f"Network Image: Network Error")
                self.status_label.setText(f"❌ Network error: {error_msg}")

        except Exception as e:
            print(f"❌ Exception processing network image: {e}")
            self.network_image_label.setText(f"Network Image: Process Error")
            self.status_label.setText(f"❌ Process error: {e}")
        finally:
            reply.deleteLater()

    def test_image_loading(self):
        """Run all image loading tests"""
        print("Starting Qt image loading tests...")

        # Test local image first
        local_success = self.test_local_image()

        # Test network image
        if local_success:
            self.test_network_image()
        else:
            self.status_label.setText(
                "❌ Local test failed, skipping network test")


def main():
    app = QApplication(sys.argv)

    print("=" * 50)
    print("Qt Profile Image Loading Test")
    print("=" * 50)

    # Check if local image exists
    import os
    if not os.path.exists("profile_picture.jpg"):
        print("❌ profile_picture.jpg not found!")
        print("Run test_profile_picture.py first to download the image.")
        return

    window = ProfileImageTest()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
