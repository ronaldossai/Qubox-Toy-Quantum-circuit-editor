import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from mpl_toolkits.mplot3d import Axes3D
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog, QLabel, QComboBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Calculate Bloch sphere coordinates from qubit state
def qubit_to_bloch(state_vector):
    # Convert a 2D state vector to Bloch sphere coordinates.
    # Ensure state is normalized
    norm = np.sqrt(np.abs(state_vector[0])**2 + np.abs(state_vector[1])**2)
    if norm < 1e-10:
        return [0, 0, 0]  # Return center of sphere for zero vector
    
    state_vector = state_vector / norm
    
    # Extract components
    alpha = state_vector[0]
    beta = state_vector[1]
    
    # Calculate Bloch sphere coordinates
    # x = 2 * Re(alpha* * beta)
    # y = 2 * Im(alpha* * beta)
    # z = |alpha|^2 - |beta|^2
    x = 2 * (alpha.conjugate() * beta).real
    y = 2 * (alpha.conjugate() * beta).imag
    z = (np.abs(alpha)**2 - np.abs(beta)**2)
    
    return [x, y, z]

# Visualize Bloch sphere
def create_bloch_sphere(ax, vectors=None, labels=None, title="Bloch Sphere"):
    # Create a Bloch sphere visualization with optional state vectors.
    # Set up the axes
    ax.clear()
    ax.set_aspect('equal')
    ax.set_title(title)
    
    # Draw the Bloch sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Surface of the sphere
    ax.plot_surface(x, y, z, color='lightgray', alpha=0.1)
    
    # Wireframe for better visibility
    ax.plot_wireframe(x, y, z, color='gray', alpha=0.3, rstride=10, cstride=10)
    
    # Draw the axes
    ax.plot([-1.5, 1.5], [0, 0], [0, 0], 'k--', alpha=0.5, lw=1)  # x-axis
    ax.plot([0, 0], [-1.5, 1.5], [0, 0], 'k--', alpha=0.5, lw=1)  # y-axis
    ax.plot([0, 0], [0, 0], [-1.5, 1.5], 'k--', alpha=0.5, lw=1)  # z-axis
    
    # Label the axes
    ax.text(1.7, 0, 0, "X", fontsize=10)
    ax.text(0, 1.7, 0, "Y", fontsize=10)
    ax.text(0, 0, 1.7, "Z", fontsize=10)
    
    # Add |0⟩ and |1⟩ state labels
    ax.text(0, 0, 1.5, "|0⟩", fontsize=10)
    ax.text(0, 0, -1.7, "|1⟩", fontsize=10)
    
    # Add |+⟩ and |-⟩ state labels
    ax.text(1.3, 0, 0, "|+⟩", fontsize=10)
    ax.text(-1.7, 0, 0, "|-⟩", fontsize=10)
    
    # Draw the state vectors if provided
    colors_list = ['r', 'g', 'b', 'c', 'm', 'y']
    
    if vectors is not None:
        for i, vector in enumerate(vectors):
            if vector is not None:
                x, y, z = vector
                color = colors_list[i % len(colors_list)]
                # Draw the vector
                ax.quiver(0, 0, 0, x, y, z, color=color, lw=2, arrow_length_ratio=0.1)
                
                # Add a label if provided
                if labels and i < len(labels):
                    ax.text(x*1.1, y*1.1, z*1.1, labels[i], color=color, fontsize=10)
    
    # Set limits to contain the sphere
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])

# BlochSphereWidget to display single or multiple qubits
class BlochSphereWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        # Create layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create figure and canvas
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Initialize 3D axes for Bloch sphere
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Create default Bloch sphere
        create_bloch_sphere(self.ax)
        self.canvas.draw()
    
    def update_from_circuit(self, circuit, selected_qubits=None):
        # Update the Bloch sphere from a quantum circuit.
        if not circuit:
            return
        
        # Calculate full state vector
        state_vector = circuit.calculate_state_vector()
        
        # If no specific qubits are selected, show qubit 0
        if selected_qubits is None or len(selected_qubits) == 0:
            selected_qubits = [0]
        
        # Extract individual qubit states from the full state vector
        vectors = []
        labels = []
        
        for qubit_idx in selected_qubits:
            # Get the reduced density matrix for this qubit
            reduced_state = self.get_reduced_state(state_vector, qubit_idx, circuit.num_qubits)
            
            # Convert to Bloch vector
            bloch_vector = qubit_to_bloch(reduced_state)
            vectors.append(bloch_vector)
            labels.append(f"q{qubit_idx}")
        
        # Clear and redraw
        title = "Bloch Sphere" if len(selected_qubits) == 1 else "Multiple Qubits"
        create_bloch_sphere(self.ax, vectors, labels, title)
        self.canvas.draw()
    
    def get_reduced_state(self, state_vector, target_qubit, num_qubits):
        # Get the reduced state of a single qubit from the full state vector.
        # Initialize reduced density matrix
        rho = np.zeros((2, 2), dtype=complex)
        
        # Loop through all basis states
        for i in range(2**num_qubits):
            for j in range(2**num_qubits):
                # Convert to binary
                i_binary = format(i, f'0{num_qubits}b')
                j_binary = format(j, f'0{num_qubits}b')
                
                # Check if the qubits match except for the target qubit
                match = True
                for k in range(num_qubits):
                    if k != target_qubit and i_binary[k] != j_binary[k]:
                        match = False
                        break
                
                if match:
                    # Extract the bit values for the target qubit
                    i_bit = int(i_binary[target_qubit])
                    j_bit = int(j_binary[target_qubit])
                    
                    # Update the density matrix
                    rho[i_bit, j_bit] += state_vector[i] * np.conj(state_vector[j])
        
        # Calculate the qubit state from the reduced density matrix
        # This is an approximation - for more precise results, eigendecomposition would be better
        qubit_state = np.zeros(2, dtype=complex)
        qubit_state[0] = np.sqrt(rho[0, 0])
        if rho[0, 1] != 0:
            phase = np.angle(rho[0, 1]) / 2
            qubit_state[1] = np.sqrt(rho[1, 1]) * np.exp(1j * phase)
        else:
            qubit_state[1] = np.sqrt(rho[1, 1])
        
        return qubit_state

# Dialog for selecting qubits to visualize
class QubitSelectorDialog(QDialog):
    def __init__(self, parent=None, num_qubits=1):
        super().__init__(parent)
        self.setWindowTitle("Select Qubits to Visualize")
        self.num_qubits = num_qubits
        self.selected_qubits = [0]  # Default to first qubit
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Label
        layout.addWidget(QLabel("Select up to 3 qubits to visualize on the Bloch sphere:"))
        
        # Qubit selection
        qubit_layout = QHBoxLayout()
        
        self.qubit_combos = []
        for i in range(3):  # Allow up to 3 qubits
            combo = QComboBox()
            combo.addItem("None")
            for j in range(self.num_qubits):
                combo.addItem(f"Qubit {j}")
            
            # Set first combo to Qubit 0 by default
            if i == 0:
                combo.setCurrentIndex(1)
            
            self.qubit_combos.append(combo)
            qubit_layout.addWidget(combo)
        
        layout.addLayout(qubit_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_selected_qubits(self):
        # Get the list of selected qubits.
        selected = []
        for combo in self.qubit_combos:
            index = combo.currentIndex()
            if index > 0:  # Not "None"
                qubit_idx = index - 1  # -1 because index 0 is "None"
                if qubit_idx not in selected:  # Avoid duplicates
                    selected.append(qubit_idx)
        
        return selected if selected else [0]  # Default to qubit 0 if nothing selected
