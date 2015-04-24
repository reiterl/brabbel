from __future__ import division
from builtins import str
from datetime import date


########################################################################
#                              Operators                               #
########################################################################


def _in(a, b):
    return a in b

def _div(a, b):
    """Returns float in all cases"""
    return a / b

########################################################################
#                              Functions                               #
########################################################################


def _date(ds):
    """Will convert a given string into a date object. The given date can have the following format:

    today
        Will generate to current date
    YYYYMMDD
        Will generate the date of year (YYYY) month (MM) day (DD)

    :v: Value to be checked
    :returns: Date object

    """
    if ds in ["'today'", 'today']:
        return date.today()
    else:
        ds = ds.strip("'")
        y = int(ds[0:4])
        m = int(ds[4:6])
        d = int(ds[6:8])
    return date(y, m, d)


def _bool(v):
    """Will check if the given value is set and not empty. Empty means:

    * For String: No value or empty String
    * For Lists: No value or empty Lists
    * For Numbers: No value (0 is consideret as valid value)

    :Examples:

    >>> _bool(None)
    False
    >>> _bool('')
    False
    >>> _bool('  ')
    True
    >>> _bool([])
    False
    >>> _bool(0)
    True
    >>> _bool('foo')
    True

    :v: Value to be checked
    :returns: True or False

    """
    if v is None:
        return False
    if isinstance(v, str):
        if v == "''":
            return False
        else:
            return bool(v)
    elif isinstance(v, list):
        if len(v) == 0:
            return False
        elif v[0] == '':
            # FIXME: check why empty lists become [''] after parsing.
            # (ti) <2014-10-23 10:56>
            return False
        else:
            return True
    else:
        return bool(str(v))


def _len(v):
    """Will return of the given value. For all values except a list the
    value will be converted into a string first and the length of the
    string will be returned. In case of a None value the length will be
    0.

    :Examples:

    >>> _len(1.0)
    3
    >>> _len(1234)
    4
    >>> _bool([1,2,3,4,5])
    5
    >>> _bool('')
    0
    >>> _bool(None)
    0

    :v: Value to be checked
    :returns: True or False

    """
    if isinstance(v, list):
        return len(v)
    elif v is None:
        return 0
    return len(unicode(v))
