"""
structures.py — ядро модели балочной конструкции.

Определяет основные классы: Node, BeamSegment, Force, Torque, Support, Beam и др.
Хранит геометрию, нагрузки и опоры, формирует систему уравнений, выполняет решение
через SymPy.

Ключевые функции:
- solve() — символьное решение реакций;
- to_dict()/from_file() — сериализация;
- pretty_print() — форматированный вывод.

Зависит от:
- networkx (графовая модель);
- sympy (аналитические уравнения);
- errors.py (обработка исключений);
- ids.py (уникальные идентификаторы).
"""

import json
import math
from enum import Enum
import networkx as nx
import sympy as sp
from errors import *
from ids import IDNumerator


class Force(IDNumerator):
    def __init__(self,
                 value: float,
                 angle: float,
                 node1_dist: float,
                 length: float = 1,
                 unknown: bool = False,
                 unknown_x: bool = False,
                 unknown_y: bool = False,
                 custom_id: int | None = None):
        super().__init__(custom_id)

        if value < 0: raise NegativeOrZeroValueError("Значение силы не может быть отрицательным!")
        self.value: float = value

        self.angle: float = angle % 360

        if node1_dist < 0: raise NegativeOrZeroValueError("Расстояние от края не может быть отрицательным!")
        self.node1_dist: float = node1_dist

        if length <= 0: raise NegativeOrZeroValueError("Длина действия силы должна быть положительной!")
        self.length: float = length

        self.unknown_x: bool = unknown or unknown_x
        self.unknown_y: bool = unknown or unknown_y

    @staticmethod
    def combine_force_projections(fx: float, fy: float) -> tuple[float, float]:
        magnitude = math.hypot(fx, fy)
        angle_rad = math.atan2(fy, fx)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360
        return magnitude, angle_deg

    @property
    def part_x(self):
        if self.angle in (0, 180):
            return self.value * self.length * (1 if self.angle == 0 else -1)
        elif self.angle in (90, 270):
            return 0
        else:
            return math.cos(math.radians(self.angle)) * self.value * self.length

    @property
    def part_y(self):
        if self.angle in (0, 180):
            return 0
        elif self.angle == 90:
            return self.value * self.length
        elif self.angle == 270:
            return -self.value * self.length
        else:
            return math.sin(math.radians(self.angle)) * self.value * self.length

    def __repr__(self):
        return f"Force(value={self.value}, angle={self.angle}, node1_dist={self.node1_dist}, length={self.length}, unknown={self.unknown})"

    class Type(Enum):
        OTHER = 0
        VERTICAL = 1
        HORIZONTAL = 2

    @property
    def get_type(self):
        if self.angle in (0, 180): return Force.Type.HORIZONTAL
        elif self.angle in (90, 270): return Force.Type.VERTICAL
        else: return Force.Type.OTHER

    def pretty_print(self, indent=0):
        pad = ' ' * indent
        return (f"{pad}Force#{self.id}: val={self.value}, angle={self.angle}°, "
                f"dist={self.node1_dist}, len={self.length}, unknown_x={self.unknown_x}, unknown_y={self.unknown_y}")


class Torque(IDNumerator):
    def __init__(self, value: float, node1_dist: float, unknown: bool = False, custom_id: int | None = None):
        super().__init__(custom_id)

        self.value: float = value

        if node1_dist < 0: raise NegativeOrZeroValueError("Расстояние не может быть отрицательным!")
        self.node1_dist: float = node1_dist

        self.unknown: bool = unknown

    def __repr__(self):
        return f"Torque(value={self.value}, node1_dist={self.node1_dist}, unknown={self.unknown})"
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        return (f"{pad}Torque#{self.id}: val={self.value}, dist={self.node1_dist}, unknown={'Y' if self.unknown else 'N'}")


class Support(IDNumerator):

    class Type(Enum):
        FIXED = 0
        PINNED = 1
        ROLLER = 2

    def __init__(self,
                 support_type: Type,
                 angle: float,
                 force_x: float,
                 force_y: float,
                 torque: float,
                 unknown_fx: bool,
                 unknown_fy: bool,
                 unknown_t: bool,
                 custom_id: int | None = None,
                 is_new: bool = True):
        super().__init__(custom_id)
        self.support_type = support_type
        self.angle: float = angle % 360
        magnitude, force_angle = Force.combine_force_projections(force_x, force_y)

        ux = unknown_fx
        uy = unknown_fy

        if is_new:
            if angle == 0 or angle == 180:
                pass
            elif angle == 90 or angle == 270:
                ux = unknown_fy
                uy = unknown_fx
            else:
                ux = True
                uy = True

        self.force: Force = Force(magnitude, angle + force_angle, 0, 1, unknown_x=ux, unknown_y=uy)
        self.torque: Torque = Torque(torque, 0, unknown_t)

    def __repr__(self):
        return f"Support(angle={self.angle}, force={self.force}, torque={self.torque})"

    def pretty_print(self, indent=0):
        pad = ' ' * indent
        result = [f"{pad}Support#{self.id}: angle={self.angle}°"]
        result.append(self.force.pretty_print(indent + 2))
        result.append(self.torque.pretty_print(indent + 2))
        return '\n'.join(result)


class Hinge(IDNumerator):
    def __init__(self, custom_id: int | None = None):
        super().__init__(custom_id)
        self.bodies: list["Beam"] = []

    def assign_body(self, beam: "Beam"):
        if beam not in self.bodies:
            self.bodies.append(beam)

    def pretty_print(self, indent=0):
        pad = ' ' * indent
        parts = ', '.join(f'Beam#{b.id}' for b in self.bodies)
        return f"{pad}Hinge#{self.id}: bodies=[{parts}]"

class Node(IDNumerator):
    def __init__(self, x: float, y: float, custom_id: int | None = None):
        super().__init__(custom_id)
        self.x: float = x
        self.y: float = y
        self.support: Support = None
        self.hinge: Hinge = None

    def add_support(self, support: Support):
        self.support = support

    def add_hinge(self):
        self.hinge = Hinge()

    def __repr__(self):
        return f"Node(coords=({self.x}, {self.y}), support={self.support})"

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        lines = [f"{pad}Node#{self.id}: ({self.x}, {self.y})"]
        if self.support:
            lines.append(self.support.pretty_print(indent + 2))
        if self.hinge:
            lines.append(self.hinge.pretty_print(indent + 2))
        return '\n'.join(lines)


class BeamSegment(IDNumerator):
    def __init__(self, node1: Node, node2: Node, custom_id: int | None = None):
        super().__init__(custom_id)
        self.node1: Node = node1
        self.node2: Node = node2
        self.forces: list[Force] = []
        self.torques: list[Torque] = []

    def add_force(self, force: Force):
        if force.node1_dist > self.length:
            raise HighDistanceError("Отступ не может быть больше длины сегмента!")
        self.forces.append(force)

    def add_torque(self, torque: Torque):
        if torque.node1_dist > self.length:
            raise HighDistanceError("Отступ не может быть больше длины сегмента!")
        self.torques.append(torque)

    @property
    def length(self):
        return math.hypot(self.node1.x - self.node2.x, self.node1.y - self.node2.y)

    def __repr__(self):
        return f"BeamSegment(from={self.node1}, to={self.node2}, forces={self.forces}, torques={self.torques})"
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        lines = [f"{pad}Segment#{self.id}: from Node#{self.node1.id} to Node#{self.node2.id}"]
        for force in self.forces:
            lines.append(force.pretty_print(indent + 2))
        for torque in self.torques:
            lines.append(torque.pretty_print(indent + 2))
        return '\n'.join(lines)


class Beam(IDNumerator):
    def __init__(self, segments: list[BeamSegment] = [], custom_id: int | None = None):
        super().__init__(custom_id)
        self.graph = nx.Graph()
        for s in segments:
            self.add_segment(s)

    def add_node(self, node: Node):
        for existing_node in self.graph.nodes:
            if existing_node.x == node.x and existing_node.y == node.y:
                return existing_node

        self.graph.add_node(node)
        return node

    def add_segment_exist(self, segment: BeamSegment) -> BeamSegment:
        node1 = self.add_node(segment.node1)
        node2 = self.add_node(segment.node2)

        if node1.x == node2.x and node1.y == node2.y:
            raise DotBeamError("Балка не может начинаться и заканчиваться в одной точке!")

        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]['object']

        self.graph.add_edge(node1, node2, object=segment)
        return segment

    def add_segment_new(self, node1: Node, node2: Node, custom_id: int | None = None) -> BeamSegment:
        node1 = self.add_node(node1)
        node2 = self.add_node(node2)

        if node1.x == node2.x and node1.y == node2.y:
            raise DotBeamError("Балка не может начинаться и заканчиваться в одной точке!")

        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]['object']

        segment = BeamSegment(node1, node2, custom_id)
        self.graph.add_edge(node1, node2, object=segment)
        return segment

    def get_segments(self):
        return [data['object'] for _, _, data in self.graph.edges(data=True)]

    def get_nodes(self):
        return list(self.graph.nodes)

    def reassign_ids(self):
        for cls in [Node, BeamSegment, Force, Torque, Support]:
            cls._next_id = 1
            cls._used_ids.clear()

        for idx, node in enumerate(self.get_nodes(), start=1):
            node.id = idx
            if node.support:
                node.support.id = Support._next_id
                Support._used_ids.add(Support._next_id)
                Support._next_id += 1

                node.support.force.id = Force._next_id
                Force._used_ids.add(Force._next_id)
                Force._next_id += 1

                node.support.torque.id = Torque._next_id
                Torque._used_ids.add(Torque._next_id)
                Torque._next_id += 1

        for idx, segment in enumerate(self.get_segments(), start=1):
            segment.id = idx
            for force in segment.forces:
                force.id = Force._next_id
                Force._used_ids.add(Force._next_id)
                Force._next_id += 1
            for torque in segment.torques:
                torque.id = Torque._next_id
                Torque._used_ids.add(Torque._next_id)
                Torque._next_id += 1

    @staticmethod
    def format_readable_answers(answer_dict: dict[str, float]) -> dict[str, float]:
        readable_answer = {}

        for key, value in answer_dict.items():
            if key.startswith('node_'):
                parts = key.split('_')
                node_id = parts[1]

                if '_vertical_y' in key or key.endswith('_y'):
                    readable_answer[f"Вертикальная реакция в узле {node_id}"] = value
                elif '_horizontal_x' in key or key.endswith('_x'):
                    readable_answer[f"Горизонтальная реакция в узле {node_id}"] = value
                elif '_torque' in key:
                    readable_answer[f"Момент в узле {node_id}"] = value

            elif key.startswith('hinge_') and '_for_beam_' in key:
                parts = key.split('_')
                hinge_id = parts[1]
                beam_id = int(parts[4]) - 1
                direction = 'горизонтальная' if '_force_x' in key else 'вертикальная'
                readable_answer[f"{direction.capitalize()} реакция в шарнире {hinge_id} для балки {beam_id}"] = value

            else:
                readable_answer[key] = value

        return readable_answer

    def build_equations(self):
        fx_dict, fy_dict, t_dict = {}, {}, {}

        def add_force_parts(name: str, force: Force, x: float, y: float):
            part = force.part_x
            fx_dict[f'{name}_x'] = '?' if force.unknown_x else part
            t_dict[f'{name}_x_torque'] = 0 if y == 0 else f'{-y}*{name}_x' if force.unknown_x else part * -y

            part = force.part_y
            fy_dict[f'{name}_y'] = '?' if force.unknown_y else part
            t_dict[f'{name}_y_torque'] = 0 if x == 0 else f'{x}*{name}_y' if force.unknown_y else part * x

        hinges_equations = []

        for node in self.get_nodes():
            if node.support:
                nid = f'node_{node.id}'
                add_force_parts(f'{nid}', node.support.force, node.x, node.y)
                t_dict[f'{nid}_torque'] = '?' if node.support.torque.unknown else node.support.torque.value

            elif node.hinge:
                hinge = node.hinge
                if self not in hinge.bodies:
                    continue

                prefix = f'hinge_{node.id}_for_beam_{self.id}'
                name_x = f'{prefix}_force_x'
                name_y = f'{prefix}_force_y'

                fx_dict[name_x] = '?'
                fy_dict[name_y] = '?'

                t_dict[f'{name_x}_torque'] = f'{-node.y}*{name_x}' if node.y != 0 else 0
                t_dict[f'{name_y}_torque'] = f'{node.x}*{name_y}' if node.x != 0 else 0

                if hinge.bodies[0] == self:
                    hinges_equations.extend([
                        sp.Eq(sp.simplify(
                            ' + '.join(f'hinge_{node.id}_for_beam_{body.id}_force_x' for body in hinge.bodies)
                        ), 0),

                        sp.Eq(sp.simplify(
                            ' + '.join(f'hinge_{node.id}_for_beam_{body.id}_force_y' for body in hinge.bodies)
                        ), 0),

                        # sp.Eq(sp.simplify(
                        #     ' + '.join(
                        #         f'hinge_{hinge.id}_for_beam_{body.id}_force_x_torque + hinge_{hinge.id}_for_beam_{body.id}_force_y_torque'
                        #         for body in hinge.bodies)
                        # ), 0),
                    ])


        for segment in self.get_segments():
            sid = f'segment_{segment.id}'
            for force in segment.forces:
                x = segment.node1.x + force.node1_dist * (segment.node2.x - segment.node1.x) / segment.length
                y = segment.node1.y + force.node1_dist * (segment.node2.y - segment.node1.y) / segment.length
                add_force_parts(f'{sid}_force_{force.id}', force, x, y)
            for torque in segment.torques:
                t_dict[f'{sid}_torque_{torque.id}'] = '?' if torque.unknown else torque.value

        eqs = [
            sp.Eq(sp.simplify(' + '.join(fx_dict.keys())), 0),
            sp.Eq(sp.simplify(' + '.join(fy_dict.keys())), 0),
            sp.Eq(sp.simplify(' + '.join(t_dict.keys())), 0)
        ]

        eqs.extend(hinges_equations)

        secondary_eqs = []
        unknowns = []
        all_symbols = []

        for d in (fx_dict, fy_dict, t_dict):
            for key, val in d.items():
                if val == '?':
                    unknowns.append(key)
                else:
                    secondary_eqs.append(sp.Eq(sp.Symbol(key), sp.simplify(val)))
                all_symbols.append(key)

        return eqs, secondary_eqs, unknowns, all_symbols

    def solve(self):
        if len(self.graph.nodes) == 0:
            raise NoBeamError("Нет балки!")
        
        if all(node.support is None for node in self.get_nodes()):
            raise NoSupportsError("Вы не добавили опор!")

        if not nx.is_connected(self.graph):
            raise DividedBeamError("Балка состоит из несвязанных сегментов!")

        self.reassign_ids()

        subbeams = self.split_beam_by_hinges()

        for b in subbeams:
            print(b.pretty_print())
        print()

        eqs = []
        secondary_eqs = []
        unknowns_set = set()
        all_symbols_set = set()

        for beam in subbeams:
            e, s, u, a = beam.build_equations()
            eqs.extend(e)
            secondary_eqs.extend(s)
            unknowns_set.update(u)
            all_symbols_set.update(a)

        unknowns = list(unknowns_set)
        all_symbols = list(all_symbols_set)

        if len(unknowns) > len(eqs):
            raise TooManyUnknownsError("Слишком много неизвестных!")

        print('---eqs---')
        for i in eqs:
            print(i)

        print('---secondary_eqs---')
        for i in secondary_eqs:
            print(i)

        print('---unknowns---')
        print(unknowns)

        print('---all_symbols---')
        print(all_symbols)

        print()
        solution = sp.solve(eqs + secondary_eqs, sp.symbols(all_symbols))

        if len(solution) < 1:
            raise UnsolvableError("Невозможно найти решение либо система подвижна!")

        try:
            raw_answer = {str(k): round(float(v), 2) for k, v in solution.items() if str(k) in unknowns}
            return Beam.format_readable_answers(raw_answer)
        except Exception as e:
            raise UnsolvableError("Невозможно найти решение либо система подвижна!")

    def __repr__(self):
        return f"Beam(segments={self.get_segments()})"
    
    def pretty_print(self, indent=0):
        pad = ' ' * indent
        lines = [f"{pad}Beam#{self.id}:"]
        lines.append(f"{pad} Nodes:")
        for node in self.get_nodes():
            lines.append(node.pretty_print(indent + 2))
        lines.append(f"{pad} Segments:")
        for segment in self.get_segments():
            lines.append(segment.pretty_print(indent + 2))
        return '\n'.join(lines)
    
    def split_beam_by_hinges(self) -> list["Beam"]:
        hinge_nodes = [n for n in self.graph.nodes if n.hinge is not None]
        g_wo_hinges = self.graph.copy()
        g_wo_hinges.remove_nodes_from(hinge_nodes)
        components = list(nx.connected_components(g_wo_hinges))

        subbeams = []
        node_to_subbeam = {}

        for nodes in components:
            extended_nodes = set(nodes)

            for node in nodes:
                for neighbor in self.graph.neighbors(node):
                    if neighbor.hinge is not None:
                        extended_nodes.add(neighbor)

            subgraph = self.graph.subgraph(extended_nodes)
            beam = Beam()
            for u, v, data in subgraph.edges(data=True):
                beam.add_segment_exist(data['object'])

            for node in subgraph.nodes:
                node_to_subbeam[node] = beam

            subbeams.append(beam)

        for hinge_node in hinge_nodes:
            hinge = hinge_node.hinge
            if not hinge:
                continue

            for neighbor in self.graph.neighbors(hinge_node):
                beam = node_to_subbeam.get(neighbor)
                if beam:
                    hinge.assign_body(beam)

        return subbeams