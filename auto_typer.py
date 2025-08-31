import sys
import time
import pyautogui
from pynput import keyboard
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QSlider, QHBoxLayout, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Global variable
typing_active = False


class TyperThread(QThread):
    """ Thread to handle typing in the background """
    finished = pyqtSignal()  # Signal when typing is done

    def __init__(self, text, speed):
        super().__init__()
        self.text = text
        self.speed = speed

    def run(self):
        global typing_active
        typing_active = True
        for char in self.text:
            if not typing_active:
                break
            pyautogui.typewrite(char)
            time.sleep(self.speed)
        typing_active = False  # Auto-reset after completion
        self.finished.emit()  # Notify the GUI


class AutoTyperGUI(QWidget):
    """ Main GUI class """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Automatic Typer")
        self.setGeometry(100, 100, 500, 300)

        # Layouts
        layout = QVBoxLayout()

        # Label for instruction
        self.label = QLabel("Enter text to type:", self)
        layout.addWidget(self.label)

        # Textbox to enter text
        self.text_area = QTextEdit(self)
        layout.addWidget(self.text_area)

        # Speed slider
        speed_layout = QHBoxLayout()
        self.speed_label = QLabel("Typing Speed:", self)
        speed_layout.addWidget(self.speed_label)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_slider.setMinimum(1)  # Fastest speed
        self.speed_slider.setMaximum(100)  # Slowest speed
        self.speed_slider.setValue(50)
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        speed_layout.addWidget(self.speed_slider)

        self.speed_display = QLabel("Speed: 50", self)
        speed_layout.addWidget(self.speed_display)

        layout.addLayout(speed_layout)

        # Delay before typing starts
        delay_layout = QHBoxLayout()
        self.delay_label = QLabel("Start Delay (seconds):", self)
        delay_layout.addWidget(self.delay_label)

        self.delay_spinner = QSpinBox(self)
        self.delay_spinner.setMinimum(0)
        self.delay_spinner.setMaximum(10)
        self.delay_spinner.setValue(2)
        delay_layout.addWidget(self.delay_spinner)

        layout.addLayout(delay_layout)

        # Start and Stop buttons
        self.start_button = QPushButton("Start Typing (F9)", self)
        self.start_button.clicked.connect(self.start_typing)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Typing (F10)", self)
        self.stop_button.clicked.connect(self.stop_typing)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Thread for typing
        self.typer_thread = None

        # Hotkey listener
        self.hotkey_listener = keyboard.Listener(on_press=self.on_hotkey)
        self.hotkey_listener.start()

    def update_speed_label(self):
        """ Update the speed label dynamically based on the slider """
        speed = self.speed_slider.value()
        self.speed_display.setText(f"Speed: {speed}")

    def start_typing(self):
        """ Starts the typing process """
        global typing_active

        if typing_active:
            return

        text = self.text_area.toPlainText()
        if not text:
            self.label.setText("⚠️ Enter text first!")
            return

        speed = (100 - self.speed_slider.value()) / 100  # Convert slider to delay
        delay = self.delay_spinner.value()

        self.label.setText(f"⏳ Typing starts in {delay} seconds...")

        time.sleep(delay)  # Wait before starting
        self.label.setText("✍️ Typing in progress...")

        self.typer_thread = TyperThread(text, speed)
        self.typer_thread.finished.connect(self.typing_done)
        self.typer_thread.start()

    def stop_typing(self):
        """ Stops the typing process """
        global typing_active
        typing_active = False
        self.label.setText("⏹️ Typing stopped.")

    def typing_done(self):
        """ Callback when typing is completed """
        global typing_active
        typing_active = False  # Ensure typing state resets
        self.label.setText("✅ Typing completed! Ready for next.")

    def on_hotkey(self, key):
        """ Handles hotkey presses """
        try:
            if key == keyboard.Key.f9:
                self.start_typing()
            elif key == keyboard.Key.f10:
                self.stop_typing()
        except AttributeError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoTyperGUI()
    window.show()
    sys.exit(app.exec())
