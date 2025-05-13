import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

class QuboxWelcome(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle("Welcome")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Add logo - look in the docs folder at project root
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "blochlogo.png")
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("Logo not found")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Add title
        title = QLabel("QUBOX")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add subtitle
        subtitle = QLabel("A Visual Tool for Quantum Circuit Design and Simulation")
        subtitle_font = QFont("Arial", 12)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Add click instruction
        click_label = QLabel("Click anywhere to start")
        click_font = QFont("Arial", 10, QFont.Weight.Light)
        click_label.setFont(click_font)
        click_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(click_label)
        
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
        """)
    
    def mousePressEvent(self, event):
        self.close()
    
    @staticmethod
    def show_welcome(parent=None):
        dialog = QuboxWelcome(parent)
        dialog.exec()
