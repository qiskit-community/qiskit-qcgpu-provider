from qiskit.wrapper import load_qasm_file
from qiskit import QISKitError, execute, Aer

qc = load_qasm_file("qft_n20.qasm")

sim_backend = Aer.get_backend('statevector_simulator')


# Compile and run the Quantum circuit on a local simulator backend
job_sim = execute(qc, sim_backend)
sim_result = job_sim.result()

# Show the results
print("simulation: ", sim_result)
# print(sim_result.get_counts(qc))