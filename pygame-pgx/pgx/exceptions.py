class InvalidAppException(Exception): pass
class InvalidAttributeException(InvalidAppException): pass
class ChildrenNotPermittedException(InvalidAppException): pass