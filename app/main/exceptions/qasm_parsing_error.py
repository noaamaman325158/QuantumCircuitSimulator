class QASMParsingError(Exception):
    """
    Custom exception for QASM circuit parsing errors.

    Attributes:
        message (str): Detailed error message
        original_qasm (str): Original QASM circuit string
    """

    def __init__(self, message: str, original_qasm: str = None):
        """
        Initialize the QASMParsingError.

        Args:
            message (str): Error description
            original_qasm (str, optional): The original QASM circuit string
        """
        self.message = message
        self.original_qasm = original_qasm

        super().__init__(message)

    def to_dict(self):
        """
        Convert the exception to a dictionary for easy serialization.

        Returns:
            dict: A dictionary representation of the error
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "original_qasm": self.original_qasm
        }