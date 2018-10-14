"""
Exception for errors raised by QCGPU simulators
"""

from qiskit import QISKitError


class QCGPUSimulatorError(QISKitError):
    """Base class for errors raised by simulators."""

    def __init__(self, *message):
        """Set the error message"""
        super().__init__(*message)
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message"""
        return repr(self.message)
