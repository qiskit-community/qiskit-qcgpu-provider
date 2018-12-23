"""Provider for local QCGPU backends."""

from collections import OrderedDict
import logging

from qiskit.providers import BaseProvider
from qiskit.providers.providerutils import filter_backends

from .simulatorerror import QCGPUSimulatorError
from .statevector_simulator import QCGPUStatevectorSimulator
from .qasm_simulator import QCGPUQasmSimulator

logger = logging.getLogger(__name__)

SIMULATORS = [
    QCGPUStatevectorSimulator,
    QCGPUQasmSimulator
]


class QCGPUProvider(BaseProvider):
    """Provider for local QCGPU backends."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self._backends = self._verify_backends()

    def backends(self, name=None, filters=None, **kwargs):
        backends = self._backends.values()

        if name:
            try:
                backends = [backend for backend in backends if backend.name() == name]
            except LookupError:
                pass

        return filter_backends(backends, filters=filters, **kwargs)

    def _verify_backends(self):
        res = OrderedDict()

        for backend_class in SIMULATORS:
            try:
                backend_instance = backend_class(provider=self)
                backend_name = backend_instance.name()
                res[backend_name] = backend_instance
            except QCGPUSimulatorError as err:
                logger.info(err)

        return res

    def _get_backend_instance(self, backend_class):
        try:
            backend_instance = backend_class(provider=self)
        except Exception as err:
            raise QCGPUSimulatorError(
                'Backend {} could not be instantiated: {}'.format(
                    backend_class, err))

        return backend_instance

    def __str__(self):
        return 'QCGPU Provider'

# from qiskit.backends import BaseProvider
# from qiskit.backends.providerutils import filter_backends

# from .statevector_simulator import QCGPUStatevectorSimulator
# from .qasm_simulator import QCGPUQasmSimulator

# import qcgpu

# class QCGPUProvider(BaseProvider):
#     """Provider for local QCGPU backends."""

#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)

#         qcgpu.backend.create_context()

#         self._backends = [QCGPUQasmSimulator(provider=self),
#                           QCGPUStatevectorSimulator(provider=self)]

#     def get_backend(self, name=None, **kwargs):
#         return super().get_backend(name=name, **kwargs)

#     def backends(self, name=None, filters=None, **kwargs):
#         # pylint: disable=arguments-differ
#         if name:
#             kwargs.update({'name': name})

#         return filter_backends(self._backends, filters=filters, **kwargs)

#     def __str__(self):
#         return 'QCGPU Provider'
