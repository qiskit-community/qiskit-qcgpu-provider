"""
In this example a Bell state is made.
"""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit_qcgpu_provider import QCGPUProvider

Provider = QCGPUProvider()

# Create a Quantum Register with 2 qubits.
q = QuantumRegister(2)
# Create a Quantum Circuit with 2 Qubits
qc = QuantumCircuit(q)

# Add a H gate on qubit 0, putting this qubit in superposition.
qc.h(q[0])
# Add a CX (CNOT) gate on control qubit 0 and target qubit 1, putting
# the qubits in a Bell state.
qc.cx(q[0], q[1])


# See a list of available local simulators
print("QCGPU backends: ", Provider.backends())
backend_sim = Provider.get_backend('statevector_simulator')

# Compile and run the Quantum circuit on a simulator backend
job_sim = execute(qc, backend_sim)
result_sim = job_sim.result()

# Show the results
print("Simulation Results: ", result_sim)
print(result_sim.get_statevector(qc))
