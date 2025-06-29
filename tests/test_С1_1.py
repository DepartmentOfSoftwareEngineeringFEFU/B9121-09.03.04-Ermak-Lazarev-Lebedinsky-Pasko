#https://isopromat.ru/tehmeh/reshenie-zadach/opredelenie-reakcij-opor-balki-sila-pod-uglom

from structures import *
from serialization import *

# Создаём балку
beam = Beam()

# Массив узлов
nodes = [
    beam.add_node(Node(-17, 1)),
    beam.add_node(Node(-11, 1)),
    beam.add_node(Node(-1, 1))
]

# Добавляем опоры
nodes[1].add_support(Support(Support.Type.PINNED, 0, 0, 0, 0, True, True, False))
nodes[2].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))

# Массив сегментов
segments = [
    beam.add_segment(BeamSegment(nodes[0], nodes[1])),
    beam.add_segment(BeamSegment(nodes[1], nodes[2]))
]

# Добавляем нагрузки
segments[0].add_force(Force(10, 215, 0, 1, False))
segments[1].add_torque(Torque(8, 0, False))
segments[1].add_force(Force(4, 270, 2.5, 5, False))

save_beam_to_file(beam, "beam_C1_1.bm")

# Решаем систему
print(beam.solve())