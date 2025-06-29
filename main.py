"""
main.py — основной входной модуль приложения.

Инициализирует графическую подсистему, создаёт главное окно и запускает
главный цикл событий приложения. Связывает GUI-интерфейс и модельную часть
через объект MainWindow.

Используемые технологии:
- PyQt6 для GUI;
- interface.py для построения окна и элементов управления.

Запускается как самостоятельный модуль.
"""

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