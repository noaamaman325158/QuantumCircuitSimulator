# This exception is the base exception for all custom exceptions in the module. It is a subclass of the built-in Exception class. The other custom exceptions in the module are subclasses of this base exception. This allows for a common base class for all custom exceptions in the module, which can be used to catch all custom exceptions in a single except block. This is a common pattern in Python exception handling, where a base exception class is used to group related exceptions together.
class QuantumCircuitError(Exception):
    """Base class for exceptions in this module."""
    pass