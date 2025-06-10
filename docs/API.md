# API Documentation

## CircuitBackend Module

### QuantumGates Class
Core implementation of quantum gates and operations.

#### Single-Qubit Gates
- `H`: Hadamard gate
- `X`: Pauli-X (NOT) gate
- `Y`: Pauli-Y gate
- `Z`: Pauli-Z gate
- `S`: Phase gate
- `T`: π/8 gate

#### Parameterized Gates
- `Rx(theta)`: Rotation around X-axis
- `Ry(theta)`: Rotation around Y-axis
- `Rz(theta)`: Rotation around Z-axis
- `P(phi)`: Phase rotation

#### Multi-Qubit Gates
- `controlled_not(control_idx, target_idx, num_qubits)`: CNOT gate
- `toffoli(control1_idx, control2_idx, target_idx, num_qubits)`: Toffoli (CCNOT) gate
- `swap(qubit1_idx, qubit2_idx, num_qubits)`: SWAP gate

### QuantumCircuit Class
Manages quantum circuits and their simulation.

#### Methods
- `__init__(num_qubits)`: Initialize circuit with specified number of qubits
- `add_gate(gate_type, target_qubits, params=None)`: Add a gate to the circuit
- `calculate_state_vector()`: Calculate the quantum state vector
- `measure_qubit(qubit_idx)`: Perform measurement on specific qubit
- `to_qasm()`: Export circuit to QASM format
- `from_qasm(qasm_str)`: Create circuit from QASM string

### Qubit Class
Represents a single qubit and its state.

#### States
- `STATE_0`: |0⟩ state
- `STATE_1`: |1⟩ state
- `STATE_PLUS`: |+⟩ state
- `STATE_MINUS`: |-⟩ state

## CircuitUI Module

### MainWindow Class
Main application window implementing the circuit editor interface.

#### Features
- Circuit visualization
- Gate drag-and-drop
- State vector display
- Bloch sphere visualization
- QASM code editor

### CircuitScene Class
Handles the graphical representation of quantum circuits.

#### Methods
- `add_gate(gate_type, target_qubits, params, time_step)`: Add gate to circuit
- `remove_gate(time_step, qubit)`: Remove gate from circuit
- `build_circuit()`: Convert visual circuit to QuantumCircuit object

## Usage Examples

### Creating a Bell State
```python
circuit = QuantumCircuit(2)
circuit.add_gate("H", [0])
circuit.add_gate("CNOT", [0, 1])
```

### Quantum Teleportation
```python
circuit = QuantumCircuit(3)
# Create Bell pair
circuit.add_gate("H", [1])
circuit.add_gate("CNOT", [1, 2])
# Entangle with source
circuit.add_gate("CNOT", [0, 1])
circuit.add_gate("H", [0])
# Measure
circuit.add_gate("Measure", [0])
circuit.add_gate("Measure", [1])
```
