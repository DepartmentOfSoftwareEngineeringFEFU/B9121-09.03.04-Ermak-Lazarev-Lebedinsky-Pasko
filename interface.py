"""
interface.py — построение главного окна приложения.

Определяет класс MainWindow, содержащий компоновку интерфейса:
панель инструментов, графическое поле для схемы балки, кнопки управления,
и диалоги добавления элементов.

Зависит от:
- grid.py для холста;
- dialogs.py для ввода параметров;
- structures.py для хранения модели;
- PyQt6 для UI-компонентов.
"""

# Импорт необходимых классов из PyQt6 для создания графического интерфейса
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)

from structures import *
from grid import GridWidget
from dialogs import DialogManager
from serialization import *

# Импорт пользовательских классов и модулей
from structures import *          # Содержит определения структур: Beam, Node, Force, и т.д.
from grid import GridWidget       # Отвечает за отрисовку координатной плоскости и балки
from dialogs import DialogManager # Управляет диалогами для добавления элементов и решения задачи


# Главный виджет приложения
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Основной горизонтальный макет интерфейса (делит окно на левую панель и область рисования)
        layout = QHBoxLayout()

        # Виджет для отрисовки балки и элементов на координатной плоскости
        self.grid_widget = GridWidget()

        # Менеджер диалогов, получает ссылку на grid_widget для взаимодействия
        self.dialogs = DialogManager(self.grid_widget)

        # Вертикальный макет для кнопок на левой панели
        left_layout = QVBoxLayout()

        # Кнопка добавления сегмента балки
        add_segment_button = QPushButton("Добавить сегмент балки")
        add_segment_button.setMinimumHeight(40)
        add_segment_button.setMinimumWidth(180)
        add_segment_button.setStyleSheet("background-color: #f3e0dc")
        add_segment_button.clicked.connect(self.dialogs.open_segment_dialog)  # Открывает диалог добавления сегмента
        left_layout.addWidget(add_segment_button)

        # Кнопка добавления опоры
        add_support_button = QPushButton("Добавить опору")
        add_support_button.setMinimumHeight(40)
        add_support_button.setMinimumWidth(180)
        add_support_button.setStyleSheet("background-color: #f3e0dc")
        add_support_button.clicked.connect(self.dialogs.open_support_dialog)  # Открывает диалог добавления опоры
        left_layout.addWidget(add_support_button)

        # Кнопка добавления силы
        add_force_button = QPushButton("Добавить силу")
        add_force_button.setMinimumHeight(40)
        add_force_button.setMinimumWidth(180)
        add_force_button.setStyleSheet("background-color: #f3e0dc")
        add_force_button.clicked.connect(self.dialogs.open_force_dialog)  # Открывает диалог добавления силы
        left_layout.addWidget(add_force_button)

        # Кнопка добавления момента (торка)
        add_torque_button = QPushButton("Добавить момент")
        add_torque_button.setMinimumHeight(40)
        add_torque_button.setMinimumWidth(180)
        add_torque_button.setStyleSheet("background-color: #f3e0dc")
        add_torque_button.clicked.connect(self.dialogs.open_torque_dialog)  # Открывает диалог добавления момента
        left_layout.addWidget(add_torque_button)

        add_hinge_button = QPushButton("Добавить шарнир")
        add_hinge_button.clicked.connect(self.dialogs.open_hinge_dialog)
        left_layout.addWidget(add_hinge_button)

        solve_button = QPushButton("Посчитать")
        solve_button.setMinimumHeight(40)
        solve_button.setMinimumWidth(180)
        solve_button.setStyleSheet("background-color: #f3e0dc")
        solve_button.clicked.connect(self.dialogs.open_solve_dialog)  # Открывает диалог расчёта
        left_layout.addWidget(solve_button)

        # Кнопка сброса смещения (перемещения) координатной плоскости
        reset_offset_button = QPushButton("Вернуться к началу координат")
        reset_offset_button.setMinimumHeight(40)
        reset_offset_button.setMinimumWidth(180)
        reset_offset_button.setStyleSheet("background-color: #f3e0dc")
        reset_offset_button.clicked.connect(self.grid_widget.resetOffset)  # Сброс смещения
        left_layout.addWidget(reset_offset_button)

        # Кнопка очистки всех элементов с поля
        clear_button = QPushButton("Очистить поле")
        clear_button.setMinimumHeight(40)
        clear_button.setMinimumWidth(180)
        clear_button.setStyleSheet("background-color: #f3e0dc")
        clear_button.clicked.connect(self.clear_button_message)  # Подтверждение и очистка
        left_layout.addWidget(clear_button)

        # Кнопка сохранения балки в файл
        save_button = QPushButton("Сохранить балку")
        save_button.setMinimumHeight(40)
        save_button.setMinimumWidth(180)
        save_button.setStyleSheet("background-color: #f3e0dc")
        save_button.clicked.connect(self.save_beam)  # Сохраняет beam в файл формата .bm
        left_layout.addWidget(save_button)

        # Кнопка загрузки балки из файла
        load_button = QPushButton("Загрузить балку")
        load_button.setMinimumHeight(40)
        load_button.setMinimumWidth(180)
        load_button.setStyleSheet("background-color: #f3e0dc")
        load_button.clicked.connect(self.load_beam)  # Загружает beam из файла .bm
        left_layout.addWidget(load_button)

        # Обёртка для левой панели, фиксируем ширину
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(200)  # Панель шириной 200px
        left_widget.setStyleSheet("background-color: #d4a59a;")  

        # Добавление панелей в основной макет
        layout.addWidget(left_widget)         # Левая панель с кнопками
        layout.addWidget(self.grid_widget)    # Область отрисовки

        # Применение макета к основному окну
        self.setLayout(layout)


    # Метод для сохранения текущей балки в файл
    def save_beam(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить балку",         # Заголовок окна
            "",                        # Путь по умолчанию
            "Файлы балки (*.bm);;Все файлы (*)"  # Фильтр файлов
        )
        if filename:  # Если пользователь выбрал файл
            if not filename.endswith(".bm"):
                filename += ".bm"  # Добавляем расширение, если его нет

            try:
                save_beam_to_file(self.grid_widget.beam, filename)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", str(e))  # Ошибка при сохранении


    # Метод для загрузки балки из файла
    def load_beam(self):
        # Если на поле уже есть элементы, подтверждаем удаление текущей балки
        if len(self.grid_widget.beam.graph.nodes) > 0:
            box = QMessageBox(self)
            box.setWindowTitle("Подтверждение загрузки")
            box.setText("Вы хотите загрузить другую балку? Текущая балка будет удалена.")
            button_yes = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
            button_no = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            button_yes.setStyleSheet("background-color: #f3e0dc")
            button_no.setStyleSheet("background-color: #f3e0dc")
            box.setStyleSheet("background-color: #d4a59a;")  
            box.exec()

            if box.clickedButton() != button_yes:

                return

        # Диалог выбора файла
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить балку",
            "",
            "Файлы балки (*.bm);;Все файлы (*)"
        )
        if not filename:
            return

        try:
            self.clear_field()
            load_beam_from_file(filename, self.grid_widget.beam)
            self.grid_widget.update()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))  # Ошибка при загрузке


    # Метод с подтверждением очистки поля
    def clear_button_message(self):
        box = QMessageBox(self)
        box.setWindowTitle("Подтверждение очистки")
        box.setText("Вы уверены, что хотите очистить поле?")
        button_yes = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        button_no = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        button_yes.setStyleSheet("background-color: #f3e0dc")
        button_no.setStyleSheet("background-color: #f3e0dc")
        box.setStyleSheet("background-color: #d4a59a;")  
        box.exec()

        if box.clickedButton() == button_yes:
            self.clear_field()  # Очистка подтверждена


    # Метод, полностью очищающий поле от элементов и сбрасывающий ID
    def clear_field(self):
        for cls in [Force, Torque, Support, Hinge, Node, BeamSegment, Beam]:
            cls._next_id = 1
            cls._used_ids.clear()

        # Создание новой пустой балки
        self.grid_widget.beam = Beam()

        # Обновление отображения
        self.grid_widget.update()