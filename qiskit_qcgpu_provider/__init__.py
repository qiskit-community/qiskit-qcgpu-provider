"""Provider for local QCGPU backends."""

from qiskit.backends import BaseProvider
from qiskit.backends.providerutils import filter_backends

from .statevector_simulator import QCGPUStatevectorSimulator

class QCGPUProvider(BaseProvider):
    """Provider for local QCGPU backends."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        # Populate the list of local backends
        self._backends = [QCGPUStatevectorSimulator(provider=self)]

    def get_backend(self, name=None, **kwargs):
        """Get a backend from the provider"""
        return super().get_backend(name=name, **kwargs)
    
    def backends(self, name=None, filters=None, **kwargs):
        if name:
            val = {'name': name}
            val.update(kwargs)
            # kwargs.update({'name', name})
        
        return filter_backends(self._backends, filters=filters, **kwargs)

    def __str__(self):
        return "QCGPUProvider"