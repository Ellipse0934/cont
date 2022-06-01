class Ptr:
    def __init__(self, typ: type = object):
        self.typ = typ
    def __eq__(self, other) -> bool:
        if isinstance(other, Ptr):
            return self.typ == other.typ
        return False
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

class Int:
    def __eq__(self, other) -> bool:
        return isinstance(other, Int)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)