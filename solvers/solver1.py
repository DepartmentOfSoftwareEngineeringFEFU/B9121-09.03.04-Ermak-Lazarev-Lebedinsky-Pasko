from structures import *

class Solver1:
    def __init__(self, segments=[]):
        self.segments = segments
        self.nodes = set()
        for s in segments:
            self.nodes.add(s.node1)
            self.nodes.add(s.node2)
        self.nodes = list(self.nodes)
        self.base_node = None

    def add_segment(self, segment):
        self.segments.append(segment)

    def solve(self):
        fx = array([])
        fy = array([])
        t = array([])

        for n in self.nodes:
            if n.support != None and (n.support.v_force < 0 or n.support.h_force < 0 or n.support.torque < 0):
                self.base_node = n
                break

        for n in self.nodes:
            if n.support != None:
                if n.support.v_force > 0:
                    force_part = n.support.v_force * np.cos(np.deg2rad(n.support.angle))
                    fx = np.append(fx, force_part)
                    t = np.append(t, force_part * (n.y - self.base_node.y))

                    force_part = n.support.v_force * np.sin(np.deg2rad(n.support.angle))
                    fy = np.append(fy, force_part)
                    t = np.append(t, -force_part * (n.x - self.base_node.x))

                if n.support.h_force > 0:
                    force_part = n.support.h_force * np.cos(np.deg2rad(n.support.angle))
                    fx = np.append(fx, force_part)
                    t = np.append(t, force_part * (n.y - self.base_node.y))

                    force_part = n.support.h_force * np.sin(np.deg2rad(n.support.angle))
                    fy = np.append(fy, force_part)
                    t = np.append(t, -force_part * (n.x - self.base_node.x))

                if n.support.torque> 0:
                    if n.support.torq_dir:
                        t = np.append(t, n.support.torque)
                    else:
                        t = np.append(t, -n.support.torque)

        for s in self.segments:
            for f in s.forces:
                force_part = f.value * np.cos(np.deg2rad(f.angle))
                fx = np.append(fx, force_part)
                t = np.append(t, force_part * (s.node1.y + f.node1_dist * (s.node2.y - s.node1.y) / s.length - self.base_node.y))

                force_part = f.value * np.sin(np.deg2rad(f.angle))
                fy = np.append(fy, force_part)
                t = np.append(t, -force_part * (s.node1.x + f.node1_dist * (s.node2.x - s.node1.x) / s.length - self.base_node.x))
            for torq in s.torques:
                if torq.direction:
                    t = np.append(t, torq.value)
                else:
                    t = np.append(t, -torq.value)
        temp = np.round(-np.sum(fx), 5)
        result = f"Горизонтальная реакция опоры: {temp if temp != 0 else 0.0}\n"
        temp = np.round(-np.sum(fy), 5)
        result += f"Вертикальная реакция опоры: {temp if temp != 0 else 0.0}\n"
        temp = np.round(-np.sum(t), 5)
        result += f"Момент реакции опоры: {temp if temp != 0 else 0.0}"
        return result

    def __repr__(self):
        return f"Beam(segments={self.segments})"
    
class Support:
    def __init__(self, angle, v_force, h_force, torque, torq_dir=False):
        self.angle = angle
        self.v_force = v_force
        self.h_force = h_force
        self.torque = torque
        self.torq_dir = torq_dir

    def __repr__(self):
        return f"Support(angle={self.angle}, v_force={self.v_force}, h_force={self.h_force}, torque={self.torque})"

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.beam_segments = []
        self.support = None

    def add_beam_segment(self, beam_segment):
        self.beam_segments.append(beam_segment)

    def add_support(self, support):
        self.support = support

    def __repr__(self):
        return f"Node(coords=({self.x}, {self.y}), support={self.support})"