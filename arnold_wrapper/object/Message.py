import inspect
import c4d

from ..util.Utility import Utility

class Message(Utility):
    """
    UTILITY:
        Layer class of the arnold python API.
        Allow you to get directly c4d/python object without to deal of internal arnold API

    USAGE:
        Create one message object per call
        Basic workflow set_data => send => get_data
    """

    material = None
    msg_type = None
    params = list()
    resps = list()
    bc = None

    def __init__(self):
        # Associative list to know how many parameters are needed / receiveds for a given call
        self.aviable_type = {
            "{}".format(str(self.C4DTOA_MSG_QUERY_SHADER_NETWORK)): [[], [True] * 4],
            "{}".format(str(self.C4DTOA_MSG_ADD_SHADER)): [[True] * 4, [True]],
            "{}".format(str(self.C4DTOA_MSG_REMOVE_SHADER)): [[True], [True]],
            "{}".format(str(self.C4DTOA_MSG_ADD_CONNECTION)): [[True] * 4, [True]],
            "{}".format(str(self.C4DTOA_MSG_REMOVE_CONNECTION)): [[True] * 2, [True]],
            "{}".format(str(self.C4DTOA_MSG_CONNECT_ROOT_SHADER)): [[True] * 3, [True]],
            "{}".format(str(self.C4DTOA_MSG_DISCONNECT_ROOT_SHADER)): [[True], [True]],
        }

    def _initialize_bc(self):
        self.bc = c4d.BaseContainer()
        self.bc.SetInt32(self.C4DTOA_MSG_TYPE, self.msg_type)
        for x in range(0, len(self.params)):
            self.bc.SetData(self.C4DTOA_MSG_PARAM1 + x, self.params[x])

    def set_data(self, mat, msg_type, *args):
        """
        Set data and build the c4d.BaseContainer who gonna be filled
        :param mat: c4d.BaseMaterial. The arnold BaseMaterial we gonna use
        :param msg_type: int. The message_id to pass
        :param args: params to be given (can't have more than 4 params)
        :return: True, if everythings is fine, False if something went wrong
        """
        # Check our msg_type is an integer
        if not isinstance(mat, c4d.BaseMaterial) or not mat.CheckType(self.ARNOLD_MATERIAL):
            if self.DEBUG: print("{} -> mat is not a good material".format(
                inspect.stack()[0][3]
            ))
            return False

        # Check our msg_type is an integer
        if not isinstance(msg_type, int):
            if self.DEBUG: print("{} -> msg_type not integer".format(
                inspect.stack()[0][3]
            ))
            return False

        # Check if msg_type is allowed
        if not str(msg_type) in self.aviable_type:
            if self.DEBUG: print("{} -> msg_type not allowed".format(
                inspect.stack()[0][3]
            ))
            return False

        # Check if the correct amount of msg_params are send
        resp_check = self.aviable_type[str(msg_type)][0]
        if len(resp_check) != len(args):
            if self.DEBUG: print("{} -> wrong arg numbers {} filled while {} excepted".format(
                inspect.stack()[0][3],
                len(resp_check),
                len(args)
            ))
            return False

        # if we are here everything it's fine with input,now save data
        self.material = mat
        self.msg_type = msg_type
        self.params = args

        # Then we build our bc
        self._initialize_bc()

        return True

    def send(self):
        self.material.Message(c4d.MSG_BASECONTAINER, self.bc)

    def get_data(self):
        """
        Read the result and put result in ordered list.
        :return: list of value returned, False if something fail
        it also return the bc, it can be usefull in some case
        """
        buffer = list()

        # Get data from bc
        resp_1 = self.bc[self.C4DTOA_MSG_RESP1]
        resp_2 = self.bc[self.C4DTOA_MSG_RESP2]
        resp_3 = self.bc[self.C4DTOA_MSG_RESP3]
        resp_4 = self.bc[self.C4DTOA_MSG_RESP4]

        # if there is data we add the buffer
        if self.bc.GetType(self.C4DTOA_MSG_RESP1) != c4d.DA_NIL:
            buffer.append(resp_1)
        else:  # Since there is always a return value, if the first value is none there is something wrong
            if self.DEBUG: print("{}.{} -> first respond is None".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        if self.bc.GetType(self.C4DTOA_MSG_RESP2) != c4d.DA_NIL:
            buffer.append(resp_2)

        if self.bc.GetType(self.C4DTOA_MSG_RESP3) != c4d.DA_NIL:
            buffer.append(resp_3)

        if self.bc.GetType(self.C4DTOA_MSG_RESP4) != c4d.DA_NIL:
            buffer.append(resp_4)

        # Check if the correct amount of msg_result are received
        resp_check = self.aviable_type[str(self.msg_type)][1]
        if len(resp_check) != len(buffer):
            if self.DEBUG: print("{}.{} -> wrong arg numbers {} received while {} excepted".format(
                self.__class__.__name__,
                inspect.stack()[0][3],
                len(resp_check),
                len(buffer)))
            return False

        return buffer, self.bc