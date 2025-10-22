import sys
import subprocess
import os
import signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget, QTextEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QIcon, QTextCursor
from PyQt5.QtCore import Qt, QTimer
import requests
import pandas as pd

class QuantumShieldGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize Matplotlib Figure and Canvas
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Window Setup
        self.setWindowTitle('Quantum Shield')
        self.setWindowIcon(QIcon('images/icon48.png'))  # Logo for the app
        self.setGeometry(1000, 600, 400, 300)  # Window size

        # Custom Font and Project Title (Phishing Detector)
        self.setStyleSheet("background-color: #e7e4f9;")  # Slightly brighter background

        # Header Title "Phishing Detector"
        self.title_label = QLabel('Phishing Detector', self)
        self.title_label.setFont(QFont('Roboto', 24))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet('color: #5300ab; padding: 20px;')  # Purple color, tech look

        # Circular Activate/Deactivate Button
        self.toggle_button = QPushButton('Activate', self)
        self.toggle_button.setFont(QFont('Roboto', 14))
        self.toggle_button.setFixedSize(150, 150)  # Ensure fixed size for circular button
        self.toggle_button.setStyleSheet('''
            QPushButton {
                background-color: green;
                color: white;
                font-size: 18px;
                border-radius: 75px;  /* Make the button circular */
            }
            QPushButton:hover {
                background-color: #00cc00;  /* Lighter green when hovered */
            }
            QPushButton:pressed {
                background-color: #006400;
            }
        ''')
        self.toggle_button.clicked.connect(self.toggle_app)

        # Status Indicator - Active/Inactive after the button, aligned left
        self.status_label = QLabel('⦿ Inactive', self)
        self.status_label.setFont(QFont('Roboto', 16))
        self.status_label.setStyleSheet('color: red')  # Default to red for inactive
        self.status_label.setAlignment(Qt.AlignLeft)

        # Shield Activity Button
        self.stats_button = QPushButton('Shield Activity', self)
        self.stats_button.setFont(QFont('Roboto', 11))
        self.stats_button.setFixedSize(120, 40)
        self.stats_button.setStyleSheet('''
            QPushButton {
                border: 2px solid #2e2c9a;  /* Info-colored border */
                border-radius: 8px;  /* Rounded corners */
                background-color: transparent;  /* Transparent background */
                color: #2e2c9a;  /* Info-colored text */
                padding: 5px;
    }
    QPushButton:hover {
        background-color: rgba(46, 44, 154, 0.1);  /* Light transparent background on hover */
        color: #3a2081;  /* Brighter color for text on hover */
        border: 2px solid #3a2081;  /* Brighter border on hover */
    }
    QPushButton:pressed {
        background-color: rgba(46, 44, 154, 0.2);  /* Slightly darker transparent background when pressed */
        color: #120348;  /* Change text color to white when pressed */
        border: 2px solid #120348;  /* Keep border the same brighter color */
    }
        ''')
        self.stats_button.clicked.connect(self.open_stats_window)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)  # Phishing Detector Title
        layout.addWidget(self.toggle_button, alignment=Qt.AlignCenter)  # Center the circular button
        layout.addWidget(self.status_label, alignment=Qt.AlignLeft)  # Align the status to the left
        layout.addWidget(self.stats_button, alignment=Qt.AlignLeft)  # Center the Shield Activity button
        self.setLayout(layout)

        # Move to bottom right of the screen
        self.move_to_bottom_right()

        # To track if app.py is running
        self.is_active = False
        self.app_process = None  # To store the process of app.py

        # Check the current status of app.py on startup
        self.check_app_status()

    def move_to_bottom_right(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_size = screen_geometry.size()
        window_size = self.size()

        # Adjust X to keep it in the right corner
        x = screen_size.width() - window_size.width() - 7

        # Adjust Y to move the window up a little from the bottom corner
        y = screen_size.height() - window_size.height() - 70  # Adjust as needed

        self.move(x, y)

    def toggle_app(self):
        # Toggle between active/inactive states
        if not self.is_active:
            self.activate_app()
        else:
            self.deactivate_app()

    def activate_app(self):
        # Check if app.py is already running by querying the status endpoint
        try:
            response = requests.get('http://127.0.0.1:5000/status')
            if response.status_code == 200:
                print("App is already running")
                self.is_active = True
                self.update_ui_active()
                return  # App is already active, no need to restart

        except Exception:
            print("starting app.py...")

        # If app.py is not running, start it
        try:
            if sys.platform == "win32":
                self.app_process = subprocess.Popen(
                    ['python', 'app.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW  # Suppress the Command Prompt window
                )
            else:
                self.app_process = subprocess.Popen(
                    ['python3', 'app.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # For Unix-like systems to allow termination
                )
            self.is_active = True
            self.update_gui_state()

        except Exception as e:
            print(f"Error starting app.py: {e}")
            self.is_active = False

    def deactivate_app(self):
        # Terminate the process if app.py is running
        if self.app_process and self.app_process.poll() is None:
            print("Stopping app.py...")
            try:
                # Use os.kill with SIGTERM for cross-platform compatibility
                if os.name == 'nt':  # For Windows
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.app_process.pid)])
                else:  # For Unix/Linux systems
                    os.killpg(os.getpgid(self.app_process.pid), signal.SIGTERM)
                self.app_process.wait()  # Ensure it's terminated
            except Exception as e:
                print(f"Error while stopping app.py: {e}")
            finally:
                self.is_active = False
                self.update_gui_state()
        else:
            print("No app.py process found to stop.")

    def check_app_status(self):
        # Check if app.py is running on startup
        try:
            response = requests.get('http://127.0.0.1:5000/status')
            if response.status_code == 200:
                self.is_active = True
                self.update_gui_state()
            else:
                self.is_active = False
                self.update_gui_state()
        except:
            self.is_active = False
            self.update_gui_state()

    def update_gui_state(self):
        # Update button and status label based on whether app.py is active
        if self.is_active:
            self.toggle_button.setText('Deactivate')
            self.toggle_button.setStyleSheet('''
                QPushButton {
                    background-color: #e2160f;
                    color: white;
                    font-size: 18px;
                    border-radius: 75px;
                    border: 4px solid #bb120c;
                }
                QPushButton:hover {
                    background-color: #fd3a36;  /* Lighter red when hovered */
                }
                QPushButton:pressed {
                    background-color: #8B0000;
                }
            ''')
            self.status_label.setText('⦿ Active')
            self.status_label.setStyleSheet('color: green')
        else:
            self.toggle_button.setText('Activate')
            self.toggle_button.setStyleSheet('''
                QPushButton {
                    background-color: #3a2081;
                    color: white;
                    font-size: 18px;
                    border-radius: 75px;                        
                    border: 4px solid #2e2c9a;
                }
                QPushButton:hover {
                    background-color: #4d2bab;
                }                             
                QPushButton:pressed {
                    background-color: #3a2081;
                }
            ''')
            self.status_label.setText('⦿ Inactive')
            self.status_label.setStyleSheet('color: red')

    def open_stats_window(self):
        # Create a new window to display Shield Activity
        self.stats_window = QWidget()
        self.stats_window.setWindowTitle('Shield Activity')
        self.stats_window.setWindowIcon(QIcon('images/icon48.png'))
        
        # Create a QTabWidget to hold tabs
        tab_widget = QTabWidget()

        # Create the dataset tab with a better layout
        self.dataset_tab = QWidget()
        dataset_layout = QVBoxLayout()
        # Add a header label for the dataset
        header_label = QLabel("Phishing Dataset Statistics")
        header_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 6px;")  # Customize the style as needed
        dataset_layout.addWidget(header_label)
        # Create a label to show the phishing URL count
        self.dataset_info_label = QLabel("")
        self.dataset_info_label.setStyleSheet("font-size: 14px;")  # Customize the style as needed
        dataset_layout.addWidget(self.dataset_info_label)

        # Add the Matplotlib canvas to the layout for the graphs
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        dataset_layout.addWidget(self.canvas)

        self.dataset_tab.setLayout(dataset_layout)

        # Create the Logs tab
        self.logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        self.logs_area = QTextEdit(self.logs_tab)
        self.logs_area.setReadOnly(True)
        logs_layout.addWidget(self.logs_area)
        self.logs_tab.setLayout(logs_layout)

        # Add tabs to the QTabWidget
        tab_widget.addTab(self.dataset_tab, "Phishing Dataset")
        tab_widget.addTab(self.logs_tab, "Logs")

        # Layout for the Shield Activity window
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(tab_widget)
        self.stats_window.setLayout(stats_layout)
        self.stats_window.resize(535, 335)

        # Get the position of the main window
        main_window_geometry = self.geometry()

        # Set the Shield Activity window to open beside the main window (to the left)
        stats_x = main_window_geometry.x() - self.stats_window.width() - 10  # 10 pixels of spacing to the left
        stats_y = main_window_geometry.y() - self.stats_window.height() + 303

        # Move the stats window to the left of the main window
        self.stats_window.move(stats_x, stats_y)

        # Start a timer to update logs every second in real-time
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(1000)  # Update every second

        # Load the phishing dataset and display statistics
        self.update_dataset_stats()

        # Show the stats window
        self.stats_window.show()

    def update_log(self):
        # Update the logs in the stats window in real-time, showing new logs
        log_file = 'app_logs.log'
        try:
            # Open the log file and read all lines
            with open(log_file, 'r') as f:
                logs = f.readlines()

            # If the file contains more than 200 lines, overwrite the file to keep only the last 200 lines
            if len(logs) > 200:
                with open(log_file, 'w') as f:
                    f.writelines(logs[-200:])

            # Read only the last 50 lines to display
            logs_to_display = logs[-50:]
            self.logs_area.setPlainText("".join(logs_to_display))
            self.logs_area.moveCursor(QTextCursor.End)
        except FileNotFoundError:
            self.logs_area.setPlainText("No logs available.")
    
    def update_dataset_stats(self):
        # Load the phishing dataset CSV file
        try:
            dataset_path = 'data/phishing_dataset.csv'
            df = pd.read_csv(dataset_path)

            # Count the number of phishing URLs (where label is 1)
            phishing_count = df[df['label'] == 1].shape[0]
            # Display the number of phishing URLs captured
            dataset_info = f" {phishing_count} Phishing URLs have been captured."
            self.dataset_info_label.setText(dataset_info)

            # Clear the previous figure to avoid overlapping
            self.figure.clear()

            # Generate the bar chart for the most common domains
            ax2 = self.figure.add_subplot(111)
            df['domain'] = df['text'].apply(lambda x: x.split('/')[2] if '//' in x else x.split('/')[0])  # Extract domain
            domain_counts = df['domain'].value_counts().head(10)
            ax2.bar(domain_counts.index, domain_counts.values, color='red')

            # Set x-ticks and labels
            ax2.set_title('Top 10 Phishing Domains', fontsize=10)
            ax2.set_ylabel('Count', fontsize=10)
            ax2.set_xticks(range(len(domain_counts.index)))  # Set the tick positions
            ax2.set_xticklabels(domain_counts.index, rotation=25, ha='right', fontsize=8.5)  # Set the tick labels

            self.canvas.draw()  # Draw the new figure

        except Exception as e:
            # In case of any error, display it in the dataset area
            self.dataset_info_label.setText(f"Error loading dataset: {str(e)}")

    def closeEvent(self, event):
        # Ensure app.py is properly terminated if the GUI is closed
        if self.is_active:
            self.deactivate_app()
        event.accept()  # Close the window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    quantum_shield_gui = QuantumShieldGUI()
    quantum_shield_gui.show()
    sys.exit(app.exec_())
