#Яблонский С4 5 вариант (https://teor-meh.ru/catalog/s4/variant_5_5.html)

from structures import *
from serialization import *

# Создаём балку
beam = Beam()

# Массив узлов
nodes = [
    beam.add_node(Node(0, 0)),
    beam.add_node(Node(1, 1)),
    beam.add_node(Node(3, 3)),
    beam.add_node(Node(5, 3)),
    beam.add_node(Node(3, 0)),
]

# Добавляем опоры
nodes[0].add_support(Support(Support.Type.PINNED, 0, 0, 0, 0, True, True, False))
nodes[1].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))
nodes[2].add_hinge()
nodes[3].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))
nodes[4].add_support(Support(Support.Type.ROLLER, 90, 0, 0, 0, False, True, False))

# Массив сегментов
segments = [
    beam.add_segment(BeamSegment(nodes[0], nodes[1])),
    beam.add_segment(BeamSegment(nodes[1], nodes[2])),
    beam.add_segment(BeamSegment(nodes[2], nodes[3])),
    beam.add_segment(BeamSegment(nodes[2], nodes[4])),
]

# Добавляем нагрузки
segments[1].add_force(Force(1100, 315, math.sqrt(8)/2, math.sqrt(8), False))
segments[2].add_force(Force(8000, 240, 1, 1, False))
segments[3].add_force(Force(15000, 180, 1.5, 1, False))
segments[1].add_torque(Torque(-22000, 1, False))

save_beam_to_file(beam, "beam_C4_2.bm")

print(beam.solve())