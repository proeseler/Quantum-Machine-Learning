# Installation: pip install qiskit

import numpy as np
import math
from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from pgmpy.models import BayesianNetwork
from qiskit.circuit import QuantumRegister
from qiskit.circuit.library import GroverOperator

class QBayesian:

    # Discrete quantum Bayesian network
    def __init__(self, bNetwork: BayesianNetwork = None, circuit: QuantumCircuit = None):
        if bNetwork is None and circuit is None:
            raise ValueError("One Bayesian network or quantum circuit must be provided")
        self.samples = {}
        self.tValidS = 0
        if circuit is not None:
            self.circuit = circuit
        else:
            # Represent any discrete Bayesian network with any number of nodes.
            self.network = bNetwork
            self.initialize()

    def initialize(self):
        """Initializes the circuit to a specific state."""
        # Quantum register
        qr_list = list()
        for node_key, node_card in self.network.cardinalities:  # returns the number of states for each node (variable)
            m_i = math.ceil(math.log2(node_card))
            qr_i = QuantumRegister(m_i, name=node_key)
            qr_list.append(qr_i)

        # Quantum circuit


    def rejectionSampling(self, evidence):

        def getSe(ctrls):
            """
            ctrls: control qubits are the evidence var
            """
            opSe = QuantumCircuit(self.circuit.num_qubits)
            query_var = set(self.circuit.qubits)-set(ctrls)
            for q in query_var:
                # multi control z gate
                opSe.h(q)
                opSe.mcx(ctrls, q)
                opSe.h(q)
                # x gate
                opSe.x(q)
                # multi control z gate
                opSe.h(q)
                opSe.mcx(ctrls, q)
                opSe.h(q)
                # x gate
                opSe.x(q)
            return opSe

        def run_circuit(circuit, shots=10_000):
            """
            Run the provided quantum circuit on the Aer simulator backend.

            Parameters:
            - circuit: The quantum circuit to be executed.
            - shots (default=10,000): The number of times the circuit is executed.

            Returns:
            - counts: A dictionary with the counts of each quantum state result.
            """

            # Get the Aer simulator backend
            simulator_backend = Aer.get_backend('aer_simulator')

            # Transpile the circuit for the given backend
            transpiled_circuit = transpile(circuit, simulator_backend)

            # Run the transpiled circuit on the simulator
            job = simulator_backend.run(transpiled_circuit, shots=shots)
            result = job.result()

            # Get the counts of quantum state results
            counts = result.get_counts(transpiled_circuit)

            return counts

        opSe = getSe(query)
        # Grover
        opG = GroverOperator(opSe, self.circuit)
        # Circuit
        qregs = self.circuit.qregs
        qc = QuantumCircuit(*qregs)
        qc.append(self.circuit, qregs)
        qc.append(opG, qregs)

        qc.measure_all()
        # Run circuit
        counts = run_circuit(qc)
        # Calc inference
        self.samples = {}
        self.tValidS = 0
        # TODO check if evidence and query build all vars - YES
        # Assume key is bin and e_key is the qubits number
        for key, val in counts.items():
            accept = True
            for e_key, e_val in evidence.items():
                if key[e_key] != e_val:
                    accept = False
                    break
            if accept:
                self.samples[key] = val
                self.tValidS += val
        return self.samples


    def inference(self, query, evidence: None):
        if evidence is not None:
            self.rejectionSampling(query, evidence)
        q_count = 0
        for sample_key, sample_val in self.samples.items():
            add = True
            for q_key, q_val in query.items():
                if sample_key[q_key]!=q_val:
                    add=False
                    break
            if add:
                q_count += sample_val
        return q_count/self.tValidS


    def measure(self):
        """Adds a measurement operation to all qubits."""
        self.circuit.measure_all()

    def simulate(self):
        """Simulates the circuit and returns the probability distribution."""
        simulator = AerSimulator()
        compiled_circuit = transpile(self.circuit, simulator)
        result = simulator.run(compiled_circuit).result()
        counts = result.get_counts(self.circuit)
        return counts

    def visualize(self, counts):
        """Visualizes the result."""
        return plot_histogram(counts)


# Example usage:


# Define a 2-qubit system
qbi = QuantumBayesianInference(2)

# Initialize with some state (for simplicity, the |00> state is used)
initial_state = [1, 0, 0, 0]  # |00> state for 2 qubits
qbi.initialize(initial_state)

# Apply some operations (Hadamard gate on first qubit and CNOT gate)
qbi.apply_gate('H', 0)
qbi.apply_gate('CX', 0, 1)

# Measure the qubits
qbi.measure()

# Simulate and visualize the circuit
counts = qbi.simulate()
qbi.visualize(counts)
