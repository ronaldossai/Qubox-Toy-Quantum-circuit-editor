import unittest
import numpy as np
from src.CircuitBackend import QuantumGates, QuantumCircuit, Qubit

class TestQuantumGates(unittest.TestCase):
    def test_hadamard_gate(self):
        """Test Hadamard gate operation"""
        h_gate = QuantumGates.H
        # Test H|0⟩ = |+⟩
        result = h_gate @ Qubit.STATE_0
        expected = Qubit.STATE_PLUS
        np.testing.assert_array_almost_equal(result, expected)

    def test_cnot_gate(self):
        """Test CNOT gate operation"""
        circuit = QuantumCircuit(2)
        # Prepare |10⟩ state
        circuit.add_gate("X", [0])
        # Apply CNOT
        circuit.add_gate("CNOT", [0, 1])
        # Should result in |11⟩ state
        state_vector = circuit.calculate_state_vector()
        expected = np.zeros(4)
        expected[3] = 1  # |11⟩ state
        np.testing.assert_array_almost_equal(state_vector, expected)

    def test_toffoli_gate(self):
        """Test Toffoli gate operation"""
        circuit = QuantumCircuit(3)
        # Prepare |110⟩ state
        circuit.add_gate("X", [0])
        circuit.add_gate("X", [1])
        # Apply Toffoli
        circuit.add_gate("Toffoli", [0, 1, 2])
        # Should result in |111⟩ state
        state_vector = circuit.calculate_state_vector()
        expected = np.zeros(8)
        expected[7] = 1  # |111⟩ state
        np.testing.assert_array_almost_equal(state_vector, expected)

if __name__ == '__main__':
    unittest.main()
