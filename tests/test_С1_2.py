#https://www.youtube.com/watch?v=Jed7uLL7xr8

from structures import *
from serialization import *

nodes = [
    Node(-3, 0),
    Node(3, 0),
]

nodes[0].add_support(Support(Support.Type.PINNED, 0, 0, 0, 0, True, True, False))
nodes[1].add_support(Support(Support.Type.ROLLER, 0, 0, 0, 0, False, True, False))

segments = [
    BeamSegment(nodes[0], nodes[1])
]

segments[0].add_force(Force(10000, 270, 1, 2, False))
segments[0].add_torque(Torque(20000, 0, False))
segments[0].add_force(Force(30000, 270, 4, 1, False))

beam = Beam(segments)
save_beam_to_file(beam, "beam_C1_2.bm")
print(beam.solve())