import numpy as np
from typing import List, Dict, Tuple, Optional, Union

# Represents a single qubit in a specific state.
class Qubit:
    
    # Standard basis states
    STATE_0 = np.array([1, 0], dtype=complex)
    STATE_1 = np.array([0, 1], dtype=complex)
    # Uniform superposition with a poistive phase
    STATE_PLUS = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)  
    # Uniform superposition with negative phase
    STATE_MINUS = np.array([1/np.sqrt(2), -1/np.sqrt(2)], dtype=complex)  
   
    # Initialize a qubit in a specified state.
    def __init__(self, initial_state="0"):
        if initial_state == "0":
            self.state = self.STATE_0.copy()
        elif initial_state == "1":
            self.state = self.STATE_1.copy()
        elif initial_state == "+":
            self.state = self.STATE_PLUS.copy()
        elif initial_state == "-":
            self.state = self.STATE_MINUS.copy()
        else:
            raise ValueError("Invalid initial state. Use '0', '1', '+', or '-'.")

# Collection of quantum gates as numpy matrices.
class QuantumGates: 
    
    # Single-qubit gates
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)  # Pauli-X / NOT
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli-Y
    Z = np.array([[1, 0], [0, -1]], dtype=complex)  # Pauli-Z
    H = np.array([[1/np.sqrt(2), 1/np.sqrt(2)], 
                  [1/np.sqrt(2), -1/np.sqrt(2)]], dtype=complex)  # Hadamard
    S = np.array([[1, 0], [0, 1j]], dtype=complex)  # Phase gate
    T = np.array([[1, 0], [0, np.exp(1j*np.pi/4)]], dtype=complex)  # T gate
    
    @staticmethod
    def Rx(theta: float) -> np.ndarray:
        # Rotation around X-axis
        return np.array([
            [np.cos(theta/2), -1j*np.sin(theta/2)],
            [-1j*np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def Ry(theta: float) -> np.ndarray:
        # Rotation around Y-axis
        return np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def Rz(theta: float) -> np.ndarray:
        # Rotation around Z-axis
        return np.array([
            [np.exp(-1j*theta/2), 0],
            [0, np.exp(1j*theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def P(phi: float) -> np.ndarray:
        # Phase gate with arbitrary angle
        return np.array([
            [1, 0],
            [0, np.exp(1j*phi)]
        ], dtype=complex)
    
    @staticmethod
    def swap(qubit1_idx: int, qubit2_idx: int, num_qubits: int) -> np.ndarray:
        # Create a SWAP gate matrix for the specified qubits
        dim = 2 ** num_qubits
        swap = np.zeros((dim, dim), dtype=complex)
        
        # For each computational basis state
        for i in range(dim):
            # Convert to binary representation
            binary = list(format(i, f'0{num_qubits}b'))
            
            # Swap the bits at the specified positions
            binary[qubit1_idx], binary[qubit2_idx] = binary[qubit2_idx], binary[qubit1_idx]
            target_state = int(''.join(binary), 2)
            
            # Set the matrix element
            swap[target_state, i] = 1
        
        return swap
    
    # Multi-qubit gates are implemented as methods
    @staticmethod
    def controlled_not(control_idx, target_idx, num_qubits):
        # Create a CNOT matrix for specified control and target qubits.
        dim = 2 ** num_qubits
        cnot = np.identity(dim, dtype=complex)
        
        # For each computational basis state
        for i in range(dim):
            # Convert to binary representation
            binary = format(i, f'0{num_qubits}b')
            
            # Check if control qubit is 1
            if binary[control_idx] == '1':
                # Find the corresponding state with target bit flipped
                target_binary = list(binary)
                target_binary[target_idx] = '1' if binary[target_idx] == '0' else '0'
                target_state = int(''.join(target_binary), 2)
                
                # Swap amplitudes
                cnot[i, i] = 0
                cnot[target_state, target_state] = 0
                cnot[i, target_state] = 1
                cnot[target_state, i] = 1
        
        return cnot
    
    @staticmethod
    def toffoli(control1_idx, control2_idx, target_idx, num_qubits):
        # Create a Toffoli (CCNOT) matrix for the specified control and target qubits.
        dim = 2 ** num_qubits
        toffoli = np.identity(dim, dtype=complex)
        
        # For each computational basis state
        for i in range(dim):
            # Convert to binary representation
            binary = format(i, f'0{num_qubits}b')
            
            # Check if both control qubits are 1
            if binary[control1_idx] == '1' and binary[control2_idx] == '1':
                # Find the corresponding state with target bit flipped
                target_binary = list(binary)
                target_binary[target_idx] = '1' if binary[target_idx] == '0' else '0'
                target_state = int(''.join(target_binary), 2)
                
                # Swap amplitudes
                toffoli[i, i] = 0
                toffoli[target_state, target_state] = 0
                toffoli[i, target_state] = 1
                toffoli[target_state, i] = 1
        
        return toffoli

class QuantumCircuit:
    # Represents a quantum circuit with multiple qubits and gates.
    
    def __init__(self, num_qubits: int):
        # Initialize a quantum circuit with specified number of qubits.
        self.num_qubits = num_qubits
        self.qubits = [Qubit("0") for _ in range(num_qubits)]
        self.gates = []  # List of (gate_type, target_qubits, params) tuples
        self.custom_gates = {}  # Dictionary of custom gates
        self.measurements = {}  # Dictionary to store measurement results
        self.classical_registers = {}  # Dictionary to store classical register values
    
    def set_initial_state(self, qubit_idx: int, state: str):
        # Set the initial state of a specific qubit.
        if qubit_idx < 0 or qubit_idx >= self.num_qubits:
            raise ValueError(f"Invalid qubit index: {qubit_idx}")
        self.qubits[qubit_idx] = Qubit(state)
    
    def add_gate(self, gate_type: str, target_qubits: List[int], params: Optional[List[float]] = None):
        # Add a gate to the circuit.
        # Args:
        # gate_type: Type of the gate ("H", "X", "Y", "Z", "S", "T", "Rx", "Ry", "Rz", "P", "SWAP", "CNOT", "Toffoli", "Measure", "Bell", "Reset")
        # target_qubits: List of target qubit indices
        # params: Optional parameters for parameterized gates (Rx, Ry, Rz, P)
        
        # Validate gate type and qubit indices
        if gate_type not in ["H", "T", "S", "X", "Y", "Z", "Rx", "Ry", "Rz", "P", "SWAP", "CNOT", "Toffoli", "Measure", "Bell", "Reset"]:
            raise ValueError(f"Unsupported gate type: {gate_type}")
        
        for idx in target_qubits:
            if idx < 0 or idx >= self.num_qubits:
                raise ValueError(f"Invalid qubit index: {idx}")
        
        # Check proper number of target qubits for each gate type
        if gate_type in ["H", "T", "S", "X", "Y", "Z", "Measure", "Reset"] and len(target_qubits) != 1:
            raise ValueError(f"{gate_type} gate requires exactly 1 target qubit")
        elif gate_type in ["Rx", "Ry", "Rz", "P"] and len(target_qubits) != 1:
            raise ValueError(f"{gate_type} gate requires exactly 1 target qubit")
        elif gate_type in ["SWAP", "CNOT", "Bell"] and len(target_qubits) != 2:
            raise ValueError(f"{gate_type} gate requires exactly 2 qubits")
        elif gate_type == "Toffoli" and len(target_qubits) != 3:
            raise ValueError("Toffoli gate requires exactly 3 qubits (control1, control2, target)")
        
        # Check parameters for parameterized gates
        if gate_type in ["Rx", "Ry", "Rz", "P"]:
            if not params or len(params) != 1:
                raise ValueError(f"{gate_type} gate requires exactly 1 parameter")
        
        self.gates.append((gate_type, target_qubits, params))
    
    def define_custom_gate(self, name: str, gate_sequence: List[Tuple[str, List[int], Optional[List[float]]]]):
        # Define a custom gate as a sequence of primitive gates.
        # Args:
        #    name: Name of the custom gate
        #    gate_sequence: List of tuples, where each tuple is (gate_type, target_qubits, params)
        self.custom_gates[name] = gate_sequence
    
    def add_custom_gate(self, name: str, target_qubits: List[int]):
        # Add a custom gate to the circuit.
        # Args:
        #    name: Name of the custom gate
        #    target_qubits: List of target qubit indices where the custom gate will be applied
        #
        if name not in self.custom_gates:
            raise ValueError(f"Custom gate '{name}' is not defined")
        
        # Store the custom gate application in the gates list
        self.gates.append((name, target_qubits, None))
    
    def calculate_state_vector(self) -> np.ndarray:
        # Initialize the state vector as a tensor product of all qubits
        # Note: We use right-to-left ordering for tensor products
        state = self.qubits[-1].state
        for i in range(self.num_qubits - 2, -1, -1):
            state = np.kron(self.qubits[i].state, state)
        
        # Apply each gate in sequence
        for gate_type, target_qubits, params in self.gates:
            if gate_type in self.custom_gates:
                # Handle custom gate by applying its sequence
                for sub_gate_type, relative_targets, sub_params in self.custom_gates[gate_type]: # Use sub_params
                    # Map relative qubit indices to actual indices
                    actual_targets = [target_qubits[i] for i in relative_targets]
                    
                    # Apply the constituent gate
                    if sub_gate_type in ["H", "T", "S", "X", "Y", "Z"]:
                        gate_matrix = self._apply_single_qubit_gate(getattr(QuantumGates, sub_gate_type), actual_targets[0])
                    elif sub_gate_type in ["Rx", "Ry", "Rz", "P"]:
                        if not sub_params or len(sub_params) != 1:
                             raise ValueError(f"Missing or incorrect parameters for {sub_gate_type} within custom gate '{gate_type}'")
                        if sub_gate_type == "Rx":
                            gate_matrix = self._apply_single_qubit_gate(QuantumGates.Rx(sub_params[0]), actual_targets[0]) # Use sub_params
                        elif sub_gate_type == "Ry":
                            gate_matrix = self._apply_single_qubit_gate(QuantumGates.Ry(sub_params[0]), actual_targets[0]) # Use sub_params
                        elif sub_gate_type == "Rz":
                            gate_matrix = self._apply_single_qubit_gate(QuantumGates.Rz(sub_params[0]), actual_targets[0]) # Use sub_params
                        else:  # P gate
                            gate_matrix = self._apply_single_qubit_gate(QuantumGates.P(sub_params[0]), actual_targets[0]) # Use sub_params
                    elif sub_gate_type == "CNOT":
                        gate_matrix = QuantumGates.controlled_not(actual_targets[0], actual_targets[1], self.num_qubits)
                    elif sub_gate_type == "SWAP":
                        gate_matrix = QuantumGates.swap(actual_targets[0], actual_targets[1], self.num_qubits)
                    elif sub_gate_type == "Toffoli":
                        gate_matrix = QuantumGates.toffoli(actual_targets[0], actual_targets[1], actual_targets[2], self.num_qubits)
                    
                    state = gate_matrix @ state
                continue
            
            # Handle standard gates as before
            if gate_type == "H":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.H, target_qubits[0])
            elif gate_type == "T":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.T, target_qubits[0])
            elif gate_type == "S":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.S, target_qubits[0])
            elif gate_type == "X":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.X, target_qubits[0])
            elif gate_type == "Y":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.Y, target_qubits[0])
            elif gate_type == "Z":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.Z, target_qubits[0])
            elif gate_type == "Rx":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.Rx(params[0]), target_qubits[0])
            elif gate_type == "Ry":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.Ry(params[0]), target_qubits[0])
            elif gate_type == "Rz":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.Rz(params[0]), target_qubits[0])
            elif gate_type == "P":
                gate_matrix = self._apply_single_qubit_gate(QuantumGates.P(params[0]), target_qubits[0])
            elif gate_type == "SWAP":
                gate_matrix = QuantumGates.swap(target_qubits[0], target_qubits[1], self.num_qubits)
            elif gate_type == "CNOT":
                gate_matrix = QuantumGates.controlled_not(target_qubits[0], target_qubits[1], self.num_qubits)
            elif gate_type == "Toffoli":
                gate_matrix = QuantumGates.toffoli(target_qubits[0], target_qubits[1], target_qubits[2], self.num_qubits)
            elif gate_type == "Bell":
                # Create Bell state between two qubits
                # First apply Hadamard to control qubit
                h_matrix = self._apply_single_qubit_gate(QuantumGates.H, target_qubits[0])
                state = h_matrix @ state
                # Then apply CNOT
                cnot_matrix = QuantumGates.controlled_not(target_qubits[0], target_qubits[1], self.num_qubits)
                gate_matrix = cnot_matrix
            elif gate_type == "Measure":
                # Measurement is handled separately after state vector calculation
                continue
            
            state = gate_matrix @ state
        
        return state
    
    def _apply_single_qubit_gate(self, gate_matrix: np.ndarray, target_qubit: int) -> np.ndarray:
        # Start with identity matrices for all qubits
        # We use right-to-left ordering for tensor products
        matrices = [QuantumGates.I] * self.num_qubits
        
        # Replace the target qubit's matrix with the gate matrix
        # Convert target_qubit to right-to-left ordering
        matrices[self.num_qubits - 1 - target_qubit] = gate_matrix
        
        # Calculate the tensor product of all matrices
        # Use right-to-left ordering
        result = matrices[-1]
        for i in range(self.num_qubits - 2, -1, -1):
            result = np.kron(matrices[i], result)
        
        return result
    
    def get_state_vector_representation(self) -> str:
        # Get a string representation of the state vector with improved formatting. 
        state = self.calculate_state_vector()
        result = []
        
        # Create all possible basis states
        for i in range(2**self.num_qubits):
            binary = format(i, f'0{self.num_qubits}b')
            amplitude = state[i]
            
            # Skip terms with zero amplitude
            if abs(amplitude) < 1e-10:
                continue
            
            # Format the amplitude with improved precision and readability
            if abs(amplitude.real) < 1e-10 and abs(amplitude.imag) < 1e-10:
                continue
            elif abs(amplitude.real) < 1e-10:
                coef = f"{amplitude.imag:.4f}i"
            elif abs(amplitude.imag) < 1e-10:
                coef = f"{amplitude.real:.4f}"
            else:
                # Handle both real and imaginary parts
                real_part = f"{amplitude.real:.4f}"
                imag_part = f"{amplitude.imag:.4f}i"
                
                # Format the complex number with proper signs
                if amplitude.imag > 0:
                    coef = f"({real_part} + {imag_part})"
                else:
                    coef = f"({real_part} - {abs(amplitude.imag):.4f}i)"
            
            # Add probability information
            prob = abs(amplitude)**2
            result.append(f"{coef}|{binary}⟩ ({prob:.4f})")
        
        return " + ".join(result) if result else "0"
    
    def get_probability_distribution(self) -> Dict[str, float]:
        # Get the probability distribution over basis states.
        state = self.calculate_state_vector()
        probs = {}
        
        for i in range(2**self.num_qubits):
            binary = format(i, f'0{self.num_qubits}b')
            prob = abs(state[i])**2
            if prob > 1e-10:  # Only include non-zero probabilities
                probs[binary] = prob
        
        return probs
    
    def measure_qubit(self, qubit_idx: int) -> str:
        # Measure a specific qubit and return the result ('0' or '1').
        if qubit_idx < 0 or qubit_idx >= self.num_qubits:
            raise ValueError(f"Invalid qubit index: {qubit_idx}")
        
        state_vector = self.calculate_state_vector()
        probabilities = np.zeros(2)
        
        # Calculate probabilities for 0 and 1
        for i in range(len(state_vector)):
            binary = format(i, f'0{self.num_qubits}b')
            bit = int(binary[qubit_idx])
            probabilities[bit] += abs(state_vector[i])**2
        
        # Normalize probabilities
        probabilities = probabilities / np.sum(probabilities)
        
        # Random measurement based on probabilities
        result = np.random.choice(['0', '1'], p=probabilities)
        self.measurements[qubit_idx] = result
        
        return result
    
    def get_measurement_results(self) -> Dict[int, str]:
        # Get all measurement results.
        return self.measurements.copy()
    
    def to_qasm(self) -> str:
        qasm = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n\n"
        qasm += f"qreg q[{self.num_qubits}];\n"
        qasm += f"creg c[{self.num_qubits}];\n"  # Classical register for measurements
        
        # Initialize qubits
        for i, qubit in enumerate(self.qubits):
            if np.array_equal(qubit.state, Qubit.STATE_1):
                qasm += f"x q[{i}];\n"
            elif np.array_equal(qubit.state, Qubit.STATE_PLUS):
                qasm += f"h q[{i}];\n"
        
        # Add gates
        for gate_type, target_qubits, params in self.gates:
            if gate_type == "H":
                qasm += f"h q[{target_qubits[0]}];\n"
            elif gate_type == "T":
                qasm += f"t q[{target_qubits[0]}];\n"
            elif gate_type == "S":
                qasm += f"s q[{target_qubits[0]}];\n"
            elif gate_type == "X":
                qasm += f"x q[{target_qubits[0]}];\n"
            elif gate_type == "Y":
                qasm += f"y q[{target_qubits[0]}];\n"
            elif gate_type == "Z":
                qasm += f"z q[{target_qubits[0]}];\n"
            elif gate_type == "Rx":
                qasm += f"rx({params[0]}) q[{target_qubits[0]}];\n"
            elif gate_type == "Ry":
                qasm += f"ry({params[0]}) q[{target_qubits[0]}];\n"
            elif gate_type == "Rz":
                qasm += f"rz({params[0]}) q[{target_qubits[0]}];\n"
            elif gate_type == "P":
                qasm += f"p({params[0]}) q[{target_qubits[0]}];\n"
            elif gate_type == "SWAP":
                qasm += f"swap q[{target_qubits[0]}],q[{target_qubits[1]}];\n"
            elif gate_type == "CNOT":
                qasm += f"cx q[{target_qubits[0]}],q[{target_qubits[1]}];\n"
            elif gate_type == "Toffoli":
                qasm += f"ccx q[{target_qubits[0]}],q[{target_qubits[1]}],q[{target_qubits[2]}];\n"
            elif gate_type == "Bell":
                qasm += f"h q[{target_qubits[0]}];\n"
                qasm += f"cx q[{target_qubits[0]}],q[{target_qubits[1]}];\n"
            elif gate_type == "Measure":
                qasm += f"measure q[{target_qubits[0]}] -> c[{target_qubits[0]}];\n"
            elif gate_type == "Reset":
                qasm += f"reset q[{target_qubits[0]}];\n"
        
        return qasm
    
    @classmethod
    def from_qasm(cls, qasm_str: str) -> 'QuantumCircuit':
        # Create a quantum circuit from OpenQASM 2.0 code with enhanced parsing.
        lines = qasm_str.strip().split('\n')
        circuit = None
        current_custom_gate = None
        current_custom_sequence = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines, comments, and includes
            if not line or line.startswith('//') or line.startswith('include') or line.startswith('OPENQASM'):
                continue
            
            # Parse quantum register declaration
            if line.startswith('qreg'):
                match = line.split('[')[1].split(']')[0]
                num_qubits = int(match)
                circuit = cls(num_qubits)
            
            # Parse classical register declaration
            elif line.startswith('creg'):
                match = line.split('[')[1].split(']')[0]
                num_bits = int(match)
                circuit.classical_registers = {i: '0' for i in range(num_bits)}
            
            # Parse custom gate definition
            elif line.startswith('gate'):
                if circuit is None:
                    raise ValueError("Circuit must be defined before custom gates")
                parts = line.split()
                current_custom_gate = parts[1]
                # Extract qubit parameters
                qubit_params = parts[2:-1]  # Everything between gate name and {
                current_custom_sequence = []
            
            # Parse custom gate body
            elif current_custom_gate is not None:
                if line == '}':
                    circuit.define_custom_gate(current_custom_gate, current_custom_sequence)
                    current_custom_gate = None
                    current_custom_sequence = []
                else:
                    # Parse gate instruction in custom gate
                    gate_parts = line.split()
                    if len(gate_parts) >= 2:
                        gate_type = gate_parts[0]
                        qubits = [int(q.strip('q[]')) for q in gate_parts[1].split(',')]
                        current_custom_sequence.append((gate_type, qubits))
            
            # Parse gates
            elif circuit is not None:
                if line.startswith('barrier'):
                    continue  # Skip barrier instructions
                elif line.startswith('if'):
                    # Parse conditional operations
                    parts = line.split('==')
                    if len(parts) == 2:
                        condition = parts[0].split()[1]  # Get the condition
                        target = int(parts[1].split('[')[1].split(']')[0])
                        # Store conditional information with the next gate
                        circuit.gates.append(('CONDITIONAL', [target], condition))
                elif line.startswith('h '):
                    target = int(line.split('[')[1].split(']')[0])
                    circuit.add_gate("H", [target])
                elif line.startswith('t '):
                    target = int(line.split('[')[1].split(']')[0])
                    circuit.add_gate("T", [target])
                elif line.startswith('s '):
                    target = int(line.split('[')[1].split(']')[0])
                    circuit.add_gate("S", [target])
                elif line.startswith('x '):
                    target = int(line.split('[')[1].split(']')[0])
                    circuit.add_gate("X", [target])
                elif line.startswith('y '):
                    target = int(line.split('[')[1].split(']')[0])
                    circuit.add_gate("Y", [target])
                elif line.startswith('z '):
                    target = int(line.split('[')[1].split(']')[0])
                    circuit.add_gate("Z", [target])
                elif line.startswith('rx('):
                    # Format is: rx(parameter) q[target];
                    param_end = line.find(')')
                    param = float(line[3:param_end])  # Extract parameter from inside parentheses
                    target = int(line.split('[')[1].split(']')[0])  # Extract target qubit
                    circuit.add_gate("Rx", [target], [param])
                elif line.startswith('ry('):
                    # Format is: ry(parameter) q[target];
                    param_end = line.find(')')
                    param = float(line[3:param_end])  # Extract parameter from inside parentheses
                    target = int(line.split('[')[1].split(']')[0])  # Extract target qubit
                    circuit.add_gate("Ry", [target], [param])
                elif line.startswith('rz('):
                    # Format is: rz(parameter) q[target];
                    param_end = line.find(')')
                    param = float(line[3:param_end])  # Extract parameter from inside parentheses
                    target = int(line.split('[')[1].split(']')[0])  # Extract target qubit
                    circuit.add_gate("Rz", [target], [param])
                elif line.startswith('p('):
                    # Format is: p(parameter) q[target];
                    param_end = line.find(')')
                    param = float(line[2:param_end])  # Extract parameter from inside parentheses
                    target = int(line.split('[')[1].split(']')[0])  # Extract target qubit
                    circuit.add_gate("P", [target], [param])
                elif line.startswith('cx '):
                    parts = line.split(',')
                    control = int(parts[0].split('[')[1].split(']')[0])
                    target = int(parts[1].split('[')[1].split(']')[0])
                    circuit.add_gate("CNOT", [control, target])
                elif line.startswith('ccx '):
                    parts = line.split(',')
                    control1 = int(parts[0].split('[')[1].split(']')[0])
                    control2 = int(parts[1].split('[')[1].split(']')[0])
                    target = int(parts[2].split('[')[1].split(']')[0])
                    circuit.add_gate("Toffoli", [control1, control2, target])
                elif line.startswith('measure'):
                    parts = line.split('->')
                    target = int(parts[0].split('[')[1].split(']')[0])
                    classical = int(parts[1].split('[')[1].split(']')[0])
                    circuit.add_gate("Measure", [target])
                    circuit.classical_registers[classical] = circuit.measure_qubit(target)
        
        return circuit