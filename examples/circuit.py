"""
Example usage of the QCGPU qiskit addon
"""

from qiskit_addon_qcgpu import get_backend
from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from qiskit.wrapper import load_qasm_file

qc = load_qasm_file("bv_n10.qasm")

# qr = QuantumRegister(3)
# qc = QuantumCircuit(qr)
# qc.h(qr[0])
# qc.cx(qr[0], qr[1])
backend = get_backend('statevector_simulator_qcgpu')
result = execute(qc, backend=backend, shots=1).result()
print(result.get_data())