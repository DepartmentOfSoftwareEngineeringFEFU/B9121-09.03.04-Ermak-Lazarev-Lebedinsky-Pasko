import json
from structures import Beam, BeamSegment, Node, Force, Torque, Support, Hinge


def beam_to_dict(beam: Beam) -> dict:
    return {
        'nodes': [
            {
                'id': node.id,
                'x': node.x,
                'y': node.y,
                'support': {
                    'id': node.support.id,
                    'type': node.support.support_type.value,
                    'angle': node.support.angle,
                    'force': {
                        'id': node.support.force.id,
                        'value': node.support.force.value,
                        'angle': node.support.force.angle,
                        'node1_dist': node.support.force.node1_dist,
                        'length': node.support.force.length,
                        'unknown_x': node.support.force.unknown_x,
                        'unknown_y': node.support.force.unknown_y
                    },
                    'torque': {
                        'id': node.support.torque.id,
                        'value': node.support.torque.value,
                        'node1_dist': node.support.torque.node1_dist,
                        'unknown': node.support.torque.unknown
                    }
                } if node.support else None,
                'hinge_id': node.hinge.id if node.hinge else None
            }
            for node in beam.get_nodes()
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
                        'unknown': force.unknown_x or force.unknown_y
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
            for segment in beam.get_segments()
        ],
        'hinges': [
            {
                'id': hinge.id,
                'node_ids': [node.id for node in beam.graph.nodes if node.hinge == hinge]
            }
            for hinge in {node.hinge for node in beam.get_nodes() if node.hinge}
        ]
    }


def save_beam_to_file(beam: Beam, filename: str = "beam.bm"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(beam_to_dict(beam), f, indent=4)


def load_beam_from_file(filename: str, beam: Beam):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    beam.graph.clear()
    id_node_map = {}

    for node_data in data['nodes']:
        node = Node(node_data['x'], node_data['y'], custom_id=node_data['id'])
        if node_data['support']:
            s = node_data['support']
            support = Support(
                support_type=Support.Type(s['type']),
                angle=s['angle'],
                force_x=s['force']['value'],
                force_y=0,
                torque=s['torque']['value'],
                unknown_fx=s['force']['unknown_x'],
                unknown_fy=s['force']['unknown_y'],
                unknown_t=s['torque']['unknown'],
                custom_id=s['id'],
                is_new=False
            )
            support.force.id = s['force']['id']
            support.torque.id = s['torque']['id']
            node.add_support(support)
        id_node_map[node.id] = beam.add_node(node)

    hinge_map = {}
    if 'hinges' in data:
        for h in data['hinges']:
            hinge = Hinge(custom_id=h['id'])
            hinge_map[hinge.id] = hinge
            for node_id in h['node_ids']:
                node = id_node_map[node_id]
                node.hinge = hinge
                #hinge.assign_body(beam)

    for segment_data in data['segments']:
        node1 = id_node_map[segment_data['node1_id']]
        node2 = id_node_map[segment_data['node2_id']]
        segment = beam.add_segment_new(node1, node2, custom_id=segment_data['id'])

        for f in segment_data['forces']:
            force = Force(
                f['value'], f['angle'], f['node1_dist'],
                f['length'], f['unknown'], custom_id=f['id']
            )
            segment.add_force(force)

        for t in segment_data['torques']:
            torque = Torque(
                t['value'], t['node1_dist'], t['unknown'], custom_id=t['id']
            )
            segment.add_torque(torque)
