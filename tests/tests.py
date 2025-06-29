import pytest
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
# from main import (
#     BaseDialog, BeamSegmentDialog, SupportDialog, ForceDialog, TorqueDialog, SolveDialog, DialogManager
# )
from structures import IncorrectInputError, NonExistentError, Node, BeamSegment, Support, Force, Torque

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

import pytest
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
from dialogs import (
    smart_str, BaseDialog, BeamSegmentDialog, SupportDialog,
    ForceDialog, TorqueDialog, SolveDialog, DialogManager
)
from structures import IncorrectInputError, NonExistentError, Support, Force, Torque, Node, BeamSegment

import pytest
from dialogs import DialogManager
from structures import IncorrectInputError, NonExistentError, Support, Force, Torque, BeamSegment

import pytest
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
#from main import BaseDialog, BeamSegmentDialog, SupportDialog, ForceDialog, TorqueDialog

import pytest
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
#from main import BaseDialog, BeamSegmentDialog, SupportDialog, ForceDialog, TorqueDialog

# smart_str: большие числа и отрицательные
@pytest.mark.parametrize("value, expected", [
    (-10.0, "-10"),
    (-10.5, "-10.5"),
    (123456789.0, "123456789"),
    (123456789.123, "123456789.123"),
])
def test_smart_str_large_and_negative(value, expected):
    assert smart_str(value) == expected

# BaseDialog: set_defaults с пустым списком
def test_base_dialog_set_defaults_empty(qtbot):
    line_edit = QLineEdit()
    dialog = BaseDialog("Test", ["A"], [line_edit])
    dialog.set_defaults([])
    assert line_edit.text() == ""  # Ничего не изменено

# BeamSegmentDialog: ввод нулевых значений
def test_beam_segment_dialog_zero_values(qtbot):
    dialog = BeamSegmentDialog()
    dialog.inputs[0].setText("0")
    dialog.inputs[1].setText("0")
    dialog.inputs[2].setText("0")
    dialog.validate_and_accept()
    assert dialog.get_data() == (0, 0.0, 0.0)

# SupportDialog: ввод с пустыми значениями
def test_support_dialog_empty_input(qtbot):
    dialog = SupportDialog()
    dialog.inputs[0].setText("")
    dialog.inputs[1].setCurrentIndex(0)
    dialog.inputs[2].setText("")
    dialog.validate_and_accept()
    assert dialog.get_data() is None

# ForceDialog: ввод с нулевой длиной распределённой силы
def test_force_dialog_zero_length_distributed(qtbot):
    dialog = ForceDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0")
    dialog.inputs[2].setText("0")
    dialog.inputs[3].setText("0")
    dialog.inputs[4].setChecked(True)
    dialog.inputs[5].setText("0")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.0, 0.0, 0.0, 0.0)

# TorqueDialog: ввод с большими числами
def test_torque_dialog_large_numbers(qtbot):
    dialog = TorqueDialog()
    dialog.inputs[0].setText("1000")
    dialog.inputs[1].setText("10000")
    dialog.inputs[2].setText("100000")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1000, 10000.0, 100000.0)

# smart_str: тест с разными типами данных
@pytest.mark.parametrize("value, expected", [
    (3.0, "3"),
    (3.5, "3.5"),
    (10, "10"),
    ("abc", "abc"),
])
def test_smart_str_various(value, expected):
    assert smart_str(value) == expected

# BaseDialog: проверка set_defaults с QLineEdit
def test_base_dialog_set_defaults_lineedit(qtbot):
    line_edit1 = QLineEdit()
    line_edit2 = QLineEdit()
    dialog = BaseDialog("Test", ["A", "B"], [line_edit1, line_edit2])
    dialog.set_defaults([1.0, 2.5])
    assert line_edit1.text() == "1"
    assert line_edit2.text() == "2.5"

# BaseDialog: проверка set_defaults с QComboBox и QCheckBox
def test_base_dialog_set_defaults_combo_checkbox(qtbot):
    combo = QComboBox()
    combo.addItems(["A", "B"])
    checkbox = QCheckBox()
    dialog = BaseDialog("Test", ["Combo", "Check"], [combo, checkbox])
    dialog.set_defaults([1, True])
    assert combo.currentIndex() == 1
    assert checkbox.isChecked()

# BeamSegmentDialog: некорректный ввод
def test_beam_segment_dialog_invalid_input(qtbot):
    dialog = BeamSegmentDialog()
    for field in dialog.inputs:
        field.setText("abc")  # нечисловой ввод
    dialog.validate_and_accept()
    assert dialog.get_data() is None

# SupportDialog: ввод с корректными данными
def test_support_dialog_valid_input(qtbot):
    dialog = SupportDialog()
    dialog.inputs[0].setText("2")       # номер узла
    dialog.inputs[1].setCurrentIndex(1) # тип опоры
    dialog.inputs[2].setText("45")      # угол
    dialog.validate_and_accept()
    assert dialog.get_data() == (2, 1, 45.0)

# ForceDialog: распределённая сила с длиной
def test_force_dialog_distributed_with_length(qtbot):
    dialog = ForceDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0.5")
    dialog.inputs[2].setText("100")
    dialog.inputs[3].setText("30")
    dialog.inputs[4].setChecked(True)  # распределённая
    dialog.inputs[5].setText("2.0")    # длина
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.5, 100.0, 30.0, 2.0)

# ForceDialog: сосредоточенная сила (длина = 1)
def test_force_dialog_concentrated_force(qtbot):
    dialog = ForceDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0.5")
    dialog.inputs[2].setText("100")
    dialog.inputs[3].setText("30")
    dialog.inputs[4].setChecked(False) # сосредоточенная
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.5, 100.0, 30.0, 1)

# TorqueDialog: некорректный ввод
def test_torque_dialog_invalid_input(qtbot):
    dialog = TorqueDialog()
    dialog.inputs[0].setText("x")
    dialog.inputs[1].setText("y")
    dialog.inputs[2].setText("z")
    dialog.validate_and_accept()
    assert dialog.get_data() is None


# === Дополнительные фиктивные классы для тестов ===

class DummyGrid2:
    def __init__(self):
        self.updated = False
        self.beam = DummyBeam2()
        self.node_mapping = {1: DummyNode2()}
        self.segment_mapping = {1: DummySegment2()}

    def update(self):
        self.updated = True

class DummyBeam2:
    def __init__(self):
        self.solve_called = False
        self.added_segments = []
    def add_segment(self, segment):
        if not isinstance(segment, BeamSegment):
            raise IncorrectInputError("Bad segment")
        self.added_segments.append(segment)
    def solve(self):
        self.solve_called = True
        return {'Rx': 42, 'Ry': 84}

class DummyNode2:
    def __init__(self):
        self.added_supports = []
    def add_support(self, support):
        if not isinstance(support, Support):
            raise IncorrectInputError("Bad support")
        self.added_supports.append(support)

class DummySegment2:
    def __init__(self):
        self.added_forces = []
        self.added_torques = []
    def add_force(self, force):
        if not isinstance(force, Force):
            raise IncorrectInputError("Bad force")
        self.added_forces.append(force)
    def add_torque(self, torque):
        if not isinstance(torque, Torque):
            raise IncorrectInputError("Bad torque")
        self.added_torques.append(torque)

# === DialogManager ===



def test_dialog_manager_handle_incorrect_input_error(monkeypatch):
    grid = DummyGrid2()
    manager = DialogManager(grid)
    monkeypatch.setattr("dialogs.BeamSegmentDialog.get_data", lambda self: [1, 1, "bad", 2])
    # Ошибка должна быть обработана без падения
    manager.open_segment_dialog()
    assert not grid.updated

def test_dialog_manager_handle_non_existent_error(monkeypatch):
    grid = DummyGrid2()
    manager = DialogManager(grid)
    monkeypatch.setattr("dialogs.SupportDialog.get_data", lambda self: (99, 1, 0))  # node 99 не существует
    manager.open_support_dialog()
    assert not grid.updated

def test_dialog_manager_solve(monkeypatch):
    grid = DummyGrid2()
    manager = DialogManager(grid)
    manager.open_solve_dialog()
    assert grid.beam.solve_called


# === smart_str ===

def test_smart_str_int_float():
    assert smart_str(3.0) == '3'
    assert smart_str(3.5) == '3.5'
    assert smart_str(7) == '7'
    assert smart_str('test') == 'test'

# === BaseDialog ===

def test_base_dialog_set_defaults(qtbot):
    line_edit = QLineEdit()
    combo = QComboBox()
    combo.addItems(['A', 'B'])
    checkbox = QCheckBox()

    dialog = BaseDialog("Test", ["Label1", "Label2", "Label3"],
                        [line_edit, combo, checkbox])
    dialog.set_defaults([42, 1, True])

    assert line_edit.text() == '42'
    assert combo.currentIndex() == 1
    assert checkbox.isChecked()

# === BeamSegmentDialog ===

def test_beam_segment_dialog_valid(qtbot):
    dialog = BeamSegmentDialog()
    for i, val in enumerate(['1.0', '2.0', '3.0', '4.0']):
        dialog.inputs[i].setText(val)
    dialog.validate_and_accept()
    assert dialog.get_data() == [1.0, 2.0, 3.0, 4.0]

def test_beam_segment_dialog_invalid(qtbot):
    dialog = BeamSegmentDialog()
    dialog.inputs[0].setText("bad")
    dialog.validate_and_accept()
    assert dialog.get_data() is None

# === SupportDialog ===

def test_support_dialog_valid(qtbot):
    dialog = SupportDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setCurrentIndex(2)
    dialog.inputs[2].setText("45.0")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 2, 45.0)

def test_support_dialog_invalid(qtbot):
    dialog = SupportDialog()
    dialog.inputs[0].setText("bad")
    dialog.validate_and_accept()
    assert dialog.get_data() is None

# === ForceDialog ===

def test_force_dialog_point_force(qtbot):
    dialog = ForceDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0.5")
    dialog.inputs[2].setText("100")
    dialog.inputs[3].setText("30")
    dialog.inputs[4].setChecked(False)
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.5, 100.0, 30.0, 1)

def test_force_dialog_distributed_force(qtbot):
    dialog = ForceDialog()
    dialog.inputs[0].setText("2")
    dialog.inputs[1].setText("1.5")
    dialog.inputs[2].setText("200")
    dialog.inputs[3].setText("60")
    dialog.inputs[4].setChecked(True)
    dialog.inputs[5].setText("2.5")
    dialog.validate_and_accept()
    assert dialog.get_data() == (2, 1.5, 200.0, 60.0, 2.5)

def test_force_dialog_toggle_length_field(qtbot):
    dialog = ForceDialog()
    dialog.inputs[4].setChecked(True)
    assert dialog.inputs[5].isEnabled()
    dialog.inputs[4].setChecked(False)
    assert not dialog.inputs[5].isEnabled()

# === TorqueDialog ===

def test_torque_dialog_valid(qtbot):
    dialog = TorqueDialog()
    dialog.inputs[0].setText("3")
    dialog.inputs[1].setText("0.0")
    dialog.inputs[2].setText("50")
    dialog.validate_and_accept()
    assert dialog.get_data() == (3, 0.0, 50.0)

# === SolveDialog ===

def test_solve_dialog_shows_results(qtbot):
    data = {'Rx': 10.0, 'Ry': 5.5}
    dialog = SolveDialog(data)
    # Проверяем, что в диалоге созданы поля для результатов
    assert dialog.findChild(QLineEdit, None).isReadOnly()

# === DialogManager ===

class DummyGrid:
    def __init__(self):
        self.beam = DummyBeam()
        self.node_mapping = {1: DummyNode()}
        self.segment_mapping = {1: DummySegment()}

    def update(self):
        self.updated = True

class DummyBeam:
    def add_segment(self, segment):
        self.segment_added = segment

    def solve(self):
        return {'Rx': 1.0, 'Ry': 2.0}

class DummyNode:
    def add_support(self, support):
        self.support_added = support

class DummySegment:
    def add_force(self, force):
        self.force_added = force

    def add_torque(self, torque):
        self.torque_added = torque

def test_dialog_manager_solve_dialog(qtbot):
    grid = DummyGrid()
    manager = DialogManager(grid)
    # Просто проверим, что вызов не вызывает исключения
    manager.open_solve_dialog()

# Если приложение не создано — создаём его (для тестов GUI нужно приложение)
app = QApplication.instance() or QApplication([])

@pytest.mark.parametrize("default_values, expected", [
    ([1, 2, 3, 4], ["1", "2", "3", "4"]),
    ([1.0, 2.0, 3.5, 4.5], ["1", "2", "3.5", "4.5"]),
])
def test_beam_segment_set_defaults(default_values, expected):
    dialog = BeamSegmentDialog(default_values=default_values)
    actual = [dialog.inputs[i].text() for i in range(4)]
    assert actual == expected

def test_support_dialog_set_defaults():
    dialog = SupportDialog(default_values=[5, 1, 30])
    assert dialog.inputs[0].text() == "5"
    assert dialog.inputs[1].currentIndex() == 1
    assert dialog.inputs[2].text() == "30"

def test_force_dialog_toggle_length_field():
    dialog = ForceDialog()
    dialog.inputs[4].setChecked(True)
    assert dialog.inputs[5].isEnabled()
    dialog.inputs[4].setChecked(False)
    assert not dialog.inputs[5].isEnabled()

def test_beam_segment_dialog_validation_success():
    dialog = BeamSegmentDialog()
    for i, val in enumerate(["1", "2", "3", "4"]):
        dialog.inputs[i].setText(val)
    dialog.validate_and_accept()
    assert dialog.get_data() == [1.0, 2.0, 3.0, 4.0]

def test_beam_segment_dialog_validation_failure(qtbot):
    dialog = BeamSegmentDialog()
    for i in range(4):
        dialog.inputs[i].setText("abc")
    with qtbot.waitSignal(dialog.finished, timeout=1000):
        dialog.validate_and_accept()
    assert dialog.get_data() is None

def test_support_dialog_validation_success():
    dialog = SupportDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setCurrentIndex(1)
    dialog.inputs[2].setText("45")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 1, 45.0)

def test_force_dialog_validation_distributed():
    dialog = ForceDialog()
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0.5")
    dialog.inputs[2].setText("100")
    dialog.inputs[3].setText("30")
    dialog.inputs[4].setChecked(True)
    dialog.inputs[5].setText("2")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.5, 100.0, 30.0, 2.0)

def test_force_dialog_validation_concentrated():
    dialog = ForceDialog()
    dialog.inputs[0].setText("2")
    dialog.inputs[1].setText("1.5")
    dialog.inputs[2].setText("200")
    dialog.inputs[3].setText("60")
    dialog.inputs[4].setChecked(False)
    dialog.validate_and_accept()
    assert dialog.get_data() == (2, 1.5, 200.0, 60.0, 1)

def test_torque_dialog_validation_success():
    dialog = TorqueDialog()
    dialog.inputs[0].setText("3")
    dialog.inputs[1].setText("0.7")
    dialog.inputs[2].setText("50")
    dialog.validate_and_accept()
    assert dialog.get_data() == (3, 0.7, 50.0)

def test_dialog_manager_open_segment_dialog_success(mocker):
    class FakeGrid:
        def __init__(self):
            self.beam = mocker.Mock()
            self.update = mocker.Mock()
        beam = None

    grid = FakeGrid()
    grid.beam = mocker.Mock()
    grid.beam.add_segment = mocker.Mock()
    dm = DialogManager(grid)

    mocker.patch("dialogs.BeamSegmentDialog.exec", return_value=True)
    mocker.patch("dialogs.BeamSegmentDialog.get_data", return_value=[0, 0, 1, 1])
    dm.open_segment_dialog()
    grid.beam.add_segment.assert_called_once()
    grid.update.assert_called_once()

def test_dialog_manager_open_support_dialog_nonexistent_node(mocker):
    class FakeNode:
        def add_support(self, support):
            pass

    class FakeGrid:
        node_mapping = {1: FakeNode()}
        beam = None
        def update(self): pass

    grid = FakeGrid()
    dm = DialogManager(grid)

    mocker.patch("dialogs.SupportDialog.exec", return_value=True)
    mocker.patch("dialogs.SupportDialog.get_data", return_value=(99, 0, 0))  # несуществующий узел
    mock_msg = mocker.patch("PyQt6.QtWidgets.QMessageBox.critical")

    dm.open_support_dialog()
    mock_msg.assert_called_once()

def test_smart_str_integer_float():
    assert smart_str(3.0) == "3"
    assert smart_str(3.5) == "3.5"
    assert smart_str(7) == "7"


def test_base_dialog_set_defaults(qtbot):
    inputs = [QLineEdit(), QComboBox(), QCheckBox()]
    inputs[1].addItems(["A", "B", "C"])
    dialog = BaseDialog("Test", ["Label1", "Label2", "Label3"], inputs)
    qtbot.addWidget(dialog)
    dialog.set_defaults([5, 1, True])
    assert inputs[0].text() == "5"
    assert inputs[1].currentIndex() == 1
    assert inputs[2].isChecked() is True


def test_beam_segment_dialog_valid_input(qtbot):
    dialog = BeamSegmentDialog()
    qtbot.addWidget(dialog)
    for i, val in enumerate(["1", "2", "3", "4"]):
        dialog.inputs[i].setText(val)
    dialog.validate_and_accept()
    assert dialog.get_data() == [1.0, 2.0, 3.0, 4.0]


def test_beam_segment_dialog_invalid_input(qtbot):
    dialog = BeamSegmentDialog()
    qtbot.addWidget(dialog)
    dialog.inputs[0].setText("abc")
    dialog.validate_and_accept()
    assert dialog.get_data() is None


def test_support_dialog_valid_input(qtbot):
    dialog = SupportDialog()
    qtbot.addWidget(dialog)
    dialog.inputs[0].setText("2")
    dialog.inputs[1].setCurrentIndex(1)
    dialog.inputs[2].setText("45")
    dialog.validate_and_accept()
    assert dialog.get_data() == (2, 1, 45.0)


def test_force_dialog_toggle_length_field(qtbot):
    dialog = ForceDialog()
    qtbot.addWidget(dialog)
    dialog.inputs[4].setChecked(True)
    assert dialog.inputs[5].isEnabled() is True
    dialog.inputs[4].setChecked(False)
    assert dialog.inputs[5].isEnabled() is False


def test_force_dialog_valid_input(qtbot):
    dialog = ForceDialog()
    qtbot.addWidget(dialog)
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0.5")
    dialog.inputs[2].setText("10")
    dialog.inputs[3].setText("30")
    dialog.inputs[4].setChecked(True)
    dialog.inputs[5].setText("2")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.5, 10.0, 30.0, 2.0)


def test_torque_dialog_valid_input(qtbot):
    dialog = TorqueDialog()
    qtbot.addWidget(dialog)
    dialog.inputs[0].setText("1")
    dialog.inputs[1].setText("0.5")
    dialog.inputs[2].setText("15")
    dialog.validate_and_accept()
    assert dialog.get_data() == (1, 0.5, 15.0)


def test_solve_dialog_display(qtbot):
    answers = {"R1": 5.0, "M1": 10.0}
    dialog = SolveDialog(answers)
    qtbot.addWidget(dialog)
    for i, (key, value) in enumerate(answers.items()):
        field = dialog.findChildren(QLineEdit)[i]
        assert field.text() == str(value)
        assert field.isReadOnly()


def test_dialog_manager_open_segment_dialog_valid(monkeypatch, qtbot):
    class MockGrid:
        def __init__(self):
            self.beam = self
            self.segment_mapping = {1: self}
            self.node_mapping = {1: self}
        def add_segment(self, seg):
            self.last_segment = seg
        def update(self):
            self.updated = True
        def solve(self):
            return {"R": 1.0}

    grid = MockGrid()
    manager = DialogManager(grid)

    monkeypatch.setattr(BeamSegmentDialog, "exec", lambda self: True)
    monkeypatch.setattr(BeamSegmentDialog, "get_data", lambda self: [0, 0, 1, 1])

    manager.open_segment_dialog()

    assert isinstance(grid.last_segment, BeamSegment)
    assert hasattr(grid, "updated")


def test_dialog_manager_open_support_dialog_invalid_node(monkeypatch, qtbot):
    class MockGrid:
        def __init__(self):
            self.node_mapping = {}
        def update(self):
            self.updated = True

    grid = MockGrid()
    manager = DialogManager(grid)

    monkeypatch.setattr(SupportDialog, "exec", lambda self: True)
    monkeypatch.setattr(SupportDialog, "get_data", lambda self: (99, 0, 0.0))

    # Чтобы избежать вывода QMessageBox
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.critical", lambda *args, **kwargs: None)

    manager.open_support_dialog()  # Ожидается, что NonExistentError отработает и не будет update
    assert not hasattr(grid, "updated")
