from PyQt6.QtWidgets import QApplication
from interface import MainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.setWindowTitle("Определение реакций опор")
    window.show()
    sys.exit(app.exec())