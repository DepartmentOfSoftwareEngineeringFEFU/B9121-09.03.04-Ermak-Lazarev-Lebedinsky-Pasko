#https://www.youtube.com/watch?v=HSRy3sd34P8

from structures import *
from serialization import *

# Создаём балку
beam = Beam()

# Массив узлов
nodes = [
    beam.add_node(Node(-1, 0)),
    beam.add_node(Node(-1, 2)),
    beam.add_node(Node(1, 2)),
    beam.add_node(Node(2, 0)),
]

# Добавляем опоры
nodes[0].add_support(Support(Support.Type.PINNED, 0, 0, 0, 0, True, True, False))
nodes[2].add_hinge()
nodes[3].add_support(Support(Support.Type.PINNED, 0, 0, 0, 0, True, True, False))

# Массив сегментов
segments = [
    beam.add_segment(BeamSegment(nodes[0], nodes[1])),
    beam.add_segment(BeamSegment(nodes[1], nodes[2])),
    beam.add_segment(BeamSegment(nodes[2], nodes[3]))
]

# Добавляем нагрузки
segments[0].add_torque(Torque(-20000, 0, False))
segments[1].add_force(Force(15000, 270, 1, 1, False))
segments[1].add_force(Force(2000, 270, 1, 2, False))
segments[2].add_force(Force(10000, 180, math.sqrt(5)/2, 1, False))

save_beam_to_file(beam, "beam_C3_1.bm")

print(beam.solve())