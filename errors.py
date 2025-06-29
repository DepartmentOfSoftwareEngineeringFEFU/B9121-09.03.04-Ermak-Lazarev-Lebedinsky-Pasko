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