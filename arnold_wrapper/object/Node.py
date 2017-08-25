import c4d
import inspect

from ..util.Utility import Utility

class Node(Utility):
    node = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.node:
            return self.node.GetName()
        else:
            return "None"

    def __init__(self, node):
        self.node = node

    def get_node(self):
        return self.node

    def get_type(self):
        return self.node.GetData().GetContainer(self.C4DTOA_MSG_TYPE).GetInt32(self.C4DAI_GVSHADER_TYPE)

    def get_parameter(self, parameter):
        if not isinstance(parameter, int) and not isinstance(parameter, str):
            if self.DEBUG: print("{}.{} -> parameter called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(parameter, str): parameter = self._hash_id(parameter)

        data = self.node.GetParameter(parameter, c4d.DESCFLAGS_GET_0)
        return data

    def set_parameter(self, parameter, value):
        if not isinstance(parameter, int) and not isinstance(parameter, str):
            if self.DEBUG: print("{}.{} -> parameter called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        # If it's a string, convert it into int
        if isinstance(parameter, str): parameter = self._hash_id(parameter)

        if value is None:
            if self.DEBUG: print("{}.{} -> value called with wrong type".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        return self.node.SetParameter(parameter, value, c4d.DESCFLAGS_SET_0)