# Reporting Imports
import time
import random
import statistics

from qiskit.wrapper import load_qasm_file
from qiskit import QISKitError, execute, Aer
from qiskit_addon_qcgpu import get_backend

qc = load_qasm_file("qft_n20.qasm")
qiskit_backend = Aer.get_backend('statevector_simulator')
qcgpu_backend = get_backend('statevector_simulator_qcgpu')

def bench_qiskit():
    start = time.time()
    job_sim = execute(qc, qiskit_backend)
    sim_result = job_sim.result()
    return time.time() - start

def bench_qcgpu():
    start = time.time()
    job_sim = execute(qc, backend=qcgpu_backend)
    sim_result = job_sim.result()
    return time.time() - start


# Reporting

functions = bench_qcgpu, bench_qiskit

times = {f.__name__: [] for f in functions}

names = []
means = []

samples = 10
for i in range(samples):  # adjust accordingly so whole thing takes a few sec
    progress = i / samples
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