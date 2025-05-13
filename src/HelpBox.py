import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

HELP_TEXT = """
**Qubox: Quantum Circuit Designer - Quick Help**

**1. Adding Gates:**
   - Click and drag a gate from the 'Gate Palette' on the left onto a qubit wire in the main circuit view.
   - Rotation gates (Rx2/4/8, Ry2/4/8, Rz2/4/8) have set parameters (1/2-pi turns, 1/4-pi turns, 1/8-pi turns)
   - For multi-qubit gates (CNOT, SWAP, Toffoli, Bell):
     - Drag the gate onto the desired *control* qubit wire.
     - A menu will appear; select the *target* qubit.
     - For Toffoli, a second menu will appear to select the *second control* qubit.

**2. Moving Gates:**
   - Click and drag an existing gate on the circuit to a new time step or qubit wire.
   - Gates will automatically snap to the grid.

**3. Deleting Gates:**
   - Select a gate by clicking on it.
   - Press the 'Delete' key on your keyboard.
   - Alternatively, right-click on a gate and select 'Delete Gate'.

**4. Setting Initial Qubit States:**
   - Right-click on a qubit wire (e.g., 'q0: |0⟩').
   - Select 'Set Initial State' and choose the desired state (|0⟩, |1⟩, |+⟩, |-⟩).
   - You can also select multiple wires (Shift+Click or drag selection) and use the 'Initial State' dropdown in the toolbar.

**5. Custom Gates:**
   - Click 'Define Custom Gate' in the toolbar.
   - Enter a name, number of qubits, and the sequence of standard gates (e.g., 'H 0', 'CNOT 0,1').
   - The new custom gate will appear in the 'Gate Palette'. Drag it like any other gate.

**6. Saving and Loading:**
   - Use 'Save Circuit' and 'Load Circuit' buttons in the toolbar to save/load your designs in QASM format.

**7. QASM Editor:**
   - The panel on the right shows the OpenQASM 2.0 code for the current circuit.
   - You can manually edit the QASM code.
   - Click 'Update Circuit from QASM' to apply your edits to the visual circuit.
   - Click 'Update QASM from Circuit' to refresh the QASM code based on the visual circuit.

**8. Bloch Sphere:**
   - Click 'Bloch Display' in the toolbar.
   - Select the qubit(s) you want to visualize.
   - The Bloch sphere(s) will show the state of the selected qubit(s) based on the current circuit. Click 'Update Visualization' if needed after changes.

**9. Qubit Count:**
   - Use the '+' and '-' buttons next to 'Number of Qubits' in the toolbar to change the circuit size.
"""

def get_help_text():
    # Returns the application help text.
    return HELP_TEXT


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Qubox Help")
        self.setMinimumSize(600, 400) 
        # Adjust size as needed

        layout = QVBoxLayout()
        
        help_content = QTextEdit()
        help_content.setReadOnly(True)
        # Use Markdown for basic formatting
        help_content.setMarkdown(get_help_text()) 
        
        layout.addWidget(help_content)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

