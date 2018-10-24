import click
import time
import random
import statistics
import csv
import os.path
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


qiskit_backend = Aer.get_backend('statevector_simulator')
qcgpu_backend = QCGPUProvider().get_backend('statevector_simulator_qcgpu')

def bench_qiskit(qc):
    start = time.time()
    job_sim = execute(qc, qiskit_backend)
    sim_result = job_sim.result()
    return time.time() - start

def bench_qcgpu(qc):
    job_sim = execute(qc, backend=qcgpu_backend)
    sim_result = job_sim.result()
    return sim_result.get_data()['time']


# Reporting
def create_csv(filename):
    file_exists = os.path.isfile(filename)
    csvfile = open(filename, 'a')
   
    headers = ['name', 'num_qubits', 'time']
    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

    if not file_exists:
        writer.writeheader()  # file doesn't exist yet, write a header

    return writer

def write_csv(writer, data):
    writer.writerow(data)



@click.command()
@click.option('--samples', default=5, help='Number of samples to take for each qubit.')
@click.option('--qubits', default=5, help='How many qubits you want to test for')
@click.option('--out', default='benchmark_data.csv', help='Where to store the CSV output of each test')
@click.option('--single', default=False, help='Only run the benchmark for a single amount of qubits, and print an analysis')
def benchmark(samples, qubits, out, single):
    if single:
        functions = bench_qcgpu, bench_qiskit 
        times = {f.__name__: [] for f in functions}

        names = []
        means = []

        qc = construct_circuit(qubits)
        # Run the benchmarks
        for i in range(samples):
            progress = (i) / (samples)
            print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

            func = random.choice(functions)
            t = func(qc)
            times[func.__name__].append(t)

        print('')

        for name, numbers in times.items():
            print('FUNCTION:', name, 'Used', len(numbers), 'times')
            print('\tMEDIAN', statistics.median(numbers))
            print('\tMEAN  ', statistics.mean(numbers))
            print('\tSTDEV ', statistics.stdev(numbers))

        return

    functions = bench_qcgpu, bench_qiskit 
    # times = {f.__name__: [] for f in functions}
    writer = create_csv(out)

    for n in range(qubits):
        # Progress counter
        progress = (n+1) / (qubits)
        print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)

        # Construct the circuit
        qc = construct_circuit(n+1)

        # Run the benchmarks
        for i in range(samples):
            func = random.choice(functions)
            t = func(qc)
            # times[func.__name__].append(t)
            write_csv(writer, {'name': func.__name__, 'num_qubits': n+1, 'time': t})

if __name__ == '__main__':
    benchmark()