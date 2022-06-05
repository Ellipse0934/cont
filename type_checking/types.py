from state import State, Struct

class Ptr:
    def __init__(self, typ = None):
        self.typ = typ

    def __eq__(self, other) -> bool:
        if isinstance(other, Ptr):
            return self.typ == other.typ or other.typ is None or self.typ is None 
        return False
        
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

class Int:
    def __eq__(self, other) -> bool:
        return isinstance(other, Int) or other is None

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

class Addr:
    def __eq__(self, other) -> bool:
        return isinstance(other, Addr) or other is None

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

def type_to_str(_type):
    """
    Converts cont type object to string
    """
    if isinstance(_type, Int):
        return "int"
    elif isinstance(_type, Addr):
        return "addr"
    elif isinstance(_type, Ptr):
        if _type.typ is not None:
            return "*" + type_to_str(_type.typ)
        else:
            return "ptr"
    elif isinstance(_type, Struct):
        return _type.name
    elif _type is None:
        return "any"
    else:
        assert False, f"Unimplemented type in type_to_str: {_type}"

def parse_type(token: tuple[str, str], error, auto_ptr: bool = True, allow_unpack: bool = False):
    State.loc = f"{State.filename}:{token[1]}"
    name = token[0]
    if name.startswith("*"):
        return Ptr(parse_type((token[0][1:], token[1]), error, auto_ptr=auto_ptr, allow_unpack=allow_unpack))
    elif name == "int":
        return Int()
    elif name == "ptr":
        return Ptr()
    elif name == "addr":
        return Addr()
    elif name in State.structures:
        if auto_ptr:
            return Ptr(State.structures[name])
        else:
            return State.structures[name]
    elif name.startswith("@") and allow_unpack:
        if name[1:] not in State.structures:
            State.throw_error(f"structure \"{name[1:]}\" was not found")
        return State.structures[name[1:]].fields_types
    else:
        State.throw_error(f"unknown type \"{token[0]}\" in {error}")

def sizeof(_type) -> int:
    if isinstance(_type, Int) or isinstance(_type, Ptr) and isinstance(_type, Addr):
        return 8
    elif isinstance(_type, Struct):
        return sum([sizeof(field) for field in _type.fields_types])
    elif _type is None:
        State.throw_error("cant get size of any")
    else:
        assert False, f"Unimplemented type in sizeof: {_type}"
    
    return 0 # Mypy, shut up!

def check_contravariant(got: Struct, exp: Struct) -> bool:
    """
    Not recomended to use raw, use check_varient instead
    If you only need contravariant check, refactor this function to work in all cases
    Now it only works with structures
    """
    for i in got.children:
        if i is exp:
            return True
        if check_contravariant(i, exp):
            return True

    return False


def check_varient(got: object, exp: object):
    if isinstance(exp, Int) and isinstance(got, Int):
        return True
    if isinstance(exp, Addr) and isinstance(got, Addr):
        return True
    if isinstance(exp, Ptr) and isinstance(got, Ptr):
        return check_varient(got.typ, exp.typ) or exp.typ is None or got.typ is None
    if isinstance(exp, Struct) and isinstance(got, Struct):
        # equal is covariant
        return got == exp or check_contravariant(got, exp)

    return False

def down_cast(type1: object, type2: object) -> object:
    """
    Finds object lower in hierarchy and returns it
    BEFORE CALLING ENSURE, THAT TYPES ARE RELATED
    """
    if type1 == type2:
        return type2
    else:
        return type1