# Qubox - Toy Quantum Circuit Editor

A graphical quantum circuit editor built with PyQt6 that allows users to design, simulate, and visualize quantum circuits. Perfect for learning quantum computing concepts and experimenting with quantum algorithms.

## Features

- **Interactive Circuit Design**
  - Drag-and-drop interface for quantum gates
  - Support for standard gates (H, X, Y, Z, S, T)
  - Multi-qubit operations (CNOT, Toffoli, SWAP)
  - Custom gate creation and reuse
  
- **Quantum State Visualization**
  - Real-time Bloch sphere visualization
  - State vector representation
  - Probability distribution display
  
- **Circuit Operations**
  - Import/export circuits in QASM format
  - Real-time quantum state simulation
  - Measurement operations
  - Circuit reset functionality

- **Advanced Features**
  - Parameterized quantum gates (Rx, Ry, Rz)
  - Bell state preparation
  - Custom multi-qubit gate sequences
  - Classical register support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ronaldossai/Qubox-Toy-Quantum-circuit-editor.git
cd Qubox-Toy-Quantum-circuit-editor
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

## Usage Examples

1. Creating a Bell State:
```python
# Using the GUI:
1. Add Hadamard gate to qubit 0
2. Add CNOT gate with control on qubit 0 and target on qubit 1

# Using QASM:
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
```

2. Quantum Teleportation Circuit:
```python
# Add required gates for teleportation:
1. Create Bell pair (H + CNOT)
2. Add CNOT between source and first Bell qubit
3. Add Hadamard to source qubit
4. Measure source and first Bell qubit
5. Apply controlled operations based on measurements
```

## Dependencies

- Python 3.x
- PyQt6: GUI framework
- NumPy: Mathematical operations
- Matplotlib: Bloch sphere visualization
- (See requirements.txt for complete list)

## Development

### Running Tests
```bash
python -m unittest discover tests
```

### Project Structure
```
src/
  ├── main.py           # Application entry point
  ├── CircuitUI.py      # GUI components
  ├── CircuitBackend.py # Quantum operations
  ├── BlochSphere.py    # State visualization
  └── HelpBox.py        # Documentation
tests/
  ├── test_quantum_gates.py
  └── test_qasm_integration.py
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass: `python -m unittest discover tests`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

- v1.0.0: Initial release
  - Basic quantum circuit editor
  - Standard gate set
  - QASM import/export
- v1.1.0: Added Bloch sphere visualization
- v1.2.0: Custom gate support
