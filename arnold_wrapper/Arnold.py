"""Wrapper class for doing basic stuff with any arnold material.
Make sure to call set_mat before any other call, or it will fail.
"""

__author__ = 'Adam Maxime - Graphos <gr4ph0s(at)hotmail.fr>'
__version__ = '1.0'

import c4d
import inspect

from .object.Connection import Connection
from .object.Message import Message
from .object.Node import Node

class Arnold(Message):
    mat = None

    def _connect_root(self, node, node_id, root_id):
        # Create a message object for create a new shader
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_CONNECT_ROOT_SHADER, node, node_id, root_id):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return bool(buffer[0])

    def _disconnect_root(self, root_id):
        # Create a message object for create a new shader
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_DISCONNECT_ROOT_SHADER, root_id):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return bool(buffer[0])

    def set_mat(self, mat):
        if not mat: return False
        if not mat.CheckType(self.ARNOLD_MATERIAL): return False

        self.mat = mat

    def get_material_informations(self):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Create a message object for query the network
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_QUERY_SHADER_NETWORK):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Build dict from data received
        datas = dict()
        datas["nb_node"] = buffer[0]
        datas["nb_connection"] = buffer[1]
        datas["beauty_node"] = Node(buffer[2])
        datas["displace_node"] = Node(buffer[3])
        datas["all_nodes"] = list()
        for i in range(0, datas["nb_node"]):
            datas["all_nodes"].append(Node(bc.GetLink(10000 + i)))

        datas["all_connections"] = list()
        for i in range(0, datas["nb_connection"]):
            datas["all_connections"].append(Connection(bc.GetContainer(20000 + i)))

        return datas

    def create_shader(self, shader_type, shader_id, x, y):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(shader_type, int):
            if self.DEBUG: print("{}.{} -> shader_type called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(shader_id, int) and not isinstance(shader_id, str) and not isinstance(shader_id,
                                                                                                c4d.BaseMaterial):
            if self.DEBUG: print("{}.{} -> shader_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(shader_id, str):
            shader_id = self._hash_id(shader_id)

        if not isinstance(x, int):
            if self.DEBUG: print("{}.{} -> x called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(y, int):
            if self.DEBUG: print("{}.{} -> y called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Create a message object for create a new shader
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_ADD_SHADER, shader_type, shader_id, x, y):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if the shader was created
        if buffer[0] is None:
            if self.DEBUG: print("{}.{} -> Shader creation failed".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # return the shader node created
        return Node(buffer[0])

    def remove_shader(self, shader_to_remove):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(shader_to_remove, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> shader_to_remove called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Create a message object for create a new shader
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_REMOVE_SHADER, shader_to_remove):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return bool(buffer[0])

    def create_connection(self, output_node, output_id, input_node, input_id):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(output_node, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> output_node called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(output_id, int) and not isinstance(output_id, str):
            if self.DEBUG: print("{}.{} -> output_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(output_id, str): output_id = self._hash_id(output_id)

        if not isinstance(input_node, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> input_node called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if not isinstance(input_id, int) and not isinstance(input_id, str):
            if self.DEBUG: print("{}.{} -> input_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if isinstance(input_id, str): input_id = self._hash_id(input_id)

        # Create a message object for create a new shader
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_ADD_CONNECTION, output_node, output_id, input_node, input_id):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return bool(buffer[0])

    def remove_connection(self, node, node_id):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(node, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> node called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(node_id, int) and not isinstance(node_id, str):
            if self.DEBUG: print("{}.{} -> node_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(node_id, str): node_id = self._hash_id(node_id)

        # Create a message object for create a new shader
        mess = Message()
        if not mess.set_data(self.mat, self.C4DTOA_MSG_REMOVE_CONNECTION , node, node_id):
            if self.DEBUG: print("{}.{} -> Message.set_data can't initialize".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Send the message
        mess.send()

        # Get data from message
        buffer, bc = mess.get_data()
        if not buffer:
            if self.DEBUG: print("{}.{} -> recieved nothing".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return bool(buffer[0])

    def connect_beauty(self, node, node_id):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(node, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> node called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(node_id, int) and not isinstance(node_id, str):
            if self.DEBUG: print("{}.{} -> node_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(node_id, str): node_id = self._hash_id(node_id)


        return self._connect_root(node, node_id, self.ARNOLD_BEAUTY_PORT_ID)

    def connect_displacement(self, node, node_id):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(node, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> node called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(node_id, int) and not isinstance(node_id, str):
            if self.DEBUG: print("{}.{} -> node_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(node_id, str): node_id = self._hash_id(node_id)


        return self._connect_root(node, node_id, self.ARNOLD_DISPLACEMENT_PORT_ID)

    def connect_viewport(self, node, node_id):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # Check if value filled are correct
        if not isinstance(node, c4d.modules.graphview.GvNode):
            if self.DEBUG: print("{}.{} -> node called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if not isinstance(node_id, int) and not isinstance(node_id, str):
            if self.DEBUG: print("{}.{} -> node_id called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(node_id, str): node_id = self._hash_id(node_id)


        return self._connect_root(node, node_id, self.ARNOLD_VIEWPORT_PORT_ID)

    def disconnect_beauty(self):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return self._disconnect_root(self.ARNOLD_BEAUTY_PORT_ID)

    def disconnect_displacement(self):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return self._disconnect_root(self.ARNOLD_DISPLACEMENT_PORT_ID)

    def disconnect_viewport(self):
        # Check if mat is set
        if not self.mat:
            if self.DEBUG: print("{}.{} -> mat not initialized".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return self._disconnect_root(self.ARNOLD_VIEWPORT_PORT_ID)