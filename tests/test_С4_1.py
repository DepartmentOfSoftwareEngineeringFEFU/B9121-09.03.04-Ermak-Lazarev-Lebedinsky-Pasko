#Яблонский С4 29 вариант (https://teor-meh.ru/catalog/s4/variant_29_4.html)

from structures import *
from serialization import *

# Создаём балку
beam = Beam()

# Массив узлов
nodes = [
    beam.add_node(Node(0, 0.5)),
    beam.add_node(Node(2, 3)),
    beam.add_node(Node(4, 3)),
    beam.add_node(Node(6, 3)),
    beam.add_node(Node(8, 3)),
    beam.add_node(Node(4, 0.5)),
]

# Добавляем опоры
nodes[0].add_support(Support(Support.Type.FIXED, 315, 0, 0, 0, True, True, True))
nodes[4].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))
nodes[5].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))
nodes[1].add_hinge()
nodes[3].add_hinge()

# Массив сегментов
segments = [
    beam.add_segment(BeamSegment(nodes[0], nodes[1])),
    beam.add_segment(BeamSegment(nodes[1], nodes[2])),
    beam.add_segment(BeamSegment(nodes[2], nodes[3])),
    beam.add_segment(BeamSegment(nodes[3], nodes[4])),
    beam.add_segment(BeamSegment(nodes[2], nodes[5])),
]

# Добавляем нагрузки
segments[0].add_torque(Torque(29000, 3, False))
segments[3].add_torque(Torque(-37000, 1, False))
segments[4].add_force(Force(11000, 0, 1, 1, False))

save_beam_to_file(beam, "beam_C4_1.bm")

print(beam.solve())