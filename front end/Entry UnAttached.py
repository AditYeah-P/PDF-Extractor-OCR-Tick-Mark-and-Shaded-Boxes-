import sys
import csv
import os
import json
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTextEdit, QLabel, 
                             QFileDialog, QMessageBox, QScrollArea, QFrame,
                             QInputDialog, QDialog)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class ProfileCard(QFrame):
    clicked = pyqtSignal(str)
    
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        self.setLayout(layout)
        self.setFixedHeight(100)  # Set only fixed height, allow width to stretch
        self.setStyleSheet("""
            QFrame {
                background-color: #45b7ae;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
        """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)

class ProfileSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Profile Selector")
        self.setStyleSheet("background-color: #4ECDC4;")
        self.setFixedSize(800, 600)  # Set fixed size to 800x600
        
        layout = QVBoxLayout()
        
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()  # Change back to QVBoxLayout for vertical scrolling
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align cards to the top
        self.scroll_layout.setSpacing(10)  # Add some space between cards
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        add_button = QPushButton("+")
        add_button.setFixedSize(50, 50)  # Slightly smaller button to fit the new window size
        add_button.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        add_button.clicked.connect(self.add_profile)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #45b7ae;
                color: white;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #3da69e;
            }
        """)
        
        layout.addWidget(self.scroll_area)
        layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)

    def add_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and name:
            card = ProfileCard(name)
            card.clicked.connect(self.open_profile)
            self.scroll_layout.addWidget(card)
            self.profiles.append({"name": name, "data": None})

    def open_profile(self, name):
        for profile in self.profiles:
            if profile["name"] == name:
                self.data_viewer = DataViewer(profile)
                self.data_viewer.show()
                break

class ChartWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bar Chart")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(toolbar)
        
        save_button = QPushButton("Save Image")
        save_button.clicked.connect(self.save_image)
        layout.addWidget(save_button)
        
        self.setLayout(layout)

    def plot_bar_chart(self, data, column):
        self.ax.clear()
        data.plot(kind='bar', ax=self.ax)
        self.ax.set_title(f'Bar Chart for {column}')
        self.ax.set_xlabel('Options')
        self.ax.set_ylabel('Count')
        plt.tight_layout()
        self.canvas.draw()

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.figure.savefig(file_path)
            QMessageBox.information(self, "Success", "Image saved successfully!")

class DataViewer(QWidget):
    def __init__(self, profile):
        super().__init__()
        self.profile_name = profile["name"]
        self.profile = self.load_profile()
        self.current_row = 0
        self.chart_window = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Data Viewer - {self.profile['name']}")
        self.setStyleSheet("background-color: #4ECDC4;")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Select a CSV file")
        load_button = QPushButton("Load CSV")
        load_button.clicked.connect(self.load_csv)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(load_button)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setMaximumHeight(50)
        
        nav_layout = QHBoxLayout()
        prev_button = QPushButton("<")
        next_button = QPushButton(">")
        prev_button.clicked.connect(self.show_prev)
        next_button.clicked.connect(self.show_next)
        self.row_label = QLabel("Row: 0 / 0")
        nav_layout.addWidget(prev_button)
        nav_layout.addWidget(self.row_label)
        nav_layout.addWidget(next_button)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.text_area)
        layout.addWidget(self.scroll_area)
        layout.addLayout(nav_layout)
        
        self.setLayout(layout)

        if self.profile["data"] is not None:
            self.show_current()
            self.create_radio_buttons()

    def load_profile(self):
        profile_path = f"{self.profile_name}.json"
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
                if profile['data']:
                    profile['data'] = pd.read_json(profile['data'])
                return profile
        else:
            return {"name": self.profile_name, "data": None}

    def save_profile(self):
        profile_copy = self.profile.copy()
        if isinstance(profile_copy['data'], pd.DataFrame):
            profile_copy['data'] = profile_copy['data'].to_json()
        with open(f"{self.profile_name}.json", 'w') as f:
            json.dump(profile_copy, f)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                new_data = pd.read_csv(file_path)
                print(type(new_data))
                if self.profile["data"] is None:
                    self.profile["data"] = new_data
                else:
                    if list(new_data.columns) == list(self.profile["data"].columns):
                        self.profile["data"] = pd.concat([self.profile["data"], new_data], ignore_index=True)
                    else:
                        raise ValueError("CSV structure does not match the existing data")
                self.current_row = 0
                self.show_current()
                self.create_radio_buttons()
                self.save_profile()  # Save the profile after adding new data
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def show_current(self):
        if self.profile["data"] is not None and not self.profile["data"].empty:
            row_data = self.profile["data"].iloc[self.current_row]
            formatted_data = "\n".join([f"{col}: {row_data[col]}" for col in row_data.index])
            self.text_area.setText(formatted_data)
            total_rows = len(self.profile["data"])
            self.row_label.setText(f"Row: {self.current_row + 1} / {total_rows}")

    def show_prev(self):
        if self.profile["data"] is not None and self.current_row > 0:
            self.current_row -= 1
            self.show_current()

    def show_next(self):
        if self.profile["data"] is not None and self.current_row < len(self.profile["data"]) - 1:
            self.current_row += 1
            self.show_current()

    def create_radio_buttons(self):
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
        
        radio_columns = [col for col in self.profile["data"].columns if col.startswith("RADIO_")]
        for col in radio_columns:
            button = QPushButton(col)
            button.clicked.connect(lambda checked, c=col: self.show_bar_chart(c))
            self.scroll_layout.addWidget(button)

    def show_bar_chart(self, column):
        if self.profile["data"] is not None:
            data = self.profile["data"][column].value_counts()
            
            if self.chart_window is None:
                self.chart_window = ChartWindow(self)
            
            self.chart_window.plot_bar_chart(data, column)
            self.chart_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ProfileSelector()
    ex.show()
    sys.exit(app.exec())