# User Guide

## Getting Started

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

### Basic Operations

#### Adding Gates
- Drag gates from the palette on the right to the circuit
- Single-qubit gates can be placed directly on qubits
- Multi-qubit gates will prompt for control and target qubits

#### Circuit Manipulation
- Click and drag gates to move them
- Right-click to delete gates
- Use the toolbar to add/remove qubits
- Set initial states using the state selector

#### Visualization
- State vector display shows current quantum state
- Bloch sphere shows single-qubit states
- Probability distribution shows measurement probabilities

### Advanced Features

#### Custom Gates
1. Click "Define Custom Gate" in the toolbar
2. Enter the gate sequence in the editor
3. Name your gate
4. The new gate will appear in the palette

#### QASM Integration
- Export circuits using File > Save Circuit
- Import circuits using File > Load Circuit
- Edit QASM directly in the code editor

### Example Circuits

#### Bell State
1. Add Hadamard (H) gate to first qubit
2. Add CNOT with first qubit as control, second as target

#### Quantum Teleportation
1. Create Bell pair using H + CNOT
2. Entangle with source qubit
3. Apply H to source
4. Measure source and first Bell qubit
5. Apply classical-controlled operations

### Troubleshooting

#### Common Issues
- Gates not aligning: Ensure proper grid snap
- State not updating: Check circuit validity
- QASM import fails: Verify syntax

#### Getting Help
- Use Help > Documentation
- Check the API documentation
- Submit issues on GitHub
