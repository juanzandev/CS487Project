#!/usr/bin/env python3
"""
Canvas Grade Widget - PySide6 Desktop Widget
Displays Canvas courses and grades in a desktop widget
"""

import sys
import requests
import json
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QScrollArea, QFrame)
from PySide6.QtCore import Qt, QPoint, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QPalette

# Import Canvas API Configuration
try:
    from config import CANVAS_BASE_URL, API_TOKEN
except ImportError:
    print("Error: config.py not found!")
    print("Please copy config.example.py to config.py and add your API token.")
    sys.exit(1)


class CanvasAPIWorker(QThread):
    """Worker thread for Canvas API calls to prevent UI freezing"""
    courses_fetched = Signal(list)
    error_occurred = Signal(str)

    def run(self):
        try:
            courses = self.get_canvas_courses()
            if courses:
                # Fetch grades for each course
                for course in courses:
                    grade_info = self.get_course_grade(course['id'])
                    course['grade_info'] = grade_info
                self.courses_fetched.emit(courses)
            else:
                self.error_occurred.emit("Failed to fetch courses")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")

    def get_canvas_courses(self):
        """Fetches all courses from Canvas API"""
        url = f"{CANVAS_BASE_URL}/api/v1/courses"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
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
        url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/enrollments"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
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


class CourseWidget(QFrame):
    """Widget to display a single course with grade"""

    def __init__(self, course_data):
        super().__init__()
        self.course_data = course_data
        self.initUI()

    def initUI(self):
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 2px;
                padding: 5px;
            }
            QLabel {
                border: none;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)

        # Course name
        name = self.course_data.get('name', 'Unknown Course')
        print(f"Debug - Course name: '{name}'")  # Debug print

        if len(name) > 50:  # Truncate long names
            name = name[:47] + "..."

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_label.setWordWrap(True)
        name_label.setStyleSheet(
            "border: none; color: black;")  # Ensure visibility

        # Term information only (course name is already displayed above)
        term = "Unknown term"
        if 'term' in self.course_data and self.course_data['term']:
            term = self.course_data['term'].get('name', 'Unknown term')

        info_label = QLabel(term)
        info_label.setFont(QFont("Arial", 8))
        info_label.setStyleSheet("color: #666; border: none;")

        # Grade information
        grade_label = self.create_grade_label()

        layout.addWidget(name_label)
        layout.addWidget(info_label)
        layout.addWidget(grade_label)

        self.setLayout(layout)

    def create_grade_label(self):
        """Create grade label with appropriate styling"""
        grade_info = self.course_data.get('grade_info')

        if not grade_info:
            grade_label = QLabel("Grade: Not available")
            grade_label.setStyleSheet("color: #888; font-size: 9px;")
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
            grade_label.setStyleSheet("color: #888; font-size: 9px;")
            return grade_label

        grade_label = QLabel(grade_text)
        grade_label.setFont(QFont("Arial", 9, QFont.Bold))

        # Color coding based on grade
        if score >= 90:
            color = "#2E7D32"  # Green
        elif score >= 80:
            color = "#F57C00"  # Orange
        elif score >= 70:
            color = "#D32F2F"  # Red
        else:
            color = "#B71C1C"  # Dark red

        grade_label.setStyleSheet(f"color: {color}; font-size: 9px;")

        return grade_label


class CanvasGradeWidget(QWidget):
    """Main desktop widget for Canvas grades"""

    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.courses = []
        self.initUI()
        self.setup_refresh_timer()
        self.refresh_data()

    def initUI(self):
        # Window properties for desktop widget behavior
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint
        )

        self.setGeometry(100, 100, 350, 500)
        self.setWindowOpacity(0.95)

        # Main styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 2px solid #2196F3;
                border-radius: 8px;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Header with title and controls
        header_layout = QHBoxLayout()

        title_label = QLabel("Canvas Grades")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; border: none;")

        # Refresh button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(25, 25)
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setToolTip("Refresh grades")

        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(25, 25)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                color: red;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(close_button)

        # Status label
        self.status_label = QLabel("Loading courses...")
        self.status_label.setStyleSheet(
            "color: #666; font-size: 10px; border: none;")
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
        self.status_label.setText("Refreshing courses...")
        self.refresh_button.setEnabled(False)

        # Start API worker thread
        self.api_worker = CanvasAPIWorker()
        self.api_worker.courses_fetched.connect(self.on_courses_fetched)
        self.api_worker.error_occurred.connect(self.on_error)
        self.api_worker.start()

    def on_courses_fetched(self, courses):
        """Handle successful course fetch"""
        self.courses = courses
        self.display_courses()
        self.status_label.setText(f"Last updated: {self.get_current_time()}")
        self.refresh_button.setEnabled(True)

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
    app = QApplication(sys.argv)

    # Create and show the widget
    widget = CanvasGradeWidget()
    widget.show()

    # Make sure it starts below other windows
    widget.lower()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
