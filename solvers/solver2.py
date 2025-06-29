import json
import math
from enum import Enum
import networkx as nx
import sympy as sp
from errors import *
from ids import IDNumerator
from structures import *

class Solver2:
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

    def add_segment(self, segment: BeamSegment) -> BeamSegment:
        node1 = self.add_node(segment.node1)
        node2 = self.add_node(segment.node2)

        if node1.x == node2.x and node1.y == node2.y:
            raise DotBeamError("Балка не может начинаться и заканчиваться в одной точке!")

        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]['object']

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

                node.support.horizontal_force.id = Force._next_id
                Force._used_ids.add(Force._next_id)
                Force._next_id += 1

                node.support.vertical_force.id = Force._next_id
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

            elif key.startswith('hinge_') and ('_force_x' in key or '_force_y' in key):
                hinge_id = key.split('_')[1]
                direction = 'горизонтальная' if '_force_x' in key else 'вертикальная'
                readable_answer[f"{direction.capitalize()} сила в шарнире {hinge_id}"] = value

            else:
                readable_answer[key] = value

        return readable_answer

    def build_equations(self):
        fx_dict, fy_dict, t_dict = {}, {}, {}

        def add_force_parts(name: str, force: Force, x: float, y: float):
            if force.get_type != Force.Type.VERTICAL:
                part = force.part_x
                fx_dict[f'{name}_x'] = '?' if force.unknown else part
                t_dict[f'{name}_x_torque'] = 0 if y == 0 else f'{-y}*{name}_x' if force.unknown else part * -y

            if force.get_type != Force.Type.HORIZONTAL:
                part = force.part_y
                fy_dict[f'{name}_y'] = '?' if force.unknown else part
                t_dict[f'{name}_y_torque'] = 0 if x == 0 else f'{x}*{name}_y' if force.unknown else part * x

        for node in self.get_nodes():
            if node.support:
                nid = f'node_{node.id}'
                add_force_parts(f'{nid}_vertical', node.support.vertical_force, node.x, node.y)
                add_force_parts(f'{nid}_horizontal', node.support.horizontal_force, node.x, node.y)
                t_dict[f'{nid}_torque'] = '?' if node.support.torque.unknown else node.support.torque.value

            elif node.hinge:
                hinge = node.hinge
                if hinge.body1 != self and hinge.body2 != self:
                    continue

                prefix = f'hinge_{hinge.id}'
                is_first = hinge.body1 == self

                name_x = f'{prefix}_force_x'
                name_y = f'{prefix}_force_y'

                if is_first:
                    fx_dict[name_x] = '?'
                    fy_dict[name_y] = '?'

                    t_dict[f'{name_x}_torque'] = f'{-node.y}*{name_x}' if node.y != 0 else 0
                    t_dict[f'{name_y}_torque'] = f'{node.x}*{name_y}' if node.x != 0 else 0
                else:
                    fx_dict[f'{name_x}_opp'] = f'-{name_x}'
                    fy_dict[f'{name_y}_opp'] = f'-{name_y}'

                    t_dict[f'{name_x}_opp_torque'] = f'{-node.y}*{name_x}_opp' if node.y != 0 else 0
                    t_dict[f'{name_y}_opp_torque'] = f'{node.x}*{name_y}_opp' if node.x != 0 else 0

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

        # if len(unknowns) > 3:
        #     raise TooManyUnknownsError("Невозможно найти больше трёх неизвестных!")

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

        raw_answer = {str(k): float(v) for k, v in solution.items() if str(k) in unknowns}

        return Beam.format_readable_answers(raw_answer)

    def __repr__(self):
        return f"Beam(segments={self.get_segments()})"
    
    def to_dict(self):
        return {
            'nodes': [
                {
                    'id': node.id,
                    'x': node.x,
                    'y': node.y,
                    'support': {
                        'id': node.support.id,
                        'angle': node.support.angle,
                        'horizontal_force': {
                            'id': node.support.horizontal_force.id,
                            'value': node.support.horizontal_force.value,
                            'angle': node.support.horizontal_force.angle,
                            'node1_dist': node.support.horizontal_force.node1_dist,
                            'length': node.support.horizontal_force.length,
                            'unknown': node.support.horizontal_force.unknown
                        },
                        'vertical_force': {
                            'id': node.support.vertical_force.id,
                            'value': node.support.vertical_force.value,
                            'angle': node.support.vertical_force.angle,
                            'node1_dist': node.support.vertical_force.node1_dist,
                            'length': node.support.vertical_force.length,
                            'unknown': node.support.vertical_force.unknown
                        },
                        'torque': {
                            'id': node.support.torque.id,
                            'value': node.support.torque.value,
                            'node1_dist': node.support.torque.node1_dist,
                            'unknown': node.support.torque.unknown
                        }
                    } if node.support else None
                }
                for node in self.get_nodes()
            ],
            'segments': [
                {
                    'id': segment.id,
                    'node1_id': segment.node1.id,
                    'node2_id': segment.node2.id,
                    'forces': [
                        {
                            'id': force.id,
                            'value': force.value,
                            'angle': force.angle,
                            'node1_dist': force.node1_dist,
                            'length': force.length,
                            'unknown': force.unknown
                        } for force in segment.forces
                    ],
                    'torques': [
                        {
                            'id': torque.id,
                            'value': torque.value,
                            'node1_dist': torque.node1_dist,
                            'unknown': torque.unknown
                        } for torque in segment.torques
                    ]
                }
                for segment in self.get_segments()
            ]
        }

    def save_to_file(self, filename: str = "beam.bm"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str = "beam.bm"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        id_node_map = {}
        beam = cls()

        for node_data in data['nodes']:
            node = Node(node_data['x'], node_data['y'], custom_id=node_data['id'])
            if node_data['support']:
                support_data = node_data['support']
                support = Support(
                    support_data['angle'],
                    support_data['horizontal_force']['value'],
                    support_data['vertical_force']['value'],
                    support_data['torque']['value'],
                    support_data['horizontal_force']['unknown'],
                    support_data['vertical_force']['unknown'],
                    support_data['torque']['unknown'],
                    custom_id=support_data['id']
                )
                support.horizontal_force.id = support_data['horizontal_force']['id']
                support.vertical_force.id = support_data['vertical_force']['id']
                support.torque.id = support_data['torque']['id']
                node.add_support(support)
            id_node_map[node.id] = beam.add_node(node)

        for segment_data in data['segments']:
            node1 = id_node_map[segment_data['node1_id']]
            node2 = id_node_map[segment_data['node2_id']]
            segment = BeamSegment(node1, node2, custom_id=segment_data['id'])

            for force_data in segment_data['forces']:
                force = Force(
                    force_data['value'],
                    force_data['angle'],
                    force_data['node1_dist'],
                    force_data['length'],
                    force_data['unknown'],
                    custom_id=force_data['id']
                )
                segment.add_force(force)

            for torque_data in segment_data['torques']:
                torque = Torque(
                    torque_data['value'],
                    torque_data['node1_dist'],
                    torque_data['unknown'],
                    custom_id=torque_data['id']
                )
                segment.add_torque(torque)

            beam.add_segment(segment)

        return beam
    
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

        for nodes in components:
            extended_nodes = set(nodes)

            hinge_neighbors = []
            for node in nodes:
                for neighbor in self.graph.neighbors(node):
                    if neighbor.hinge is not None:
                        extended_nodes.add(neighbor)
                        hinge_neighbors.append((node, neighbor))

            full_subgraph = self.graph.subgraph(extended_nodes)
            beam = Beam()
            for u, v, data in full_subgraph.edges(data=True):
                beam.add_segment(data['object'])

            for _, hinge_node in hinge_neighbors:
                hinge_node.hinge.assign_body(beam)

            subbeams.append(beam)

        return subbeams