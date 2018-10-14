"""Usage examples for the QCGPU backends"""

from qiskit_qcgpu_provider import QCGPUProvider

Provider = QCGPUProvider()

print(Provider.backends())

print(Provider.backends(name='statevector_simulator'))

backend = Provider.get_backend('statevector_simulator')
print(backend)

# gets the name of the backend.
print(backend.name())

# gets the status of the backend.
print(backend.status())

# returns the provider of the backend
print(backend.provider) 

# gets the configuration of the backend.
print(backend.configuration())

# gets the properties of the backend.
print(backend.properties())