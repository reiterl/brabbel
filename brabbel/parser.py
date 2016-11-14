import logging
from threading import Lock
from builtins import object

from pyparsing import (
    ParserElement,
    Forward,
    Literal, Word,
    Combine, Group, Optional,
    nums, alphanums, alphas, sglQuotedString,
    delimitedList,
    opAssoc, infixNotation, oneOf)

from brabbel.operators import operators
from brabbel.functions import functions
from brabbel.nodes import (
    Const, Func, Variable, Binary, Unary, List, Not, And, Or)


"""
number    :: '0'..'9'+
string    :: '0'..'9''a'..'z''_'+
variable  :: '$' string

"""
log = logging.getLogger(__name__)
ParserElement.enablePackrat()

########################################################################
#                               Helpers                                #
########################################################################


def _str(s):
    return unicode(s.strip("'"))


def _number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def _make_func(s, loc, toks):
    name = toks['name']
    args = toks['args']
    fn = functions[name]
    arity = len(args)
    if arity == 1:
        return Unary(fn, args[0])
    if arity == 2:
        return Binary(fn, args[0], args[1])
    return Func(fn, args[:])

def _make_binary(create = lambda op, a, b: Binary(op, a, b)):
    def make(s, loc, toks):
        toks = toks[0]
        a, op, b = toks[0], toks[1], toks[2]

        a = create(operators[op], a, b)

        remaining = iter(toks[3:])
        while True:
            op = next(remaining, None)
            if op is None:
                break
            b = next(remaining)
            a = create(operators[op], a, b)

        return a
    return make

def _make_unary(create = lambda op, a: Unary(op, a)):
    def make(s, loc, toks):
        toks = toks[0]
        return create(operators[toks[0]], toks[1])
    return make

########################################################################
#                                ATOMS                                 #
########################################################################
lpar = Literal("(")
lbr = Literal("[")
rpar = Literal(")")
rbr = Literal("]")
lquote = Literal("'")
rquote = Literal("'")
number = Combine(Optional("-") + Word(nums + '.'))
# TODO: Remove "-" from list of allowed chars. Is only here for
# compatibility. (None) <2014-10-28 14:04>
variable = Combine("$" + Word(alphanums + "_" + "-" + "."))
# FIXME: sglquotedstring will fail if the string contains a single
# quote. (ti) <2015-09-29 13:54>
string = sglQuotedString.copy()
identifier = Word(alphas + "_")
none = Literal("None")
true = Literal("True")
false = Literal("False")
atom = Forward()
infix = infixNotation(atom,
    [
    ('not', 1, opAssoc.RIGHT, _make_unary(lambda op, a: Not(a))),
    (oneOf('* /'), 2, opAssoc.LEFT, _make_binary()),
    (oneOf('+ -'), 2, opAssoc.LEFT, _make_binary()),
    (oneOf('> gt >= ge < lt <= le != ne == eq'),
        2, opAssoc.LEFT, _make_binary()),
    ('and', 2, opAssoc.LEFT, _make_binary(lambda op, a, b: And(a, b))),
    ('or', 2, opAssoc.LEFT, _make_binary(lambda op, a, b: Or(a, b))),
    ('in', 2, opAssoc.LEFT, _make_binary()),
    ])
dellist = delimitedList(Optional(atom))
listing = lbr.suppress() + dellist + rbr.suppress()
function = identifier.setResultsName('name') + lpar.suppress() + Group(
        Optional(delimitedList(atom))).setResultsName("args") + rpar.suppress()
atom <<= listing | number | string | variable | true | false | none | function

_false = Const(False)
_true = Const(True)

number.setParseAction(lambda t: Const(_number(t[0])))
variable.setParseAction(lambda t: Variable(t[0].strip("$")))
string.setParseAction(lambda t: Const(_str(t[0])))
none.setParseAction(lambda t: _false)
false.setParseAction(lambda t: _false)
true.setParseAction(lambda t: _true)
dellist.setParseAction(lambda s, l, t: List(t[:]))
function.setParseAction(_make_func)
atom.setParseAction(lambda s, l, t: t[0])

class Parser(object):

    """Parser class for python expression."""

    lock = Lock()

    def __init__(self):
        """@todo: to be defined1. """
        pass

    def parse(self, expr):
        """Returns the BNF-Tree of the given expression

        :expr: String of the expression
        :returns: Returns the parsed BNF form the the expression

        """
        try:
            with Parser.lock:
                return infix.parseString(expr)
        except Exception:
            log.exception("Error on parsing %s" % expr)
