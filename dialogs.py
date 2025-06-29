from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QMessageBox
)
from structures import *

# Умная конвертация числа в строку:
# если число является целым (например, 3.0), то оно преобразуется в '3', а не '3.0'.
def smart_str(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

# Базовый класс диалогового окна, который используется как шаблон
class BaseDialog(QDialog):
    def __init__(self, title, labels, input_widgets, parent=None, default_values=None):
        super().__init__(parent)
        self.setWindowTitle(title)  # Заголовок окна
        self.inputs = input_widgets  # Список виджетов ввода
        self._data = None  # Здесь будут храниться валидированные данные

        for widget in self.inputs:
            if isinstance(widget, QLineEdit):
                widget.setStyleSheet("background-color: #f3e0dc; color: #000000;")  # белый фон, чёрный текст
            elif isinstance(widget, QComboBox):
                widget.setStyleSheet("background-color: #f3e0dc; color: 000000;")  # аналогично
            elif isinstance(widget, QCheckBox):
                # QCheckBox обычно не имеет фонового цвета для всего виджета, но можно попробовать:
                widget.setStyleSheet("color: #000000;")  # цвет текста чекбокса

        layout = QVBoxLayout()

        # Создаём строки ввода с соответствующими подписями
        for label, input_widget in zip(labels, self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))  # Подпись
            row.addWidget(input_widget)  # Поле ввода
            layout.addLayout(row)

        # Установка значений по умолчанию, если заданы
        if default_values:
            self.set_defaults(default_values)

        # Кнопка подтверждения
        button_ok = QPushButton("ОК")
        button_ok.setStyleSheet("background-color: #f3e0dc")
        button_ok.clicked.connect(self.validate_and_accept)
        layout.addWidget(button_ok)

        self.setStyleSheet("background-color: #d4a59a;")

        self.setLayout(layout)

    # Устанавливает значения по умолчанию в поля
    def set_defaults(self, default_values):
        for widget, value in zip(self.inputs, default_values):
            if isinstance(widget, QLineEdit):
                widget.setText(smart_str(value))
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(value)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))

    # Заглушка для валидации и обработки нажатия "ОК"
    def validate_and_accept(self):
        pass

    # Метод для получения данных после закрытия диалога
    def get_data(self):
        return self._data

# Диалог добавления сегмента балки
class BeamSegmentDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить сегмент балки", ["X1:", "Y1:", "X2:", "Y2:"],
                         [QLineEdit() for _ in range(4)], parent, default_values)

    # Валидация и извлечение координат
    def validate_and_accept(self):
        try:
            self._data = [float(field.text()) for field in self.inputs]
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

# Диалог добавления опоры
class SupportDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        combo = QComboBox()
        combo.addItems(["Жёсткая заделка", "Шарнирно-неподвижная", "Шарнирно-подвижная"])
        super().__init__("Добавить опору", ["Номер узла:", "Тип опоры:", "Угол:"],
                         [QLineEdit(), combo, QLineEdit()], parent, default_values)

    # Валидация ввода номера узла, типа опоры и угла
    def validate_and_accept(self):
        try:
            node_number = int(self.inputs[0].text())
            support_type = self.inputs[1].currentIndex()
            angle = float(self.inputs[2].text())
            self._data = (node_number, support_type, angle)
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

# Диалог добавления силы
class ForceDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить силу", ["Номер балки:", "Отступ:", "Значение:", "Угол:", "Распределённая:", "Длина"],
                         [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QCheckBox(), QLineEdit()], parent, default_values)

        # При изменении состояния чекбокса — включаем/отключаем поле длины
        self.inputs[4].stateChanged.connect(self.toggle_length_field)
        self.toggle_length_field()

    # Включение/отключение поля "Длина" в зависимости от состояния "Распределённая"
    def toggle_length_field(self):
        self.inputs[5].setEnabled(self.inputs[4].isChecked())

    # Валидация данных о силе
    def validate_and_accept(self):
        try:
            segment_number = int(self.inputs[0].text())
            offset = float(self.inputs[1].text())
            value = float(self.inputs[2].text())
            angle = float(self.inputs[3].text())
            length = float(self.inputs[5].text()) if self.inputs[4].isChecked() else 1
            self._data = (segment_number, offset, value, angle, length)
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

# Диалог добавления момента
class TorqueDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить момент", ["Номер балки:", "Отступ:", "Значение:"],
                         [QLineEdit(), QLineEdit(), QLineEdit()], parent, default_values)

    # Валидация данных для момента
    def validate_and_accept(self):
        try:
            segment_number = int(self.inputs[0].text())
            offset = float(self.inputs[1].text())
            value = float(self.inputs[2].text())
            self._data = (segment_number, offset, value)
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))


class HingeDialog(BaseDialog):
        def __init__(self, parent=None, default_values=None):
            super().__init__("Добавить шарнир", ["Номер узла:"], [QLineEdit()], parent, default_values)

        def validate_and_accept(self):
            try:
                node_id = int(self.inputs[0].text())
                self._data = (node_id)
                self.accept()
            except Exception:
                QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

class SolveDialog(QDialog):
    def __init__(self, answers: dict[str, float], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результаты расчёта")

        layout = QVBoxLayout()

        # Для каждого результата создаём строку с меткой и полем (только для чтения)
        for key, value in answers.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key}:"))
            result_field = QLineEdit(str(f"{value:.2f}"))
            result_field.setReadOnly(True)
            row.addWidget(result_field)
            layout.addLayout(row)

        # Кнопка закрытия окна
        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)

# Класс, управляющий открытием диалогов и обработкой их результатов
class DialogManager:
    def __init__(self, grid_widget):
        self.grid_widget = grid_widget  # Ссылка на виджет с графиком/сценой

    # Общий метод для открытия диалогов с обработкой ошибок
    def open_dialog(self, dialog_class, apply_func):
        default_data = None
        while True:
            dialog = dialog_class(None, default_data)
            if not dialog.exec():  # Если диалог закрыт, выходим
                break
            try:
                apply_func(dialog.get_data())  # Пытаемся применить данные
                self.grid_widget.update()
                break
            except Exception as e:
                QMessageBox.critical(None, "Ошибка!", str(e))
                default_data = dialog.get_data()  # Сохраняем данные для повторного использования

    # Методы открытия конкретных диалогов:

    def open_segment_dialog(self):
        self.open_dialog(
            BeamSegmentDialog,
            lambda data: self.grid_widget.beam.add_segment(
                BeamSegment(Node(data[0], data[1]), Node(data[2], data[3]))
            )
        )

    def open_support_dialog(self):
        def apply(data):
            node_number, support_type_index, angle = data
            if node_number < 1 or node_number not in self.grid_widget.node_mapping:
                raise NonExistentError(f"Узел {node_number} не существует!")
            ufx = support_type_index != Support.Type.ROLLER.value
            ut = support_type_index == Support.Type.FIXED.value
            self.grid_widget.node_mapping[node_number].add_support(Support(Support.Type(support_type_index), angle, 0, 0, 0, ufx, True, ut))
            self.grid_widget.node_mapping[node_number].hinge = None


        self.open_dialog(SupportDialog, apply)

    def open_force_dialog(self):
        def apply(data):
            segment_number, offset, value, angle, length = data
            if segment_number not in self.grid_widget.segment_mapping:
                raise NonExistentError(f"Сегмент балки {segment_number} не существует!")
            self.grid_widget.segment_mapping[segment_number].add_force(
                Force(value, angle, offset, length, False)
            )

        self.open_dialog(ForceDialog, apply)

    def open_torque_dialog(self):
        def apply(data):
            segment_number, offset, value = data
            if segment_number not in self.grid_widget.segment_mapping:
                raise NonExistentError(f"Сегмент балки {segment_number} не существует!")
            self.grid_widget.segment_mapping[segment_number].add_torque(
                Torque(value, offset, False)
            )

        self.open_dialog(TorqueDialog, apply)

    def open_hinge_dialog(self):
        def apply(data):
            node_number = data
            if node_number < 1 or node_number not in self.grid_widget.node_mapping:
                raise NonExistentError(f"Узел {node_number} не существует!")
            node = self.grid_widget.node_mapping[node_number].add_hinge()
            self.grid_widget.node_mapping[node_number].support = None

        self.open_dialog(HingeDialog, apply)


    def open_solve_dialog(self):
        try:
            solve = self.grid_widget.beam.solve()  # Получаем результат
            dialog = SolveDialog(solve)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка!", str(e))