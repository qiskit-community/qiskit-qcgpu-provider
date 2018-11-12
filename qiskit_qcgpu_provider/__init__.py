"""Provider for local QCGPU backends."""

from qiskit.backends import BaseProvider
from qiskit.backends.providerutils import filter_backends

from .statevector_simulator import QCGPUStatevectorSimulator
from .qasm_simulator import QCGPUQasmSimulator

import qcgpu

class QCGPUProvider(BaseProvider):
    """Provider for local QCGPU backends."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        qcgpu.backend.create_context()

        self._backends = [QCGPUQasmSimulator(provider=self),
                          QCGPUStatevectorSimulator(provider=self)]
        
    def get_backend(self, name=None, **kwargs):
        return super().get_backend(name=name, **kwargs)

    def backends(self, name=None, filters=None, **kwargs):
        # pylint: disable=arguments-differ
        if name:
            kwargs.update({'name': name})

        return filter_backends(self._backends, filters=filters, **kwargs)
    
    def __str__(self):
        return 'QCGPU Provider'