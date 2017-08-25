import c4d

from ..util.Utility import Utility
from .Node import Node


class Connection(Utility):
    input_node = None
    input_port = None
    output_node = None
    output_port = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if not self.input_port or not self.input_node or not self.output_port or not self.output_node:
            return None

        string = "input: {}-{} // output port: {}-{}".format(
            self.input_port,
            self.input_node,
            self.output_port,
            self.output_node
        )
        return string

    def __init__(self, bc):
        self.input_node = Node(bc.GetLink(0))
        self.input_port = bc.GetInt32(1)
        self.output_node = bc.GetLink(2)
        self.output_port = Node(bc.GetInt32(3))