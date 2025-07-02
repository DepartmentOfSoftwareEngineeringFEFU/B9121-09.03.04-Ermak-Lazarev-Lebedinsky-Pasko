"""
dialogs.py — набор пользовательских диалогов.

Реализует модальные окна для ввода параметров: сегмент балки, опора, сила,
момент, запуск расчёта. Также содержит DialogManager для централизованного
вызова и обработки ошибок.

Используется интерфейсом MainWindow (interface.py).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from structures import *
from errors import IncorrectInputError, NonExistentError

def smart_str(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

def show_styled_error(parent, message):
    box = QMessageBox(parent)
    box.setWindowTitle("Ошибка!")
    box.setText(str(message))
    box.setIcon(QMessageBox.Icon.Critical)
    button_ok = box.addButton("ОК", QMessageBox.ButtonRole.AcceptRole)
    box.setStyleSheet("""
        QPushButton {
            background-color: #f3e0dc;
            color: #000;
        }
    """)
    box.exec()

class BaseDialog(QDialog):
    def __init__(self, title, labels, input_widgets, parent=None, default_values=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.inputs = input_widgets
        self._data = None

        for widget in self.inputs:
            if isinstance(widget, QLineEdit) or isinstance(widget, QComboBox):
                widget.setStyleSheet("background-color: #f3e0dc; color: #000;")
            elif isinstance(widget, QCheckBox):
                widget.setStyleSheet("color: #000;")

        layout = QVBoxLayout()
        for label, input_widget in zip(labels, self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(input_widget)
            layout.addLayout(row)

        if default_values:
            self.set_defaults(default_values)

        button_ok = QPushButton("ОК")
        button_ok.setStyleSheet("background-color: #f3e0dc; color: black;")
        button_ok.clicked.connect(self.validate_and_accept)
        layout.addWidget(button_ok)

        self.setStyleSheet("background-color: #d4a59a;")
        self.setLayout(layout)

    def set_defaults(self, default_values):
        for widget, value in zip(self.inputs, default_values):
            if isinstance(widget, QLineEdit):
                widget.setText(smart_str(value))
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(value)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))

    def validate_and_accept(self):
        pass

    def get_data(self):
        return self._data

class BeamSegmentDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить сегмент балки", ["X1:", "Y1:", "X2:", "Y2:"],
                         [QLineEdit() for _ in range(4)], parent, default_values)

    def validate_and_accept(self):
        try:
            self._data = [float(field.text()) for field in self.inputs]
            self.accept()
        except Exception:
            show_styled_error(self, IncorrectInputError("Введены некорректные данные!"))

class SupportDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        combo = QComboBox()
        combo.addItems(["Жёсткая заделка", "Шарнирно-неподвижная", "Шарнирно-подвижная"])
        super().__init__("Добавить опору", ["Номер узла:", "Тип опоры:", "Угол:"],
                         [QLineEdit(), combo, QLineEdit()], parent, default_values)

    def validate_and_accept(self):
        try:
            node_number = int(self.inputs[0].text())
            support_type = self.inputs[1].currentIndex()
            angle = float(self.inputs[2].text())
            self._data = (node_number, support_type, angle)
            self.accept()
        except Exception:
            show_styled_error(self, IncorrectInputError("Введены некорректные данные!"))

class ForceDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить силу", ["Номер балки:", "Отступ:", "Значение:", "Угол:", "Распределённая:", "Длина"],
                         [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QCheckBox(), QLineEdit()], parent, default_values)
        self.inputs[4].stateChanged.connect(self.toggle_length_field)
        self.toggle_length_field()

    def toggle_length_field(self):
        self.inputs[5].setEnabled(self.inputs[4].isChecked())

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
            show_styled_error(self, IncorrectInputError("Введены некорректные данные!"))

class TorqueDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить момент", ["Номер балки:", "Отступ:", "Значение:"],
                         [QLineEdit(), QLineEdit(), QLineEdit()], parent, default_values)

    def validate_and_accept(self):
        try:
            segment_number = int(self.inputs[0].text())
            offset = float(self.inputs[1].text())
            value = float(self.inputs[2].text())
            self._data = (segment_number, offset, value)
            self.accept()
        except Exception:
            show_styled_error(self, IncorrectInputError("Введены некорректные данные!"))

class HingeDialog(BaseDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__("Добавить шарнир", ["Номер узла:"], [QLineEdit()], parent, default_values)

    def validate_and_accept(self):
        try:
            node_id = int(self.inputs[0].text())
            self._data = node_id
            self.accept()
        except Exception:
            show_styled_error(self, IncorrectInputError("Введены некорректные данные!"))

class SolveDialog(QDialog):
    def __init__(self, answers: dict[str, float], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результаты расчёта")
        layout = QVBoxLayout()
        for key, value in answers.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key}:"))
            result_field = QLineEdit(f"{value:.2f}")
            result_field.setReadOnly(True)
            row.addWidget(result_field)
            layout.addLayout(row)
        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)
        self.setLayout(layout)

class DialogManager:
    def __init__(self, grid_widget):
        self.grid_widget = grid_widget

    def open_dialog(self, dialog_class, apply_func):
        default_data = None
        while True:
            dialog = dialog_class(None, default_data)
            if not dialog.exec():
                break
            try:
                apply_func(dialog.get_data())
                self.grid_widget.update()
                break
            except Exception as e:
                show_styled_error(None, e)
                default_data = dialog.get_data()

    def open_segment_dialog(self):
        self.open_dialog(
            BeamSegmentDialog,
            lambda data: self.grid_widget.beam.add_segment_new(
                Node(data[0], data[1]), Node(data[2], data[3])
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
            self.grid_widget.node_mapping[node_number].add_hinge()
            self.grid_widget.node_mapping[node_number].support = None
        self.open_dialog(HingeDialog, apply)

    def open_solve_dialog(self):
        try:
            solve = self.grid_widget.beam.solve()
            dialog = SolveDialog(solve)
            dialog.exec()
        except Exception as e:
            show_styled_error(None, e)
