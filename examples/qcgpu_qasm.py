
"""
In this example a Bell state is made.
"""

from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute
from qiskit_qcgpu_provider import QCGPUProvider

q = QuantumRegister(2)
c = ClassicalRegister(2)
qc = QuantumCircuit(q, c)

qc.h(q)
qc.cx(q[0], q[1])
qc.reset(q[0])
qc.measure(q, c)
qc.h(q[0])
qc.measure(q[0], c[0])


backend = QCGPUProvider().get_backend('qasm_simulator')
job_sim = execute(qc, backend, shots=10)
sim_result = job_sim.result()

print(sim_result.get_counts(qc))