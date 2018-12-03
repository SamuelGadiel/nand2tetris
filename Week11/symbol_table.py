#  The Compiler compiles each class (.jack file) individually so for each
#  .jack file compiled we be keeping the state of 1 class_scope and
#  subroutine scope

class_scope = {}
subroutine_scope = {}

STATIC = 'static'
FIELD = 'field'
ARGUMENT = 'argument'
LOCAL = 'local'

CLASS_KINDS = [STATIC, FIELD]
SUBROUTINE_KINDS = [ARGUMENT, LOCAL]


def _get_scope(kind):
    return {
        STATIC: class_scope,
        FIELD: class_scope,
        ARGUMENT: subroutine_scope,
        LOCAL: subroutine_scope
    }[kind]


def define(name, _type, kind):
    """
    type is a python reserved word, so using _type instead.
    Stores the name as key and a tuple of (_type, kind, index) as its value
    """
    _get_scope(kind)[name] = (_type, kind, var_count(kind))


def var_count(kind):
    return len(filter(lambda x: x[1] == kind, _get_scope(kind).values()))


def kind_of(name):
    return ((name in class_scope and class_scope[name][1]) or
            (name in subroutine_scope and subroutine_scope[name][1]) or
            None)


def type_of(name):
    return ((name in class_scope and class_scope[name][0]) or
            (name in subroutine_scope and subroutine_scope[name][0]) or
            None)


def index_of(name):
    return ((name in class_scope and class_scope[name][2]) or
            (name in subroutine_scope and subroutine_scope[name][2]) or
            0)


def start_subroutine():
    global subroutine_scope

    subroutine_scope = {}
