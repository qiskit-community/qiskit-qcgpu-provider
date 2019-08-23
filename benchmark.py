import click
import time
import random
import statistics
import csv
import os.path
import math

from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit import QiskitError, execute, Aer

from qiskit_qcgpu_provider import QCGPUProvider

# Implementation of the Quantum Fourier Transform

def construct_circuit(num_qubits):
    q = QuantumRegister(num_qubits)
    c = ClassicalRegister(num_qubits)
    circ = QuantumCircuit(q, c)

    # Quantum Fourier Transform
    for j in range(num_qubits):
        for k in range(j):
            circ.cu1(math.pi / float(2**(j - k)), q[j], q[k])
        circ.h(q[j])
    # circ.measure(q, c)

    return circ


# Benchmarking functions
# qiskit_backend = Aer.get_backend('qasm_simulator')
# qcgpu_backend = QCGPUProvider().get_backend('qasm_simulator')
qiskit_backend = Aer.get_backend('statevector_simulator')
qcgpu_backend = QCGPUProvider().get_backend('statevector_simulator')


def bench_qiskit(qc):
    start = time.time()
    job_sim = execute(qc, qiskit_backend)
    sim_result = job_sim.result()
    return time.time() - start


def bench_qcgpu(qc):
    start = time.time()
    job_sim = execute(qc, qcgpu_backend)
    sim_result = job_sim.result()
    return time.time() - start

# Reporting


def create_csv(filename):
    file_exists = os.path.isfile(filename)
    csvfile = open(filename, 'a')

    headers = ['name', 'num_qubits', 'time']
    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=headers)

    if not file_exists:
        writer.writeheader()  # file doesn't exist yet, write a header

    return writer


def write_csv(writer, data):
    writer.writerow(data)


@click.command()
@click.option('--samples', default=5, help='Number of samples to take for each qubit.')
@click.option('--qubits', default=5, help='How many qubits you want to test for')
@click.option('--out', default='benchmark_data.csv',
              help='Where to store the CSV output of each test')
@click.option(
    '--single',
    default=False,
    help='Only run the benchmark for a single amount of qubits, and print an analysis')
@click.option('--burn', default=True, help='Burn the first few samples for accuracy')
def benchmark(samples, qubits, out, single, burn):
    burn_count = 5 if burn else 0

    if single:
        functions = bench_qcgpu, bench_qiskit
        times = {f.__name__: [] for f in functions}

        names = []
        means = []

        qc = construct_circuit(qubits)

        # Run the benchmarks
        for i in range(samples + burn_count):
            progress = (i) / (samples + burn_count)
            if samples > 1:
                print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress * 100), end="", flush=True)

            func = random.choice(functions)
            t = func(qc)
            
            if i >= burn_count:
                times[func.__name__].append(t)

        print('')

        for name, numbers in times.items():
            print('FUNCTION:', name, 'Used', len(numbers), 'times')
            print('\tMEDIAN', statistics.median(numbers))
            print('\tMEAN  ', statistics.mean(numbers))
            if len(numbers) > 1:
                print('\tSTDEV ', statistics.stdev(numbers))

        return

    functions = bench_qcgpu, bench_qiskit

    writer = create_csv(out)

    for n in range(1, qubits):
        # Progress counter
        progress = (n + 1) / (qubits)
        print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress * 100), end="", flush=True)

        # Construct the circuit
        qc = construct_circuit(n + 1)

        # Run the benchmarks
        for i in range(samples):
            func = random.choice(functions)
            t = func(qc)
            # times[func.__name__].append(t)
            write_csv(writer, {'name': func.__name__, 'num_qubits': n + 1, 'time': t})


if __name__ == '__main__':
    benchmark()
