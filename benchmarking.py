import time
import random
import statistics
import math

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit.wrapper import load_qasm_file
from qiskit import QISKitError, execute, Aer
from qiskit_qcgpu_provider import QCGPUProvider

# Implementation of the Quantum Fourier Transform
def cu1(circ, l, a, b):
    circ.u1(l/2, a)
    circ.cx(a, b)
    circ.u1(-l/2, b)
    circ.cx(a, b)
    circ.u1(l/2, b)

def construct_circuit(num_qubits):
    q = QuantumRegister(num_qubits)
    circ = QuantumCircuit(q)

    # Quantum Fourier Transform
    for j in range(num_qubits):
        for k in range(j):
            cu1(circ, math.pi/float(2**(j-k)), q[j], q[k])
        circ.h(q[j])

    return circ

# Benchmarking functions
qc = construct_circuit(20)

qiskit_backend = Aer.get_backend('statevector_simulator')
qcgpu_backend = QCGPUProvider().get_backend('statevector_simulator_qcgpu')

def bench_qiskit():
    start = time.time()
    job_sim = execute(qc, qiskit_backend)
    sim_result = job_sim.result()
    # print(sim_result.get_data())
    return time.time() - start

def bench_qcgpu():
    # start = time.time()
    job_sim = execute(qc, backend=qcgpu_backend)
    sim_result = job_sim.result()
    # print(sim_result.get_data())
    # return time.time() - start
    return sim_result.get_data()['time']


# Reporting
functions = bench_qcgpu, bench_qiskit 

times = {f.__name__: [] for f in functions}

names = []
means = []

samples = 25
for i in range(samples):  # adjust accordingly so whole thing takes a few sec
    progress = (i+1) / (samples)
    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)
    func = random.choice(functions)
    t = func()
    times[func.__name__].append(t)

print('')

for name, numbers in times.items():
    print('FUNCTION:', name, 'Used', len(numbers), 'times')
    print('\tMEDIAN', statistics.median(numbers))
    print('\tMEAN  ', statistics.mean(numbers))
    print('\tSTDEV ', statistics.stdev(numbers))
    means.append(statistics.mean(numbers))
    names.append(name)


