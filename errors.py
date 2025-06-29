"""
errors.py — система пользовательских исключений.

Содержит иерархию исключений, используемых в structures.py и dialogs.py:
ошибки геометрии, некорректного ввода, невозможности решения и др.

Позволяет централизованно обрабатывать ошибки и выводить сообщения пользователю.
"""

class BaseError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UnsolvableError(BaseError):
    pass

class TooManyUnknownsError(BaseError):
    pass

class NegativeOrZeroValueError(BaseError):
    pass

class NotANumberError(BaseError):
    pass

class DividedBeamError(BaseError):
    pass

class IncorrectInputError(BaseError):
    pass

class NonExistentError(BaseError):
    pass

class NoBeamError(BaseError):
    pass

class NoSupportsError(BaseError):
    pass

class DotBeamError(BaseError):
    pass

class HighDistanceError(BaseError):
    pass