"""
grid.py — графический холст и логика отрисовки.

Содержит класс GridWidget, отвечающий за визуализацию координатной сетки,
отрисовку балок, узлов, опор, сил и моментов. Поддерживает масштабирование
и панорамирование.

Также обрабатывает взаимодействие мыши с холстом.

Используемые технологии:
- PyQt6: QWidget, QPainter;
- structures.py для модели;
- Qt Pixmap и SVG для векторных иконок.
"""

# Импорт необходимых классов из PyQt6
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QTransform
from PyQt6.QtCore import Qt, QPointF, QPoint
from structures import *  # Пользовательские структуры данных (например, Beam, Segment, Force и т.п.)
import math

# Класс GridWidget — виджет с координатной плоскостью и элементами балки
class GridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.scale = 40.0  # Масштаб по умолчанию (пикселей на 1 условную единицу)
        self.min_scale = 1.0  # Минимальный масштаб
        self.max_scale = 1000.0  # Максимальный масштаб
        self.offset = QPointF(0, 0)  # Смещение центра координат относительно центра окна
        self.last_mouse_pos = None  # Последняя позиция мыши при перемещении
        self.coord_limit = 10000  # Ограничение по координатам (в логических единицах)
        self.margin = 40  # Отступ от краёв (пока не используется)
        self.beam = Beam()  # Объект балки, содержащий узлы, сегменты, нагрузки и т.д.

    # Метод отрисовки при каждом обновлении окна
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)  # Заливка фона

        center = QPointF(self.width() / 2, self.height() / 2) + self.offset  # Центр координат с учётом смещения
        bounds = self.calculate_bounds(center)  # Границы видимой области (в логических координатах)
        spacing, sub_spacing = self.calculate_spacing()  # Основное и дополнительное расстояние между линиями сетки

        # Последовательно вызываем отрисовку всех элементов
        self.draw_grid(painter, center, bounds, spacing, sub_spacing)
        self.draw_axes(painter, center)
        self.draw_labels(painter, center, bounds, spacing)
        self.draw_forces_and_torques(painter, center)
        self.draw_beams(painter, center)
        self.draw_nodes(painter, center)

    # Вычисляет левую, правую, верхнюю и нижнюю границу в логических координатах
    def calculate_bounds(self, center):
        left = -(center.x()) / self.scale
        right = (self.width() - center.x()) / self.scale
        top = -(center.y()) / self.scale
        bottom = (self.height() - center.y()) / self.scale
        return left, right, top, bottom

    # Определяет шаг сетки в зависимости от текущего масштаба
    def calculate_spacing(self):
        steps = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
        sub_steps = 4
        for step in steps:
            if step * self.scale >= 60:  # Если шаг в пикселях больше 60 — используем его
                return step, step / sub_steps
        return 1.0, 0.2  # Значения по умолчанию

    # Отрисовка сетки (мелкой и крупной)
    def draw_grid(self, painter, center, bounds, spacing, sub_spacing):
        left, right, top, bottom = bounds

        # Мелкая (вспомогательная) сетка
        sub_grid_pen = QPen(QColor(220, 220, 220))
        sub_grid_pen.setWidth(0)
        painter.setPen(sub_grid_pen)

        # Вертикальные линии вспомогательной сетки
        x = int(left // sub_spacing) * sub_spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                painter.drawLine(int(px), 0, int(px), self.height())
            x += sub_spacing

        # Горизонтальные линии вспомогательной сетки
        y = int(top // sub_spacing) * sub_spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                painter.drawLine(0, int(py), self.width(), int(py))
            y += sub_spacing

        # Основная сетка (более тёмные линии)
        grid_pen = QPen(Qt.GlobalColor.lightGray)
        grid_pen.setWidth(2)
        painter.setPen(grid_pen)

        x = int(left // spacing) * spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                painter.drawLine(int(px), 0, int(px), self.height())
            x += spacing

        y = int(top // spacing) * spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                painter.drawLine(0, int(py), self.width(), int(py))
            y += spacing

    # Отрисовка осей координат
    def draw_axes(self, painter, center):
        axis_pen = QPen(Qt.GlobalColor.black)
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)

        if -self.coord_limit <= 0 <= self.coord_limit:
            painter.drawLine(int(center.x()), 0, int(center.x()), self.height())  # Вертикальная ось
            painter.drawLine(0, int(center.y()), self.width(), int(center.y()))  # Горизонтальная ось

    # Подписи координат вдоль сетки
    def draw_labels(self, painter, center, bounds, spacing):
        left, right, top, bottom = bounds
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", 9))

        # Подписи по оси X
        x = int(left // spacing) * spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                if 0 < px < self.width():
                    self.draw_text(painter, int(px), 6, str(int(x) if spacing >= 1 else f"{x:.2f}"))
                    self.draw_text(painter, int(px), self.height() - 6, str(int(x) if spacing >= 1 else f"{x:.2f}"))
            x += spacing

        # Подписи по оси Y
        y = int(top // spacing) * spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                if 0 < py < self.height():
                    self.draw_text(painter, 6, int(py), str(int(-y) if spacing >= 1 else f"{-y:.2f}"))
                    self.draw_text(painter, self.width() - 6, int(py), str(int(-y) if spacing >= 1 else f"{-y:.2f}"))
            y += spacing

    # Универсальная функция отрисовки текста с белым фоном
    def draw_text(self, painter, x, y, text):
        metrics = painter.fontMetrics()
        text_rect = metrics.tightBoundingRect(text)
        text_rect.adjust(-1, -1, 1, 1)
        text_rect.moveCenter(QPoint(x, y))

        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(text_rect)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    # Отрисовка всех сегментов балки
    def draw_beams(self, painter, center):
        count = 1
        self.segment_mapping = {}  # Словарь для хранения соответствия номера сегмента и объекта
        for segment in self.beam.get_segments():
            self.segment_mapping[count] = segment

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            x1 = center.x() + segment.node1.x * self.scale
            y1 = center.y() - segment.node1.y * self.scale
            x2 = center.x() + segment.node2.x * self.scale
            y2 = center.y() - segment.node2.y * self.scale
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            text = str(count)
            metrics = painter.fontMetrics()
            text_rect = metrics.tightBoundingRect(text)

            rect_x = int(x1 + (x2 - x1) // 2 - (0 if y2 - y1 == 0 else 8)) 
            rect_y = int(y1 + (y2 - y1) // 2 - (0 if x2 - x1 == 0 else 8))

            text_rect.moveCenter(QPoint(rect_x, rect_y))
            text_rect.adjust(-1, -1, 1, 1)

            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(text_rect)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            count += 1

    # Отрисовка всех сил и моментов на балке
    def draw_forces_and_torques(self, painter, center):
        for segment in self.beam.get_segments():
            x1 = center.x() + segment.node1.x * self.scale
            y1 = center.y() - segment.node1.y * self.scale
            x2 = center.x() + segment.node2.x * self.scale
            y2 = center.y() - segment.node2.y * self.scale

            for force in segment.forces:
                self.draw_force(painter, x1, y1, x2, y2, segment.length, force)
            for torque in segment.torques:
                self.draw_torque(painter, x1, y1, x2, y2, segment.length, torque)

    # Отрисовка одной силы (стрелка + подпись)
    def draw_force(self, painter, x1, y1, x2, y2, length, force):
        x = x1 + force.node1_dist * (x2 - x1) / length
        y = y1 + force.node1_dist * (y2 - y1) / length

        size_y = int(2 * self.scale)
        size_y = 35 if size_y > 35 else size_y
        size_x = size_y * 2

        painter.save()
        painter.translate(x, y)
        painter.rotate(-force.angle)

        if force.length == 1:
            painter.drawPixmap(-size_x, -size_y // 2, size_x, size_y, QPixmap("images\\arrow.svg"))
            painter.restore()

            text = f'{force.value} Н'
            self.draw_annotation(painter, x, y, size_x, force.angle, text)
        else:
            painter.rotate(-90)
            painter.drawPixmap(-size_x // 2, -size_y, size_x, size_y, QPixmap("images\\many_arrows.svg"))

            text = f'{force.length}м'
            self.draw_annotation(painter, 0, size_y, size_x, force.angle, text)

            text = f'{force.value} Н/м'
            self.draw_annotation(painter, 0, size_y * 2 + 6, size_x, force.angle, text)

            painter.restore()

    # Отрисовка одного крутящего момента
    def draw_torque(self, painter, x1, y1, x2, y2, length, torque):
        x = x1 + torque.node1_dist * (x2 - x1) / length
        y = y1 + torque.node1_dist * (y2 - y1) / length

        size = int(2 * self.scale)
        size = 35 if size > 35 else size

        painter.save()
        painter.translate(x, y)
        if torque.value < 0:
            painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("images\\circlearrow.svg").transformed(QTransform().scale(-1, 1)))
        else:
            painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("images\\circlearrow.svg"))
        painter.restore()

        text = f'{torque.value} Нм'
        self.draw_annotation(painter, x, y, size, 0, text)

    # Отрисовка поясняющей подписи к силе или моменту
    def draw_annotation(self, painter, x, y, size, angle, text):
        metrics = painter.fontMetrics()
        text_rect = metrics.tightBoundingRect(text)
        text_x = int(x - size * math.cos(math.radians(angle)))
        text_y = int(y + size * math.sin(math.radians(angle)))
        text_rect.moveCenter(QPoint(text_x, text_y))
        text_rect.adjust(-1, -1, 1, 1)

        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(text_rect)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    # Отрисовка всех узлов балки
    def draw_nodes(self, painter, center):
        node_radius = 2
        count = 1
        self.node_mapping = {}
        for node in self.beam.get_nodes():
            self.node_mapping[count] = node

            x = center.x() + node.x * self.scale
            y = center.y() - node.y * self.scale

            if node.support:
                size = int(2 * self.scale)
                size = 35 if size > 35 else size
                painter.save()
                painter.translate(x, y)
                painter.rotate(-node.support.angle)

                match node.support.support_type:
                    case Support.Type.FIXED: image = QPixmap("images\\support0.svg")
                    case Support.Type.PINNED: image = QPixmap("images\\support1.svg")
                    case Support.Type.ROLLER: image = QPixmap("images\\support2.svg")
                painter.drawPixmap(-size // 2, -size // 2 + 12, size, size, image)
                painter.restore()

            node_brush = QColor(0, 0, 255, 127)
            node_text_pen = Qt.GlobalColor.blue
            if node.hinge:
                size = int(2 * self.scale)
                size = 35 if size > 35 else size
                painter.drawPixmap(int(x - size // 2), int(y - size // 2), size, size, QPixmap("images\\hinge.svg"))
                node_text_pen = Qt.GlobalColor.red
                node_brush = QColor(255, 0, 0, 127)

            painter.setBrush(node_brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), node_radius * 2, node_radius * 2)

            text = str(count)
            metrics = painter.fontMetrics()
            text_rect = metrics.tightBoundingRect(text)
            text_rect.moveCenter(QPoint(int(x), int(y - metrics.height() / 2 - node_radius - 1)))
            text_rect.adjust(-1, -1, 0, 1)

            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(text_rect)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(node_text_pen)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            count += 1

    # Сброс смещения (центрируется координатная сетка)
    def resetOffset(self):
        self.offset = QPointF(0, 0)
        self.update()

    # Обработка колесика мыши для увеличения/уменьшения масштаба
    def wheelEvent(self, event):
        zoom_in_factor = 1.1
        zoom_out_factor = 0.9

        old_scale = self.scale
        if event.angleDelta().y() > 0:
            self.scale *= zoom_in_factor
        else:
            self.scale *= zoom_out_factor

        self.scale = max(self.min_scale, min(self.max_scale, self.scale))

        mouse_pos = event.position()
        center = QPointF(self.width() / 2, self.height() / 2)
        mouse_delta = mouse_pos - center - self.offset
        self.offset -= mouse_delta * (self.scale / old_scale - 1)

        self.clamp_offset()
        self.update()

    # При нажатии ЛКМ — сохраняем позицию
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()

    # При движении мыши с зажатой ЛКМ — смещаем сетку
    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.position()
            self.clamp_offset()
            self.update()

    # Отпускание кнопки мыши — обнуляем перемещение
    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None

    # Ограничение на смещение — чтобы не "уйти" за пределы допустимых координат
    def clamp_offset(self):
        half_w = self.width() / 2
        half_h = self.height() / 2

        max_offset_x = self.coord_limit * self.scale - half_w
        max_offset_y = self.coord_limit * self.scale - half_h

        self.offset.setX(max(-max_offset_x, min(max_offset_x, self.offset.x())))
        self.offset.setY(max(-max_offset_y, min(max_offset_y, self.offset.y())))

    def save_as_image(self, file_path):
        pixmap = self.grab()
        pixmap.save(file_path, "JPG")