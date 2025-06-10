import unittest
from src.CircuitBackend import QuantumCircuit

class TestQASMIntegration(unittest.TestCase):
    def test_qasm_export_import(self):
        """Test QASM export and import functionality"""
        # Create a test circuit
        original = QuantumCircuit(2)
        original.add_gate("H", [0])
        original.add_gate("CNOT", [0, 1])
        
        # Export to QASM
        qasm_str = original.to_qasm()
        
        # Import from QASM
        imported = QuantumCircuit.from_qasm(qasm_str)
        
        # Compare states
        original_state = original.calculate_state_vector()
        imported_state = imported.calculate_state_vector()
        np.testing.assert_array_almost_equal(original_state, imported_state)

    def test_invalid_qasm(self):
        """Test handling of invalid QASM code"""
        invalid_qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        invalid command;
        """
        with self.assertRaises(ValueError):
            QuantumCircuit.from_qasm(invalid_qasm)

    def test_bell_state_qasm(self):
        """Test creating a Bell state and exporting to QASM"""
        circuit = QuantumCircuit(2)
        circuit.add_gate("H", [0])
        circuit.add_gate("CNOT", [0, 1])
        
        qasm = circuit.to_qasm()
        self.assertIn("h q[0];", qasm)
        self.assertIn("cx q[0],q[1];", qasm)

if __name__ == '__main__':
    unittest.main()
