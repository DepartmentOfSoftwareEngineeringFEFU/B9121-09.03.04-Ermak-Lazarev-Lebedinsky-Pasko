#Яблонский С3 5 вариант (https://teor-meh.ru/catalog/s3/variant_5_4.html)

from structures import *
from serialization import *

# Создаём балку
beam = Beam()

# Массив узлов
nodes = [
    beam.add_node(Node(1, 1)),
    beam.add_node(Node(1, 4)),
    beam.add_node(Node(4, 4)),
    beam.add_node(Node(4, 3)),
    beam.add_node(Node(6, 3)),
    beam.add_node(Node(9, 3)),
]

# Добавляем опоры
nodes[0].add_support(Support(Support.Type.FIXED, 0, 0, 0, 0, True, True, True))
nodes[2].add_hinge()
nodes[4].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))

# Массив сегментов
segments = [
    beam.add_segment(BeamSegment(nodes[0], nodes[1])),
    beam.add_segment(BeamSegment(nodes[1], nodes[2])),
    beam.add_segment(BeamSegment(nodes[2], nodes[3])),
    beam.add_segment(BeamSegment(nodes[3], nodes[4])),
    beam.add_segment(BeamSegment(nodes[4], nodes[5])),
]

# Добавляем нагрузки
segments[1].add_force(Force(1600, 270, 1.5, 3, False))
segments[3].add_torque(Torque(-16000, 1, False))
segments[4].add_force(Force(9000, 330, 3, 1, False))

save_beam_to_file(beam, "beam_C3_2.bm")

print(beam.solve())