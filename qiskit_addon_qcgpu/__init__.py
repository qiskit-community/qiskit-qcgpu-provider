"""Local QCGPU Backend."""

from .statevector_simulator_qcgpu import StatevectorSimulatorQCGPU

backends_list = { 'statevector_simulator_qcgpu': StatevectorSimulatorQCGPU() }

def get_backend(name):
        return backends_list[name]

def available_backends(filters=None):
    backends = backends_list

    filters = filters or {}
    for key, value in filters.items():
        backends = {name: instance for name, instance in backends.items()
                    if instance.configuration().get(key) == value}

    return list(backends.values())
    
def backends(name=None, **kwargs):
    return list(backends_list.values())