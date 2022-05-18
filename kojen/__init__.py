if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


# http://mikegrouchy.com/blog/2012/05/be-pythonic-__init__py.html
#from .smgen import *
__all__ = ['smgen', 'cgen', 'vppclassdiagram', 'vppfs', 'kojentypes', 'umlgen', 'protogen', 'Generate']
