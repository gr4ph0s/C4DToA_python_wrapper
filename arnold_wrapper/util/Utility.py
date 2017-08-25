import inspect
import ctypes
from .Const import Const

class Utility(Const):
    def _hash_id(self, parameter_name):
        if not isinstance(parameter_name, str):
            if self.DEBUG: print("{}.{} -> parameter_name not str".format(
                self.__class__.__name__,
                inspect.stack()[0][3]
            ))
            return False

        h = 5381
        for c in parameter_name:
            h = (h << 5) + h + ord(c)
        h = ctypes.c_int32(h).value
        if h < 0: h = -h

        return h