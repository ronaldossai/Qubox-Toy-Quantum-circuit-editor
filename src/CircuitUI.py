import sys
import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QToolBar, QFileDialog, 
                             QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QMenu, QDialog,
                             QLineEdit, QFormLayout, QSpinBox, QTextEdit, QSplitter, QDoubleSpinBox,
                             QScrollArea, QGridLayout, QToolTip)
from PyQt6.QtCore import Qt, QRectF, QPointF, QMimeData, pyqtSignal, QSize, QTimer, QPoint, QLineF
from PyQt6.QtGui import (QColor, QPen, QBrush, QPainter, QFont, QDrag, QPixmap, QShortcut, QKeySequence, QCursor,
                         QAction, QIcon)

from CircuitBackend import QuantumCircuit, Qubit
from BlochSphere import BlochSphereWidget, QubitSelectorDialog
from HelpBox import HelpDialog 


class CircuitElement:
    # Base class for circuit elements (gates and wires).
    def __init__(self, name, color=Qt.GlobalColor.white):
        self.name = name
        self.color = color
        self.width = 60
        self.height = 40
        
class GateGraphicsItem(QGraphicsItem):
    # Graphics item representing a quantum gate.
    
    def __init__(self, gate_type: str, params=None):
        super().__init__()
        self.gate_type = gate_type
        self.params = params
        self.is_custom = False  # Add this flag for custom gates
        self.setAcceptDrops(False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Set size based on gate type
        self.width = 50 if gate_type in ["CNOT", "Toffoli", "SWAP", "Measure", "Bell"] else 40
        self.height = 40
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        # Draw gate box
        painter.setPen(QPen(QColor("#333333")))
        painter.setBrush(QBrush(QColor("#ffffff")))
        
        # Add a bit of styling when selected
        if self.isSelected():
            painter.setBrush(QBrush(QColor("#e0f7fa")))  # Light blue when selected
            painter.setPen(QPen(QColor("#0277bd"), 2))  # Thicker blue border when selected
        
        # Different visuals for different gate types
        if self.gate_type == "CNOT":
            # Draw control qubit circle
            control_circle_rect = QRectF(5, 5, 10, 10)
            painter.drawEllipse(control_circle_rect)
            painter.drawLine(QLineF(10, 15, 10, 35))
            
            # Draw target qubit X
            target_x_rect = QRectF(25, 25, 20, 10)
            painter.drawEllipse(target_x_rect)
            painter.drawLine(QLineF(25, 30, 45, 30))
        elif self.gate_type == "Toffoli":
            # Draw three symbols for Toffoli (two controls and a target)
            # First control dot
            painter.drawEllipse(QRectF(5, 5, 10, 10))
            # Second control dot
            painter.drawEllipse(QRectF(20, 5, 10, 10))
            # Vertical line connecting them
            painter.drawLine(QLineF(10, 15, 10, 35))
            painter.drawLine(QLineF(25, 15, 25, 25))
            painter.drawLine(QLineF(10, 25, 40, 25))
            
            # Target X
            target_x_rect = QRectF(30, 25, 20, 10)
            painter.drawEllipse(target_x_rect)
            painter.drawLine(QLineF(30, 30, 50, 30))
        elif self.gate_type == "SWAP":
            # Draw an X on both ends, connected by a line
            painter.drawLine(QLineF(10, 10, 20, 20))
            painter.drawLine(QLineF(10, 20, 20, 10))
            painter.drawLine(QLineF(15, 15, 35, 15))
            painter.drawLine(QLineF(30, 10, 40, 20))
            painter.drawLine(QLineF(30, 20, 40, 10))
        elif self.gate_type == "Measure":
            # Draw a simple measurement symbol (half-circle with line)
            painter.drawChord(QRectF(5, 5, 30, 30), 0, 180 * 16)
            painter.drawLine(QLineF(5, 20, 35, 20))
            # Draw an arrow pointing right
            painter.drawLine(QLineF(35, 20, 45, 20))
            painter.drawLine(QLineF(40, 15, 45, 20))
            painter.drawLine(QLineF(40, 25, 45, 20))
        else:
            # Draw standard gate box
            painter.drawRect(self.boundingRect())
            
            # Set font
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            
            # Draw gate symbol
            text = self.gate_type
            if self.params and self.gate_type in ["Rx", "Ry", "Rz"]:
                # Format parameter as angle in π units
                angle = self.params[0] / np.pi
                if abs(angle) == 1:
                    param_text = "π"
                elif angle == 0.5:
                    param_text = "π/2"
                elif angle == 0.25:
                    param_text = "π/4"
                elif angle == 0.125:
                    param_text = "π/8"
                elif angle == 0:
                    param_text = "0"
                else:
                    param_text = f"{angle:.2f}π"
                text = f"{self.gate_type}({param_text})"
                
                # Use smaller font for parameterized gates
                font.setPointSize(8)
                painter.setFont(font)
            
            # Center text in gate
            text_rect = painter.fontMetrics().boundingRect(text)
            x = (self.width - text_rect.width()) / 2
            y = (self.height + text_rect.height()) / 2
            painter.drawText(QPointF(x, y), text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Start drag operation
            drag = QDrag(self.scene().views()[0])
            mime_data = QMimeData()
            mime_data.setText(self.gate_type)
            if self.params:
                mime_data.setData("application/x-gate-params", str(self.params[0]).encode())
            
            # Create pixmap for drag
            pixmap = QPixmap(self.boundingRect().size().toSize())
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.paint(painter, None, None)
            painter.end()
            
            drag.setMimeData(mime_data)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPointF(pixmap.width()/2, pixmap.height()/2).toPoint())
            
            if drag.exec(Qt.DropAction.MoveAction) == Qt.DropAction.MoveAction:
                self.scene().removeItem(self)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        #Handle mouse release events.
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
    
    def contextMenuEvent(self, event):
        #Show context menu on right-click.
        menu = QMenu()
        
        if self.gate_type in ["CNOT", "Toffoli", "SWAP", "Bell"]:
            delete_action = menu.addAction("Delete Multi-Qubit Gate")
            delete_action.setIcon(QIcon.fromTheme("edit-delete"))
        else:
            delete_action = menu.addAction("Delete Gate")
        
        action = menu.exec(event.screenPos())
        
        if action == delete_action:
            # First, find the time step and qubit index for this gate
            pos = self.scenePos()
            scene = self.scene()
            time_step = round((pos.x() - scene.margin - scene.label_width) / scene.time_step_width)
            qubit = round((pos.y() - scene.margin) / scene.qubit_spacing)
            
            # Remove gate and all associated visuals using the remove_gate method 
            # instead of just removing the item
            scene.remove_gate(time_step, qubit)
        
        super().contextMenuEvent(event)

class QubitWireGraphicsItem(QGraphicsItem):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.width = 800  # Increased width to fill available space
        self.height = 40  # Height for the qubit wire
        self.state = "0"  # Default state
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)
        self.setAcceptHoverEvents(True)
        self.hovered = False
        self.label_width = 80  # Width reserved for label
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw selection highlight
        if self.isSelected() or self.hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(230, 230, 255))
            painter.drawRect(self.boundingRect())
        
        # Draw wire line in the middle of the height
        wire_y = int(self.height/2)  # Center of wire
        
        # Draw thinner line
        painter.setPen(QPen(Qt.GlobalColor.black, 0.5))  # Reduced thickness
        
        # Draw the line starting after the label area to the end
        painter.drawLine(self.label_width, wire_y, int(self.width), wire_y)
        
        # Draw qubit label and state
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        
        # Draw initial state
        state_label = f"|{self.state}⟩"
        if self.state == "+":
            state_label = "|+⟩"
        elif self.state == "-":
            state_label = "|-⟩"
        
        # Draw label in dedicated label area
        label_rect = QRectF(5, 0, self.label_width - 10, self.height)
        painter.drawText(label_rect, 
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 
                        f"q{self.index}: {state_label}")
        
        # Draw a subtle vertical line to separate the label from the circuit
        painter.setPen(QPen(QColor(200, 200, 200), 0.5, Qt.PenStyle.DashLine))
        painter.drawLine(self.label_width, 0, self.label_width, self.height)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle selection
            self.setSelected(not self.isSelected())
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.showContextMenu(event)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)
    
    def showContextMenu(self, event):
        menu = QMenu()
        state_menu = menu.addMenu("Set Initial State")
        
        states = [
            ("State |0⟩", "0"),
            ("State |1⟩", "1"),
            ("State |+⟩", "+"),
            ("State |-⟩", "-")
        ]
        
        for label, state in states:
            action = state_menu.addAction(label)
            action.setData(state)
        
        action = menu.exec(event.screenPos())
        if action:
            self.state = action.data()
            self.update()
            if self.scene():
                self.scene().circuit_changed.emit()

class CircuitScene(QGraphicsScene):
    # Graphics scene for the quantum circuit design.
    
    circuit_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_qubits = 3  # Default number of qubits
        self.qubit_spacing = 80
        self.max_time_steps = 16  # Fixed number of time steps
        self.time_step_width = 60  # This will be recalculated based on view size
        self.margin = 40
        self.label_width = 80  # Width reserved for qubit labels
        self.circuit = []  # List of time steps, each containing a list of gates
        self.initialize_circuit()
    
    def update_display_size(self):
        # Update scene size and wire lengths based on view size
        # Calculate view width based on available space in the parent view
        view_width = 800  # Default width
        if self.parent() and hasattr(self.parent(), 'viewport'):
            view_width = max(800, self.parent().viewport().width() - 20)  # Small margin
        
        # Calculate time step width based on available space and fixed number of time steps
        available_width = view_width - 2 * self.margin - self.label_width
        self.time_step_width = max(60, available_width / self.max_time_steps)
        
        # Update scene rectangle to match view size
        self.setSceneRect(0, 0, view_width, self.num_qubits * self.qubit_spacing + 2 * self.margin)
        
        # Update all qubit wires to extend across the full width
        for i, wire in enumerate(self.qubit_wires):
            wire.width = view_width - 2 * self.margin
            # Force a redraw
            wire.update()
    
    def initialize_circuit(self):
        # Initialize the circuit with qubit wires.
        self.clear()
        self.circuit = []
        
        # Calculate view width based on available space in the parent view if possible
        view_width = 800
        if self.parent() and hasattr(self.parent(), 'viewport'):
            view_width = max(800, self.parent().viewport().width() - 20)  # Small margin
        
        # Initialize circuit with fixed time steps
        for _ in range(self.max_time_steps):
            self.circuit.append([None] * self.num_qubits)
        
        # Calculate time step width based on available space
        available_width = view_width - 2 * self.margin - self.label_width
        self.time_step_width = max(60, available_width / self.max_time_steps)
        
        self.setSceneRect(0, 0, view_width, self.num_qubits * self.qubit_spacing + 2 * self.margin)
        
        # Add qubit wires
        self.qubit_wires = []
        for i in range(self.num_qubits):
            wire = QubitWireGraphicsItem(i)
            wire.width = view_width - 2 * self.margin  # Width adjusted to fit view
            wire.setPos(self.margin, self.margin + i * self.qubit_spacing)
            self.addItem(wire)
            self.qubit_wires.append(wire)
        
        self.circuit_changed.emit()
    
    def set_num_qubits(self, num):
        # Set the number of qubits in the circuit
        if self.num_qubits != num:
            self.num_qubits = num
            self.initialize_circuit()
            # Update display size to ensure proper wire lengths
            self.update_display_size()
    
    def build_circuit(self):
        # Build a QuantumCircuit object from the current circuit data.
        circuit = QuantumCircuit(self.num_qubits)
        
        # Set initial states
        for i, wire in enumerate(self.qubit_wires):
            circuit.set_initial_state(i, wire.state)
        
        # Add gates from circuit data
        for time_step, gates in enumerate(self.circuit):
            processed_qubits = set()  # Track which qubits have been processed
            
            for qubit, gate_info in enumerate(gates): # Renamed gate_data to gate_info
                if gate_info is None or qubit in processed_qubits:
                    continue
                
                # Updated logic to handle new gate_info structure 
                gate_type = None
                params = None
                role = None
                other_qubit = None

                if isinstance(gate_info, tuple):
                    # Possible structures:
                    # (gate_type, params, item_ref) -> len 3
                    # (gate_type, role, other_qubit, item_ref) -> len 4
                    gate_type = gate_info[0]
                    if len(gate_info) == 3: # Single qubit gate with item ref
                        params = gate_info[1] # Might be None
                    elif len(gate_info) == 4: # Multi qubit gate role with item ref
                        role = gate_info[1]
                        other_qubit = gate_info[2]
                    else:
                         # Should not happen with the new structure, but handle defensively
                         print(f"Warning: Unexpected gate_info structure at step {time_step}, qubit {qubit}: {gate_info}")
                         continue
                else:
                     # Should not happen anymore, previously allowed simple gate_type strings
                     print(f"Warning: Unexpected gate_info type at step {time_step}, qubit {qubit}: {type(gate_info)}")
                     continue

                # Process based on extracted info
                if role is None: # Single-qubit gate
                    try:
                        # Add gate expects: gate_type, target_qubits (list), params (list or None)
                        circuit.add_gate(gate_type, [qubit], params)
                    except ValueError as e:
                        print(f"Error adding gate {gate_type} at step {time_step}, qubit {qubit}: {e}")
                
                elif role in ["control", "control1", "control2"]: # Multi-qubit gate (handle from control side)
                    if gate_type == "Toffoli":
                        # Find the second control qubit
                        control1 = qubit
                        control2 = -1
                        target = other_qubit # Target is stored with control1/control2

                        for i, data in enumerate(self.circuit[time_step]):
                            if (data and isinstance(data, tuple) and len(data) == 4 and
                                data[0] == "Toffoli" and data[1] == "control2" and data[2] == target and i != control1):
                                control2 = i
                                break
                        
                        if control2 != -1 and control2 not in processed_qubits:
                             try:
                                 # Add gate expects: gate_type, target_qubits (list), params (None)
                                 circuit.add_gate(gate_type, [control1, control2, target])
                                 processed_qubits.update([control1, control2, target])
                             except ValueError as e:
                                 print(f"Error adding Toffoli gate at step {time_step}: {e}")
                        # else: Control2 already processed or not found (error state?)

                    else: # CNOT, SWAP, Bell
                        control = qubit
                        target = other_qubit
                        if target not in processed_qubits:
                            try:
                                if gate_type == "SWAP":
                                     # Add gate expects: gate_type, target_qubits (list), params (None)
                                     circuit.add_gate(gate_type, sorted([control, target])) # Ensure consistent order
                                else: # CNOT, Bell
                                     # Add gate expects: gate_type, target_qubits (list), params (None)
                                     circuit.add_gate(gate_type, [control, target])
                                processed_qubits.update([control, target])
                            except ValueError as e:
                                print(f"Error adding {gate_type} gate at step {time_step}: {e}")
                        # else: Target already processed

                elif role == "target":
                     # Target qubits are handled when processing the control qubit(s)
                     # Mark as processed to avoid redundant checks, but don't add the gate here.
                     processed_qubits.add(qubit)
                     pass 
                # --- End of updated logic ---
        
        return circuit
    
    def add_gate(self, gate_type: str, target_qubits: List[int], params=None, time_step: int = None):
        # Add a gate to the circuit at the specified time step
        if time_step is None:
            # Find the first empty time step
            time_step = 0
            while time_step < len(self.circuit):
                # Check if all target qubits are empty at this time step
                if all(self.circuit[time_step][q] is None for q in target_qubits):
                    break
                time_step += 1
            
            # If we reached the end, make sure we don't exceed max_time_steps
            if time_step >= self.max_time_steps:
                print(f"Warning: Cannot add gate beyond max time steps ({self.max_time_steps})")
                return
        
        
        # Create the new GateGraphicsItem first
        new_gate_item = GateGraphicsItem(gate_type, params)
        if gate_type in ["CNOT", "SWAP", "Bell", "Toffoli"]: # Handle custom sequence flag if needed
             pass # Potentially set new_gate_item.is_custom based on gate_type or params/sequence later
        
        # Determine position for the new item
        # Use the *first* target qubit for positioning single-qubit and the control/main part of multi-qubit gates
        main_target_qubit = target_qubits[0]
        gate_x = self.margin + self.label_width + time_step * self.time_step_width
        wire_center_y = self.margin + main_target_qubit * self.qubit_spacing + self.qubit_wires[0].height / 2
        gate_y = wire_center_y - new_gate_item.height / 2
        new_gate_item.setPos(gate_x, gate_y)

        # Clear existing data and visuals at the target location(s) and add the new gate
        associated_items_to_add = [new_gate_item] # List to hold the main gate and any connecting lines/markers

        if gate_type in ["CNOT", "Toffoli", "SWAP", "Bell"]:
            # Multi-qubit gates need special handling for data and visuals
            control = target_qubits[0]
            target = target_qubits[-1]

            # Remove any existing items at control, target (and control2 for Toffoli) positions
            qubits_to_clear = target_qubits[:] # Copy the list
            self.remove_gate(time_step, control) # Handles removing item and data
            self.remove_gate(time_step, target)

            if gate_type == "Toffoli":
                control2 = target_qubits[1]
                self.remove_gate(time_step, control2)
                # Store data (gate_type, role, other_qubit, item_ref)
                self.circuit[time_step][control] = (gate_type, "control1", target, new_gate_item)
                self.circuit[time_step][control2] = (gate_type, "control2", target, new_gate_item) # Reference same main item
                self.circuit[time_step][target] = (gate_type, "target", control, new_gate_item) # Reference same main item
            else: # CNOT, SWAP, Bell
                # Store data (gate_type, role, other_qubit, item_ref)
                self.circuit[time_step][control] = (gate_type, "control", target, new_gate_item)
                self.circuit[time_step][target] = (gate_type, "target", control, new_gate_item) # Reference same main item

            # Add visuals for multi-qubit gates (lines, markers)
            line, target_marker = self._create_multi_qubit_visuals(gate_type, target_qubits, time_step, new_gate_item)
            if line:
                associated_items_to_add.append(line)
            if target_marker:
                associated_items_to_add.append(target_marker)

        else:
            # Single-qubit gate (H, X, Rx, Measure, Reset, etc.) or Custom Gate treated as single block
            target_qubit = target_qubits[0]
            # Remove any existing item at the target position
            self.remove_gate(time_step, target_qubit) # Handles removing item and data
            # Store data (gate_type, params, item_ref) - params might be None
            self.circuit[time_step][target_qubit] = (gate_type, params, new_gate_item)

        # Add all necessary visual items to the scene
        for item in associated_items_to_add:
            self.addItem(item)

        # Store current wire positions before updating scene size 
        wire_positions = []
        for wire in self.qubit_wires:
            wire_positions.append(wire.pos())
        
        # Update scene size if needed 
        current_width = self.sceneRect().width()
        # Recalculate min_required_width based on the actual extent of the circuit data
        max_used_time_step = -1
        for t in range(len(self.circuit)):
             if any(self.circuit[t]):
                 max_used_time_step = t
        min_required_width = self.margin * 2 + self.label_width + (max_used_time_step + 1) * self.time_step_width

        view_width = current_width
        if self.parent() and hasattr(self.parent(), 'viewport'):
            view_width = max(current_width, self.parent().viewport().width())
        
        new_width = max(view_width, min_required_width)
        if new_width > current_width:
            self.setSceneRect(0, 0, new_width, self.num_qubits * self.qubit_spacing + 2 * self.margin)
            for wire in self.qubit_wires:
                wire.width = new_width - 2 * self.margin
                wire.update()
        
        # Restore wire positions 
        for i, pos in enumerate(wire_positions):
            if i < len(self.qubit_wires):
                self.qubit_wires[i].setPos(pos)
        
        self.circuit_changed.emit()

    # Method to create visual elements for multi-qubit gates (refactored)
    def _create_multi_qubit_visuals(self, gate_type, target_qubits, time_step, main_gate_item):
        line_item = None
        target_marker_item = None
        
        control_qubit = target_qubits[0]
        target_qubit = target_qubits[-1] # Last qubit is the target for CNOT/Toffoli/Bell

        control_x = main_gate_item.scenePos().x() # Use position of the already placed main item

        # Draw a line connecting control and target(s)
        qubits_involved = sorted(target_qubits)
        min_qubit = qubits_involved[0]
        max_qubit = qubits_involved[-1]
        
        if min_qubit != max_qubit:
            line_height = (max_qubit - min_qubit) * self.qubit_spacing
            line_x = control_x + main_gate_item.width / 2
            line_y_start = self.margin + min_qubit * self.qubit_spacing + self.qubit_wires[0].height / 2
            
            line_item = QGraphicsLineItem(0, 0, 0, line_height)
            line_item.setPen(QPen(Qt.GlobalColor.black, 1))
            line_item.setPos(line_x, line_y_start)
            # Set data on the line to identify it as a connecting line
            line_item.setData(0, "connecting_line")
            line_item.setData(1, time_step)
            line_item.setData(2, qubits_involved)

        # Add target marker (e.g., X for CNOT/Toffoli)
        if gate_type in ["CNOT", "Toffoli"]:
            target_x = control_x # Marker aligns vertically with control
            wire_center_y = self.margin + target_qubit * self.qubit_spacing + self.qubit_wires[0].height / 2
            
            # Use a simple circle or standard marker instead of a full GateGraphicsItem for the target
            marker_radius = 8
            target_marker_item = self.addEllipse(
                target_x + main_gate_item.width / 2 - marker_radius, 
                wire_center_y - marker_radius, 
                2 * marker_radius, 
                2 * marker_radius,
                QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.black if gate_type == "CNOT" else Qt.GlobalColor.white) # Solid for CNOT, hollow for Toffoli target? Or use X... let's stick to X
            )
            # Let's try drawing an 'X' symbol instead for CNOT/Toffoli target
            self.removeItem(target_marker_item) # Remove the ellipse if we added it
            target_marker_item = self.addText("X")
            font = QFont(); font.setPointSize(12); font.setBold(True)
            target_marker_item.setFont(font)
            marker_rect = target_marker_item.boundingRect()
            target_marker_item.setPos(target_x + (main_gate_item.width - marker_rect.width()) / 2, 
                                      wire_center_y - marker_rect.height() / 2)

        elif gate_type == "SWAP":
             # Add SWAP markers (X on both ends)
             marker1 = self.addText("X")
             marker2 = self.addText("X")
             font = QFont(); font.setPointSize(10);
             marker1.setFont(font); marker2.setFont(font)

             q1, q2 = target_qubits[0], target_qubits[1]
             y1 = self.margin + q1 * self.qubit_spacing + self.qubit_wires[0].height / 2
             y2 = self.margin + q2 * self.qubit_spacing + self.qubit_wires[0].height / 2
             x_pos = control_x + main_gate_item.width / 2 - marker1.boundingRect().width() / 2 # Center the X

             marker1.setPos(x_pos, y1 - marker1.boundingRect().height() / 2)
             marker2.setPos(x_pos, y2 - marker2.boundingRect().height() / 2)
             self.removeItem(marker1)
             self.removeItem(marker2)
             target_marker_item = None # No single target marker for SWAP visuals added this way

        return line_item, target_marker_item

    def remove_gate(self, time_step: int, qubit: int):
        # Remove gate data and visual elements at the specified time step and qubit
        if 0 <= time_step < len(self.circuit) and 0 <= qubit < self.num_qubits:
            gate_info = self.circuit[time_step][qubit]
            
            if gate_info is None:
                return # Nothing to remove

            item_to_remove = None
            items_to_remove = [] # For multi-qubit gates that might have associated visuals

            # Check the structure of gate_info to get the item reference
            # Expected structures:
            # Single qubit: (gate_type, params, item_ref)
            # Multi qubit: (gate_type, role, other_qubit, item_ref)
            
            if isinstance(gate_info, tuple):
                if len(gate_info) >= 3 and isinstance(gate_info[-1], QGraphicsItem):
                    item_ref = gate_info[-1]
                    if item_ref is not None: # Ensure item_ref is valid
                        items_to_remove.append(item_ref)


                # If removing a control, also clear target data.

                if len(gate_info) == 4:
                    gate_type, role, other_qubit = gate_info[0], gate_info[1], gate_info[2]
                    
                    # Find and remove connecting lines for multi-qubit gates
                    if gate_type in ["CNOT", "Toffoli", "SWAP", "Bell"]:
                        qubits_involved = [qubit]
                        if 0 <= other_qubit < self.num_qubits:
                            qubits_involved.append(other_qubit)
                            
                            # For Toffoli gates, find the other control qubit
                            if gate_type == "Toffoli" and role in ["control1", "target"]:
                                for i, data in enumerate(self.circuit[time_step]):
                                    if (data and isinstance(data, tuple) and len(data) == 4 and
                                        data[0] == "Toffoli" and data[1] == "control2"):
                                        qubits_involved.append(i)
                                        break
                                        
                        # Find and remove the connecting line based on position
                        connecting_lines = self.find_connecting_lines(time_step, qubits_involved)
                        items_to_remove.extend(connecting_lines)
                    
                    if role in ["control", "control1", "control2"]:
                        # Also clear the data for the target qubit(s)
                        if 0 <= other_qubit < self.num_qubits:
                            # clear the *data* here. The target's remove_gate call
                            # should handle removing its own marker if applicable.
                            target_info = self.circuit[time_step][other_qubit]
                            if target_info and isinstance(target_info, tuple) and len(target_info) == 4:
                                # Check if target references the *same* main item, if so, don't remove visual yet
                                if target_info[-1] != item_ref:
                                    # If target has its own distinct visual (e.g., marker), remove it
                                    if target_info[-1] is not None and isinstance(target_info[-1], QGraphicsItem):
                                        items_to_remove.append(target_info[-1]) # Add target's distinct visual
                            self.circuit[time_step][other_qubit] = None

                        if gate_type == "Toffoli" and role == "control1": # Find and clear control2
                            # Find control2 by searching the row
                            for i, data in enumerate(self.circuit[time_step]):
                                if (data and isinstance(data, tuple) and len(data) == 4 and
                                    data[0] == "Toffoli" and data[1] == "control2" and data[2] == other_qubit):
                                    # Check if control2 has its own distinct visual item reference
                                    if data[-1] != item_ref and data[-1] is not None and isinstance(data[-1], QGraphicsItem):
                                        items_to_remove.append(data[-1])
                                    self.circuit[time_step][i] = None # Clear control2 data
                                    break # Found control2

            # Remove the identified items from the scene
            for item in items_to_remove:
                if item.scene() == self: # Check if item is actually in the scene
                    self.removeItem(item)

            # Clear the circuit data for the primary qubit
            self.circuit[time_step][qubit] = None
            # --- End of new logic ---

            self.circuit_changed.emit()
        
    def find_connecting_lines(self, time_step, qubits_involved):
        # Find connecting lines for multi-qubit gates based on position.
        connecting_lines = []
        
        # Sort qubits to properly identify the line
        qubits_involved = sorted(qubits_involved)
        
        # Scan all items in the scene
        for item in self.items():
            # Check if the item is a QGraphicsLineItem that might be a connecting line
            if isinstance(item, QGraphicsLineItem):
                # Special check for items we've tagged with metadata
                if (item.data(0) == "connecting_line" and 
                    item.data(1) == time_step):
                    # Add it to the list of items to remove
                    connecting_lines.append(item)
                # Fallback positional check for older lines that might not have metadata
                else:
                    # Try to determine if this is a connecting line for our multi-qubit gate
                    # based on its position and size
                    if len(qubits_involved) >= 2:
                        min_qubit = qubits_involved[0]
                        max_qubit = qubits_involved[-1]
                        line_height = (max_qubit - min_qubit) * self.qubit_spacing
                        
                        # Check if the line matches the expected position
                        line_y_start = self.margin + min_qubit * self.qubit_spacing + self.qubit_wires[0].height / 2
                        
                        # Get the time step position
                        time_step_x = self.margin + self.label_width + time_step * self.time_step_width
                        
                        # Allow some tolerance in position matching
                        tolerance = 10
                        item_pos = item.scenePos()
                        item_height = item.line().y2()
                        
                        # Check if this line matches our expected position and size
                        if (abs(item_pos.y() - line_y_start) < tolerance and
                            abs(item_pos.x() - time_step_x) < self.time_step_width and
                            abs(item_height - line_height) < tolerance):
                            connecting_lines.append(item)
                            
        return connecting_lines
    
    def paint(self, painter, option, widget):
        # Draw grid lines
        painter.setPen(QPen(QColor(240, 240, 240)))  # Light gray color for grid
        
        # Draw vertical grid lines (time steps) - exactly one line per time step
        for i in range(self.max_time_steps + 1):  # +1 to include a line at the end
            x = self.margin + self.label_width + i * self.time_step_width
            painter.drawLine(x, self.margin, x, self.height() - self.margin)
        
        # Draw horizontal grid lines (qubit wires)
        for y in range(self.margin, int(self.height()), self.qubit_spacing):
            painter.drawLine(self.margin + self.label_width, y, 
                            self.width() - self.margin, y)

class ParameterDialog(QDialog):
    def __init__(self, gate_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Set {gate_type} Parameter")
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QDoubleSpinBox {
                background-color: white;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
                text-align: center;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0;
                border: none;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Parameter input
        form_layout = QFormLayout()
        
        # Create a horizontal layout for parameter control
        param_control_widget = QWidget()
        param_control_layout = QHBoxLayout()
        param_control_layout.setContentsMargins(0, 0, 0, 0)
        param_control_layout.setSpacing(5)
        
        # Add decrease button
        decrease_button = QPushButton("-")
        decrease_button.setFixedSize(24, 24)
        param_control_layout.addWidget(decrease_button)
        
        # Add spin box
        self.param_input = QDoubleSpinBox()
        self.param_input.setRange(-2*np.pi, 2*np.pi)
        self.param_input.setSingleStep(np.pi/4)
        self.param_input.setValue(0)
        self.param_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)  # Hide the up/down arrows
        param_control_layout.addWidget(self.param_input)
        
        # Add increase button
        increase_button = QPushButton("+")
        increase_button.setFixedSize(24, 24)
        param_control_layout.addWidget(increase_button)
        
        # Connect the buttons
        decrease_button.clicked.connect(lambda: self.param_input.setValue(self.param_input.value() - self.param_input.singleStep()))
        increase_button.clicked.connect(lambda: self.param_input.setValue(self.param_input.value() + self.param_input.singleStep()))
        
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_parameter(self) -> float:
        return self.param_input.value()

class GatePalette(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.custom_gates = {}  # Dictionary to store custom gate definitions
        self.custom_gate_count = 0  # Track number of custom gates for layout
        self.initUI()
        self.setAcceptDrops(False)
    
    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Create scrollable area for gates
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Single-qubit gates section
        single_qubit_label = QLabel("Single-qubit gates:")
        single_qubit_label.setStyleSheet("font-weight: bold; color: #333333;")
        scroll_layout.addWidget(single_qubit_label)
        
        # Create layout for single-qubit gates
        single_qubit_layout = QGridLayout()
        single_qubit_layout.setSpacing(5)
        
        # Add single-qubit gate buttons
        single_qubit_gates = [
            "H", "X", "Y", "Z", "S", "T", 
            # Remove redundant gates (Rx, Ry, Rz)
            # Add new rotation gates with predefined angles
            "R2x", "R2y", "R2z",  # π/2 rotations
            "R4x", "R4y", "R4z",  # π/4 rotations
            "R8x", "R8y", "R8z"   # π/8 rotations
        ]
        
        for idx, gate in enumerate(single_qubit_gates):
            button = QPushButton(gate)
            button.setFixedSize(40, 40)
            button.setObjectName(gate)
            # Remove tooltip for redundant gates (Rx, Ry, Rz)
            if gate.startswith("R2"):
                button.setToolTip(f"{gate} - Rotation around {gate[2]}-axis by π/2")
            elif gate.startswith("R4"):
                button.setToolTip(f"{gate} - Rotation around {gate[2]}-axis by π/4")
            elif gate.startswith("R8"):
                button.setToolTip(f"{gate} - Rotation around {gate[2]}-axis by π/8")
            button.mousePressEvent = lambda event, g=gate: self.buttonMousePressEvent(event, g)
            row, col = divmod(idx, 3)
            single_qubit_layout.addWidget(button, row, col)
        
        scroll_layout.addLayout(single_qubit_layout)
        
        # Multi-qubit gates section
        multi_qubit_label = QLabel("Multi-qubit gates:")
        multi_qubit_label.setStyleSheet("font-weight: bold; color: #333333;")
        scroll_layout.addWidget(multi_qubit_label)
        
        # Create layout for multi-qubit gates
        multi_qubit_layout = QGridLayout()
        multi_qubit_layout.setSpacing(5)
        
        # Add multi-qubit gate buttons
        multi_qubit_gates = ["CNOT", "SWAP", "Toffoli", "Bell"]
        for idx, gate in enumerate(multi_qubit_gates):
            button = QPushButton(gate)
            button.setFixedSize(60, 40)
            button.setObjectName(gate)
            button.mousePressEvent = lambda event, g=gate: self.buttonMousePressEvent(event, g)
            row, col = divmod(idx, 2)
            multi_qubit_layout.addWidget(button, row, col)
        
        scroll_layout.addLayout(multi_qubit_layout)
        
        # Special gates section (Measure, Reset)
        special_label = QLabel("Special gates:")
        special_label.setStyleSheet("font-weight: bold; color: #333333;")
        scroll_layout.addWidget(special_label)
        
        special_layout = QGridLayout()
        special_layout.setSpacing(5)
        
        special_gates = ["Measure", "Reset"]
        for idx, gate in enumerate(special_gates):
            button = QPushButton(gate)
            button.setFixedSize(60, 40)
            button.setObjectName(gate)
            button.mousePressEvent = lambda event, g=gate: self.buttonMousePressEvent(event, g)
            special_layout.addWidget(button, 0, idx)
        
        scroll_layout.addLayout(special_layout)
        
        # Custom gates section
        self.custom_gates_label = QLabel("Custom gates (0):")
        self.custom_gates_label.setStyleSheet("font-weight: bold; color: #333333;")
        scroll_layout.addWidget(self.custom_gates_label)
        
        # Container for custom gates
        self.custom_gates_layout = QVBoxLayout()
        self.custom_gates_layout.setSpacing(5)
        self.current_custom_row = QHBoxLayout()
        self.current_custom_row.setSpacing(5)
        self.custom_gates_layout.addLayout(self.current_custom_row)
        self.custom_gate_count = 0
        
        scroll_layout.addLayout(self.custom_gates_layout)
        
        # Add spacer at the bottom
        scroll_layout.addStretch()
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
    def create_gate(self, gate_type: str, params: List[float] = None):
        # Create a gate item for dragging.
        # Create a gate item
        gate_item = GateGraphicsItem(gate_type, params)
        
        # Create a pixmap for the drag
        pixmap = QPixmap(gate_item.boundingRect().size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gate_item.paint(painter, None, None)
        painter.end()
        
        # Create drag
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(gate_type)
        
        # Include parameters in the drag data if present
        if params:
            mime_data.setData("application/x-gate-params", str(params[0]).encode())
        
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPointF(pixmap.width()/2, pixmap.height()/2).toPoint())
        
        # Start drag operation
        drag.exec(Qt.DropAction.CopyAction)
        print(f"Gate {gate_type} dragged successfully")
    
    def add_custom_gate(self, name: str, sequence: List[Tuple[str, List[int]]]):
        # Add a custom gate to the palette.
        if name in self.custom_gates:
            return  # Gate already exists
        
        self.custom_gates[name] = sequence
        
        # Create button for the custom gate
        gate_button = QPushButton(name)
        gate_button.setFixedSize(60, 40)  # Make consistent with other multi-qubit gates
        gate_button.setObjectName(name)
        gate_button.mousePressEvent = lambda event, g=name: self.buttonMousePressEvent(event, g)
        
        # Add button to custom gates layout with better organization
        # Start a new row after every 2 gates
        if self.custom_gate_count % 2 == 0 and self.custom_gate_count > 0:
            self.current_custom_row = QHBoxLayout()
            self.current_custom_row.setSpacing(5)
            self.custom_gates_layout.addLayout(self.current_custom_row)
        
        self.current_custom_row.addWidget(gate_button)
        self.custom_gate_count += 1
        
        # Update custom gates label
        self.custom_gates_label.setText(f"Custom gates ({len(self.custom_gates)}):")
    
    def buttonMousePressEvent(self, event, gate_type):
        if event.button() == Qt.MouseButton.LeftButton:
            # For rotation gates, use predetermined values
            params = None
            # Remove handlers for redundant gates (Rx, Ry, Rz)
            # Handle new rotation gates with fixed angles
            if gate_type == "R2x":
                params = [np.pi/2]  # π/2 rotation around X-axis
                self.create_gate("Rx", params)
            elif gate_type == "R2y":
                params = [np.pi/2]  # π/2 rotation around Y-axis
                self.create_gate("Ry", params)
            elif gate_type == "R2z":
                params = [np.pi/2]  # π/2 rotation around Z-axis
                self.create_gate("Rz", params)
            elif gate_type == "R4x":
                params = [np.pi/4]  # π/4 rotation around X-axis
                self.create_gate("Rx", params)
            elif gate_type == "R4y":
                params = [np.pi/4]  # π/4 rotation around Y-axis
                self.create_gate("Ry", params)
            elif gate_type == "R4z":
                params = [np.pi/4]  # π/4 rotation around Z-axis
                self.create_gate("Rz", params)
            elif gate_type == "R8x":
                params = [np.pi/8]  # π/8 rotation around X-axis
                self.create_gate("Rx", params)
            elif gate_type == "R8y":
                params = [np.pi/8]  # π/8 rotation around Y-axis
                self.create_gate("Ry", params)
            elif gate_type == "R8z":
                params = [np.pi/8]  # π/8 rotation around Z-axis
                self.create_gate("Rz", params)
            # For custom gates, use the stored sequence
            elif gate_type in self.custom_gates:
                self.create_custom_gate(gate_type)
            else:
                self.create_gate(gate_type, params)
            event.accept()
        else:
            event.ignore()
    
    def create_custom_gate(self, gate_type):
        # Create a custom gate from its sequence.
        if gate_type not in self.custom_gates:
            return
        
        # Create a composite gate item
        gate_item = GateGraphicsItem(gate_type)
        gate_item.is_custom = True
        gate_item.sequence = self.custom_gates[gate_type]
        
        # Create a pixmap for the drag
        pixmap = QPixmap(gate_item.boundingRect().size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gate_item.paint(painter, None, None)
        painter.end()
        
        # Create drag
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(gate_type)
        
        # Store sequence for custom gate
        mime_data.setData("application/x-custom-gate", str(self.custom_gates[gate_type]).encode())
        
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPointF(pixmap.width()/2, pixmap.height()/2).toPoint())
        
        # Start drag operation
        drag.exec(Qt.DropAction.CopyAction)
        print(f"Gate {gate_type} dragged successfully")

class CircuitView(QGraphicsView):
    circuit_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = CircuitScene(self)
        self.setScene(self.scene)
        self.scene.circuit_changed.connect(self.circuit_changed)
        
        # Set up view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
        self.setObjectName("circuit_view")
        self.viewport().setStyleSheet("background-color: white;")
        
        # Enable scrollbars when content exceeds the view size
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Add keyboard shortcuts
        self.copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.copy_shortcut.activated.connect(self.copy_selected_gates)
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.activated.connect(self.paste_gates)
        self.delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        self.delete_shortcut.activated.connect(self.delete_selected_gates)
        
        self.clipboard_gates = []  # Store copied gates
        
        # Initialize dragging attributes
        self.dragging_gate = None
        self.drag_start_pos = None
        
        # Schedule an update of display size after UI initialization
        QTimer.singleShot(0, self.scene.update_display_size)
    
    def resizeEvent(self, event):
        # Handle view resize events to update scene rectangle and wire widths
        super().resizeEvent(event)
        
        # Update scene width to match the new viewport width
        if hasattr(self.scene, 'update_display_size'):
            self.scene.update_display_size()
    
    def showEvent(self, event):
        """Called when the view is shown"""
        super().showEvent(event)
        
        # Update display size when the view becomes visible
        if hasattr(self.scene, 'update_display_size'):
            self.scene.update_display_size()
    
    def copy_selected_gates(self):
        # Copy selected gates to clipboard.
        self.clipboard_gates = []
        for item in self.scene.selectedItems():
            if isinstance(item, GateGraphicsItem):
                gate_data = {
                    'type': item.gate_type,
                    'params': item.params,
                    'is_custom': getattr(item, 'is_custom', False),
                    'sequence': getattr(item, 'sequence', None)
                }
                self.clipboard_gates.append(gate_data)
    
    def paste_gates(self):
        # Paste gates from clipboard.
        if not self.clipboard_gates:
            return
        
        # Get the current mouse position
        pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        
        # Calculate target time step
        time_step = max(0, round((pos.x() - self.scene.margin) / self.scene.time_step_width))
        
        # Calculate target qubit
        target_qubit = round((pos.y() - self.scene.margin) / self.scene.qubit_spacing)
        target_qubit = max(0, min(target_qubit, self.scene.num_qubits - 1))
        
        # Paste each gate
        for gate_data in self.clipboard_gates:
            gate_type = gate_data['type']
            params = gate_data['params']
            is_custom = gate_data['is_custom']
            sequence = gate_data['sequence']
            
            # Create gate item
            gate_item = GateGraphicsItem(gate_type, params)
            if is_custom:
                gate_item.is_custom = True
                gate_item.sequence = sequence
            
            # Position the gate with proper alignment - center it on the wire
            x = self.scene.margin + self.scene.label_width + time_step * self.scene.time_step_width
            # Center the gate perfectly on the wire
            wire_center_y = self.scene.margin + target_qubit * self.scene.qubit_spacing + self.scene.qubit_wires[0].height / 2
            y = wire_center_y - gate_item.height / 2
            gate_item.setPos(x, y)
            
            # Add gate to scene and circuit data structure
            self.scene.addItem(gate_item)
            
            if is_custom:
                self.scene.add_gate(gate_type, [target_qubit], None, time_step)
            else:
                self.scene.add_gate(gate_type, [target_qubit], params, time_step)
            
            target_qubit += 1  # Move to next qubit for next gate
    
    def delete_selected_gates(self):
        # Delete selected gates.
        for item in self.scene.selectedItems():
            if isinstance(item, GateGraphicsItem):
                # Get gate position
                pos = item.scenePos()
                time_step = round((pos.x() - self.scene.margin) / self.scene.time_step_width)
                qubit = round((pos.y() - self.scene.margin) / self.scene.qubit_spacing)
                
                # Remove gate from scene and circuit data
                self.scene.removeItem(item)
                self.scene.remove_gate(time_step, qubit)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on a gate
            item = self.itemAt(event.position().toPoint())
            if isinstance(item, GateGraphicsItem):
                # Prevent dragging multi-qubit gates (CNOT, Toffoli, SWAP, Bell)
                if item.gate_type in ["CNOT", "Toffoli", "SWAP", "Bell"]:
                    # Show tooltip explaining that multi-qubit gates can't be dragged
                    QToolTip.showText(
                        self.mapToGlobal(event.position().toPoint()),
                        "Multi-qubit gates can't be moved. Please delete and recreate instead.",
                        self
                    )
                    return
                # For single-qubit gates, allow dragging as usual
                self.dragging_gate = item
                self.drag_start_pos = item.scenePos()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragging_gate') and self.dragging_gate:
            # Update gate position
            new_pos = self.mapToScene(event.position().toPoint())
            self.dragging_gate.setPos(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        # Handle mouse release event when dragging a gate.
        if self.dragging_gate and event.button() == Qt.MouseButton.LeftButton:
            # Get new position
            new_pos = self.mapToScene(event.position().toPoint())
            
            # Calculate new time step and qubit index
            if new_pos.x() < self.scene.margin + self.scene.label_width:
                new_time_step = 0
            else:
                raw_time_step = (new_pos.x() - self.scene.margin - self.scene.label_width) / self.scene.time_step_width
                new_time_step = max(0, min(round(raw_time_step), self.scene.max_time_steps - 1))
            
            raw_qubit = (new_pos.y() - self.scene.margin) / self.scene.qubit_spacing
            new_qubit = max(0, min(round(raw_qubit), self.scene.num_qubits - 1))
            
            # Get old position/indices needed for removal
            old_pos = self.drag_start_pos
            # Calculate old time step carefully
            if old_pos.x() < self.scene.margin + self.scene.label_width:
                 old_time_step = 0
            else:
                 old_raw_time_step = (old_pos.x() - self.scene.margin - self.scene.label_width) / self.scene.time_step_width
                 # Use round for old time step calculation for consistency with how gates might be stored
                 old_time_step = max(0, min(round(old_raw_time_step), self.scene.max_time_steps - 1))
            
            # Calculate old qubit index carefully
            old_raw_qubit = (old_pos.y() - self.scene.margin) / self.scene.qubit_spacing
            old_qubit = max(0, min(round(old_raw_qubit), self.scene.num_qubits - 1))

            # Get gate info from the item being dragged
            gate_type = self.dragging_gate.gate_type
            params = self.dragging_gate.params
            is_custom = getattr(self.dragging_gate, 'is_custom', False)
            sequence = getattr(self.dragging_gate, 'sequence', None) # Get sequence if it's custom

            # Avoid placing on the same spot if nothing changed logically
            if old_time_step == new_time_step and old_qubit == new_qubit:
                 # Snap back to original calculated grid position 
                 x = self.scene.margin + self.scene.label_width + old_time_step * self.scene.time_step_width
                 wire_center_y = self.scene.margin + old_qubit * self.scene.qubit_spacing + self.scene.qubit_wires[0].height / 2
                 y = wire_center_y - self.dragging_gate.height / 2
                 self.dragging_gate.setPos(x, y) # Snap back visual
                 self.dragging_gate = None
                 event.accept()
                 return
            
            #    This handles removing the old visual based on stored reference.
            self.scene.remove_gate(old_time_step, old_qubit)
            
            #    This will handle creating the new visual item and placing it.
            target_qubits = [new_qubit] # Default for single-qubit gates
            add_params = params # Use original params by default
            
            # Handle custom gates: determine target qubits and package sequence
            if is_custom and sequence:
                 try: 
                     max_q_index = 0
                     for op in sequence:
                         if len(op) >= 2 and isinstance(op[1], list):
                             max_q_index = max(max_q_index, max(op[1]))
                     num_qubits_needed = max_q_index + 1
                     target_qubits = list(range(new_qubit, new_qubit + num_qubits_needed))
                     
                     # Check if move is valid (within bounds)
                     if max(target_qubits) >= self.scene.num_qubits:
                         print("Cannot move custom gate here: requires too many qubits.")
                            # Snap back to original calculated grid position
                         # Re-calculate original target qubits for custom gate
                         old_target_qubits = list(range(old_qubit, old_qubit + num_qubits_needed))
                         self.scene.add_gate(gate_type, old_target_qubits, {"sequence": sequence}, old_time_step)
                         self.dragging_gate = None # Reset dragging state
                         event.accept()
                         return 
                 except Exception as e:
                     print(f"Could not determine qubit count from sequence for move: {e}")
                     target_qubits = [new_qubit] # Fallback
                 
                 add_params = {"sequence": sequence} # Pass sequence info via params
            
            # Add gate to the new position
            self.scene.add_gate(gate_type, target_qubits, add_params, new_time_step)
    
            # Update the visual position of the gate
            # Reset dragging state
            self.dragging_gate = None
            event.accept()
        else:
            # If not dragging a gate, pass event to base class
            super().mouseReleaseEvent(event)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            # Get gate type and parameters
            gate_type = event.mimeData().text()
            params = None
            sequence = None
            
            if event.mimeData().hasFormat("application/x-gate-params"):
                params = [float(event.mimeData().data("application/x-gate-params").data().decode())]
            elif event.mimeData().hasFormat("application/x-custom-gate"):
                sequence = eval(event.mimeData().data("application/x-custom-gate").data().decode())
            
            # Get drop position
            pos = self.mapToScene(event.position().toPoint())
            
            # Calculate target qubit(s)
            target_qubit = round((pos.y() - self.scene.margin) / self.scene.qubit_spacing)
            target_qubit = max(0, min(target_qubit, self.scene.num_qubits - 1))
            
            # Calculate time step within the fixed grid
            # Check if the position is in the label area and adjust if needed
            if pos.x() < self.scene.margin + self.scene.label_width:
                # If dropped on label area, push it to the first time step
                time_step = 0
            else:
                # Calculate time step based on position, ensuring it's within our grid
                raw_time_step = (pos.x() - self.scene.margin - self.scene.label_width) / self.scene.time_step_width
                time_step = max(0, min(round(raw_time_step), self.scene.max_time_steps - 1))
            
            # Handle multi-qubit gates
            if gate_type in ["CNOT", "Toffoli", "SWAP", "Bell"]:
                control_qubit = target_qubit
                
                # Accept the drop action first to finish the drag operation
                event.acceptProposedAction()
                
                # Show a more styled menu to select target qubit
                menu = QMenu(self)
                menu.setStyleSheet("""
                    QMenu {
                        background-color: #f5f5f5;
                        border: 1px solid #cccccc;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QMenu::item {
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                    QMenu::item:selected {
                        background-color: #e0e0e0;
                    }
                """)
                
                # Create a menu title
                title_action = QAction(f"Select target qubit for {gate_type}", self)
                title_action.setEnabled(False)
                font = title_action.font()
                font.setBold(True)
                title_action.setFont(font)
                menu.addAction(title_action)
                menu.addSeparator()
                
                # Add qubit options
                for i in range(self.scene.num_qubits):
                    if i != control_qubit:
                        action = menu.addAction(f"Qubit {i}")
                        action.setData(i)
                
                # Show the menu away from the cursor
                menu_pos = event.position().toPoint() + QPoint(15, 15)
                action = menu.exec(self.mapToGlobal(menu_pos))
                
                if action and action != title_action:
                    target_qubit = action.data()
                    # Add gate to circuit
                    if gate_type == "Toffoli":
                        # For Toffoli, we need a second control qubit
                        control2_menu = QMenu(self)
                        control2_menu.setStyleSheet(menu.styleSheet())
                        
                        # Add title for second menu
                        title2_action = QAction("Select second control qubit", self)
                        title2_action.setEnabled(False)
                        title2_action.setFont(font)
                        control2_menu.addAction(title2_action)
                        control2_menu.addSeparator()
                        
                        for i in range(self.scene.num_qubits):
                            if i != control_qubit and i != target_qubit:
                                action = control2_menu.addAction(f"Qubit {i}")
                                action.setData(i)
                        
                        action2 = control2_menu.exec(self.mapToGlobal(menu_pos + QPoint(10, 10)))
                        if action2 and action2 != title2_action:
                            control2_qubit = action2.data()
                            self.scene.add_gate(gate_type, [control_qubit, control2_qubit, target_qubit], None, time_step)
                    else:
                        self.scene.add_gate(gate_type, [control_qubit, target_qubit], None, time_step)
            elif gate_type == "Measure":
                # Measurement gate - call add_gate
                self.scene.add_gate(gate_type, [target_qubit], None, time_step)
                event.acceptProposedAction()
            else:
                # Single-qubit gate or custom gate
                if sequence:
                    # For custom gates, determine number of qubits and target qubits
                    num_qubits_needed = 1 # Default for now
                    try: 
                        # A basic check assuming sequence format is [(gate_type, [q_indices], params), ...]
                        max_q_index = 0
                        for op in sequence:
                            if len(op) >= 2 and isinstance(op[1], list):
                                max_q_index = max(max_q_index, max(op[1]))
                        num_qubits_needed = max_q_index + 1
                    except Exception as e:
                        print(f"Could not determine qubit count from sequence: {e}")
                        num_qubits_needed = 1 # Fallback
                    
                    target_qubits_list = list(range(target_qubit, target_qubit + num_qubits_needed))

                    if max(target_qubits_list) >= self.scene.num_qubits:
                        print("Custom gate requires too many qubits for this position.")
                        event.acceptProposedAction()
                        return
                    
                    # Pass sequence as params for custom gates
                    self.scene.add_gate(gate_type, target_qubits_list, {"sequence": sequence}, time_step)
                    event.acceptProposedAction()
                else:
                    # Standard single-qubit gate
                    self.scene.add_gate(gate_type, [target_qubit], params, time_step)
                    event.acceptProposedAction()
    
    def get_circuit(self):
        return self.scene.build_circuit()

class StateVectorDisplay(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Courier New", 10))
        self.display_mode = "ket"  # "ket" or "matrix"
    
    def update_state_vector(self, circuit):
        if circuit is None:
            self.setText("No valid circuit to display.")
            return
        
        try:
            # Get state vector representation
            state_repr = circuit.get_state_vector_representation()
            
            # Get measurement results
            measurements = circuit.get_measurement_results()
            
            # Get probability distribution
            probs = circuit.get_probability_distribution()
            
            # Build display text
            text = "State Vector:\n" + state_repr
            
            if probs:
                text += "\n\nProbability Distribution:\n"
                for state, prob in sorted(probs.items()):
                    text += f"|{state}⟩: {prob:.4f}\n"
            
            if measurements:
                text += "\nMeasurement Results:\n"
                for qubit, result in sorted(measurements.items()):
                    text += f"Qubit {qubit}: |{result}⟩\n"
            
            if circuit.classical_registers:
                text += "\nClassical Registers:\n"
                for reg, value in sorted(circuit.classical_registers.items()):
                    text += f"c[{reg}] = {value}\n"
            
            self.setText(text)
        except Exception as e:
            self.setText(f"Error calculating state vector: {str(e)}")

# Widget to edit OpenQASM code.
class QasmEditor(QTextEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Courier New", 10))

# Dialog for creating custom gates.
class CustomGateDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Define Custom Gate")
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit, QSpinBox, QTextEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
            }
            QSpinBox {
                min-width: 50px;
                text-align: center;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0;
                border: none;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Gate name input
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        form_layout.addRow("Gate Name:", self.name_input)
        
        # Qubit count control with + and - buttons
        qubit_control_widget = QWidget()
        qubit_control_layout = QHBoxLayout()
        qubit_control_layout.setContentsMargins(0, 0, 0, 0)
        qubit_control_layout.setSpacing(5)
        
        # Add decrease button
        decrease_button = QPushButton("-")
        decrease_button.setFixedSize(24, 24)
        decrease_button.clicked.connect(lambda: self.qubit_count.setValue(self.qubit_count.value() - 1))
        qubit_control_layout.addWidget(decrease_button)
        
        # Add spin box
        self.qubit_count = QSpinBox()
        self.qubit_count.setRange(1, 10)
        self.qubit_count.setValue(2)
        self.qubit_count.valueChanged.connect(self.update_placeholder)
        self.qubit_count.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)  # Hide the up/down arrows
        qubit_control_layout.addWidget(self.qubit_count)
        
        # Add increase button
        increase_button = QPushButton("+")
        increase_button.setFixedSize(24, 24)
        increase_button.clicked.connect(lambda: self.qubit_count.setValue(self.qubit_count.value() + 1))
        qubit_control_layout.addWidget(increase_button)
        
        qubit_control_widget.setLayout(qubit_control_layout)
        form_layout.addRow("Number of Qubits:", qubit_control_widget)
        
        layout.addLayout(form_layout)
        
        # Gate sequence editor
        layout.addWidget(QLabel("Gate Sequence (One gate per line, format: GATE q1,q2,...)"))
        self.sequence_editor = QTextEdit()
        self.sequence_editor.setPlaceholderText("Example:\nH 0\nCNOT 0,1\nX 1")
        layout.addWidget(self.sequence_editor)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_placeholder(self):
        # Update the placeholder text based on the number of qubits.
        num_qubits = self.qubit_count.value()
        example = f"H 0\nX 1\n"
        example += f"Rx(0.5*pi) 0\n"
        if num_qubits >= 2:
            example += f"CNOT 0,1\n"
        if num_qubits >= 3:
            example += f"Toffoli 0,1,2"
        self.sequence_editor.setPlaceholderText(example)
    
    def validate_and_accept(self):
        # Validate the input before accepting the dialog.
        name = self.name_input.text().strip()
        if not name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter a gate name.")
            return
        
        sequence_text = self.sequence_editor.toPlainText().strip()
        if not sequence_text:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter a gate sequence.")
            return
        
        try:
            sequence = self.parse_sequence(sequence_text)
            if not sequence:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Input", "No valid gates found in the sequence.")
                return
            self.accept()
        except ValueError as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", str(e))
    
    def parse_sequence(self, sequence_text: str) -> List[Tuple[str, List[int]]]:
        # Parse the gate sequence text into a list of (gate_type, qubits, params) tuples
        sequence = []
        num_qubits = self.qubit_count.value()
        
        for line in sequence_text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Handle parameterized gates like Rx(pi/2) 0
            params = None
            if '(' in line and ')' in line:
                # Extract parameter from format like "Rx(0.5*pi) 0"
                param_start = line.find('(')
                param_end = line.find(')')
                if param_start != -1 and param_end != -1 and param_start < param_end:
                    param_str = line[param_start+1:param_end].strip()
                    gate_type = line[:param_start].strip().upper()
                    
                    # Convert parameter string to value (supports pi constants)
                    try:
                        # Replace 'pi' with the value of pi for evaluation
                        param_str = param_str.replace('pi', str(np.pi))
                        param_value = float(eval(param_str))
                        params = [param_value]
                    except Exception as e:
                        raise ValueError(f"Error parsing parameter: {param_str}. {str(e)}")
                    
                    # Remaining part of the line contains qubit indices
                    remaining = line[param_end+1:].strip()
                    parts = remaining.split()
                    if not parts:
                        raise ValueError(f"Missing qubit indices after gate {gate_type}")
                    qubits_str = parts[0]
                else:
                    parts = line.split()
                    gate_type = parts[0].upper()
                    qubits_str = parts[1] if len(parts) > 1 else ""
            else:
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                gate_type = parts[0].upper()
                qubits_str = parts[1]
            
            if gate_type not in ["H", "T", "S", "X", "Y", "Z", "RX", "RY", "RZ", "P", "SWAP", "CNOT", "TOFFOLI"]:
                raise ValueError(f"Unsupported gate type: {gate_type}")
            
            try:
                qubits = [int(q) for q in qubits_str.split(",")]
                
                # Validate qubit indices
                for q in qubits:
                    if q < 0 or q >= num_qubits:
                        raise ValueError(f"Invalid qubit index: {q}. Must be between 0 and {num_qubits-1}")
                
                # Validate number of qubits for each gate type
                if gate_type in ["H", "T", "S", "X", "Y", "Z"] and len(qubits) != 1:
                    raise ValueError(f"{gate_type} gate requires exactly 1 qubit")
                elif gate_type in ["RX", "RY", "RZ", "P"] and len(qubits) != 1:
                    raise ValueError(f"{gate_type} gate requires exactly 1 qubit")
                elif gate_type in ["SWAP", "CNOT"] and len(qubits) != 2:
                    raise ValueError(f"{gate_type} gate requires exactly 2 qubits")
                elif gate_type == "TOFFOLI" and len(qubits) != 3:
                    raise ValueError("Toffoli gate requires exactly 3 qubits")
                
                # Require parameters for parameterized gates
                if gate_type in ["RX", "RY", "RZ", "P"] and not params:
                    raise ValueError(f"{gate_type} gate requires a parameter")
                
                sequence.append((gate_type, qubits, params))
            except ValueError as e:
                raise ValueError(f"Error parsing line '{line}': {str(e)}")
        
        return sequence
    
    def get_gate_definition(self):
        # Get the custom gate definition.
        name = self.name_input.text().strip()
        sequence_text = self.sequence_editor.toPlainText().strip()
        sequence = self.parse_sequence(sequence_text)
        return name, sequence

# Main window for the quantum circuit simulator.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.custom_gates_file = "custom_gates.json"  # File to store custom gates
        self.bloch_window = None  # Reference to the Bloch sphere window
        self.initUI()
        self.load_custom_gates()  # Load custom gates on startup
    
    def initUI(self):
        self.setWindowTitle("Qubox: Quantum Circuit Designer")
        self.setGeometry(100, 100, 1400, 900)  # Increased window size
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(32, 32))  # Larger icons
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                border-bottom: 1px solid #ddd;
                background-color: white;
                padding: 5px;
            }
            QToolButton {
                color: #333333;
            }
            QToolButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.addToolBar(toolbar)
        
        # Add actions to toolbar
        new_action = toolbar.addAction("New Circuit")
        new_action.triggered.connect(self.new_circuit)
        
        save_action = toolbar.addAction("Save Circuit")
        save_action.triggered.connect(self.save_circuit)
        
        load_action = toolbar.addAction("Load Circuit")
        load_action.triggered.connect(self.load_circuit)
        
        # Add qubit count control
        toolbar.addSeparator()
        qubit_label = QLabel("Number of Qubits:")
        qubit_label.setStyleSheet("margin-left: 10px; margin-right: 5px;")
        toolbar.addWidget(qubit_label)
        
        # Create a horizontal layout for qubit controls
        qubit_control_widget = QWidget()
        qubit_control_layout = QHBoxLayout()
        qubit_control_layout.setContentsMargins(0, 0, 0, 0)
        qubit_control_layout.setSpacing(5)
        
        # Add decrease button
        decrease_button = QPushButton("-")
        decrease_button.setFixedSize(24, 24)
        decrease_button.clicked.connect(lambda: qubit_count.setValue(qubit_count.value() - 1))
        qubit_control_layout.addWidget(decrease_button)
        
        # Add spin box
        qubit_count = QSpinBox()
        qubit_count.setRange(1, 10)
        qubit_count.setValue(3)  # Default to 3 qubits
        qubit_count.valueChanged.connect(self.set_num_qubits)
        qubit_count.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)  # Hide the up/down arrows
        qubit_count.setReadOnly(True)  # Make it read-only since we have + and - buttons
        qubit_count.setStyleSheet("""
            QSpinBox {
                min-width: 50px;
                max-width: 50px;
                padding: 2px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                text-align: center;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0;
                border: none;
            }
        """)
        qubit_control_layout.addWidget(qubit_count)
        
        # Add increase button
        increase_button = QPushButton("+")
        increase_button.setFixedSize(24, 24)
        increase_button.clicked.connect(lambda: qubit_count.setValue(qubit_count.value() + 1))
        qubit_control_layout.addWidget(increase_button)
        
        qubit_control_widget.setLayout(qubit_control_layout)
        toolbar.addWidget(qubit_control_widget)
        
        # Add initial state selector
        toolbar.addSeparator()
        state_label = QLabel("Initial State:")
        state_label.setStyleSheet("margin-left: 10px; margin-right: 5px;")
        toolbar.addWidget(state_label)
        
        self.state_selector = QComboBox()
        self.state_selector.addItems(["|0⟩", "|1⟩", "|+⟩", "|-⟩"])
        self.state_selector.setFixedWidth(80)
        self.state_selector.currentIndexChanged.connect(self.change_initial_state)
        toolbar.addWidget(self.state_selector)
        
        # Custom gate button
        toolbar.addSeparator()
        custom_gate_action = toolbar.addAction("Define Custom Gate")
        custom_gate_action.triggered.connect(self.define_custom_gate)
        
        # Bloch sphere visualization button
        toolbar.addSeparator()
        bloch_action = toolbar.addAction("Bloch Display")
        bloch_action.triggered.connect(self.show_bloch_sphere)

        # Add Help button to toolbar
        toolbar.addSeparator()
        help_action = toolbar.addAction("Help")
        help_action.triggered.connect(self.show_help)

        # Create splitter for main area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Add gate palette
        self.gate_palette = GatePalette()
        self.gate_palette.setMinimumWidth(180)  
        self.gate_palette.setMaximumWidth(200)  
        splitter.addWidget(self.gate_palette)
        
        # Add circuit view
        self.circuit_view = CircuitView()
        self.circuit_view.setMinimumWidth(600)  # Set minimum width
        self.circuit_view.circuit_changed.connect(self.update_state_vector)
        splitter.addWidget(self.circuit_view)
        
        # Create right panel with state vector display and QASM editor
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # State vector display
        state_vector_label = QLabel("State Vector:")
        state_vector_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        right_layout.addWidget(state_vector_label)
        
        self.state_vector_display = StateVectorDisplay()
        self.state_vector_display.setMinimumHeight(250)  # Increased height
        right_layout.addWidget(self.state_vector_display)
        
        # QASM editor
        qasm_label = QLabel("OpenQASM Code:")
        qasm_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        right_layout.addWidget(qasm_label)
        
        self.qasm_editor = QasmEditor()
        self.qasm_editor.setMinimumHeight(400)  # Increased height
        right_layout.addWidget(self.qasm_editor)
        
        # QASM buttons
        qasm_buttons = QHBoxLayout()
        qasm_buttons.setSpacing(10)
        
        update_circuit_button = QPushButton("Update Circuit from QASM")
        update_circuit_button.setStyleSheet("padding: 8px;")
        update_circuit_button.clicked.connect(self.update_circuit_from_qasm)
        
        update_qasm_button = QPushButton("Update QASM from Circuit")
        update_qasm_button.setStyleSheet("padding: 8px;")
        update_qasm_button.clicked.connect(self.update_qasm_from_circuit)
        
        qasm_buttons.addWidget(update_circuit_button)
        qasm_buttons.addWidget(update_qasm_button)
        right_layout.addLayout(qasm_buttons)
        
        right_panel.setLayout(right_layout)
        right_panel.setMinimumWidth(350)  # Increased minimum width
        right_panel.setMaximumWidth(400)  # Increased maximum width
        splitter.addWidget(right_panel)
        
        # Set splitter sizes for better initial proportions
        splitter.setSizes([200, 800, 400])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Set a modern style for the entire application
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                border-bottom: 1px solid #ddd;
                background-color: white;
                padding: 5px;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QToolBar QLabel {
                color: #333333;
            }
            QMenu {
                background-color: white;
                color: #333333;
            }
            QMenu::item {
                padding: 5px 15px;
                color: #333333;
            }
            QMenu::item:selected {
                background-color: #e9ecef;
            }
            QSplitter::handle {
                background-color: #ddd;
            }
            QScrollBar {
                background-color: #f5f5f5;
            }
            QScrollBar::handle {
                background-color: #ddd;
                border-radius: 4px;
            }
            QScrollBar::handle:hover {
                background-color: #ccc;
            }
            QGraphicsView {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QWidget#circuit_view {
                background-color: white;
            }
        """)
        
        # Update state vector
        self.update_state_vector()
    
    def update_state_vector(self):
        #Update the state vector display based on the current circuit.
        circuit = self.circuit_view.get_circuit()
        self.state_vector_display.update_state_vector(circuit)
        self.update_qasm_from_circuit()
    
    def update_qasm_from_circuit(self):
        #Update the QASM editor with code from the current circuit. 
        circuit = self.circuit_view.get_circuit()
        try:
            qasm_code = circuit.to_qasm()
            self.qasm_editor.setPlainText(qasm_code)
        except Exception as e:
            self.qasm_editor.setPlainText(f"Error generating QASM code: {str(e)}")
    
    def update_circuit_from_qasm(self):
        # Update the circuit based on the QASM code in the editor.
        qasm_code = self.qasm_editor.toPlainText()
        try:
            circuit = QuantumCircuit.from_qasm(qasm_code)
            
            # Store the number of qubits before clearing the scene
            num_qubits = circuit.num_qubits
            
            # Clear existing circuit and reinitialize with proper number of qubits
            self.circuit_view.scene.num_qubits = num_qubits
            self.circuit_view.scene.initialize_circuit()  # This recreates all wire objects
            
            # Set initial states after recreating wires
            for i, qubit in enumerate(circuit.qubits):
                if i < len(self.circuit_view.scene.qubit_wires):
                    if np.array_equal(qubit.state, Qubit.STATE_0):
                        self.circuit_view.scene.qubit_wires[i].state = "0"
                    elif np.array_equal(qubit.state, Qubit.STATE_1):
                        self.circuit_view.scene.qubit_wires[i].state = "1"
                    elif np.array_equal(qubit.state, Qubit.STATE_PLUS):
                        self.circuit_view.scene.qubit_wires[i].state = "+"
                    elif np.array_equal(qubit.state, Qubit.STATE_MINUS):
                        self.circuit_view.scene.qubit_wires[i].state = "-"
            
            # Add gates - FIXED VERSION: Don't specify time_step to allow optimal placement
            for gate_type, target_qubits, params in circuit.gates:
                # Let the scene's add_gate method determine the best time step
                self.circuit_view.scene.add_gate(gate_type, target_qubits, params)
            
            # Update the display size after all gates are added
            self.circuit_view.scene.update_display_size()
            self.circuit_view.scene.circuit_changed.emit()
        
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print detailed error info to console
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "QASM Error", f"Error parsing QASM code: {str(e)}")
    
    def set_num_qubits(self, num):
        # Set the number of qubits in the circuit.
        self.circuit_view.scene.num_qubits = num
        self.circuit_view.scene.initialize_circuit()
    
    def new_circuit(self):
        # Create a new empty circuit.
        self.circuit_view.scene.initialize_circuit()
    
    def save_circuit(self):
        # Save the circuit to a file.
        circuit = self.circuit_view.get_circuit()
        qasm_code = circuit.to_qasm()
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Circuit", "", "QASM Files (*.qasm);;All Files (*)")
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(qasm_code)
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Save Error", f"Error saving circuit: {str(e)}")
    
    def load_circuit(self):
        # Load a circuit from a file.
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Circuit", "", "QASM Files (*.qasm);;All Files (*)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    qasm_code = f.read()
                self.qasm_editor.setPlainText(qasm_code)
                self.update_circuit_from_qasm()
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Load Error", f"Error loading circuit: {str(e)}")
    
    def load_custom_gates(self):
        # Load custom gates from file.
        try:
            if os.path.exists(self.custom_gates_file):
                with open(self.custom_gates_file, 'r') as f:
                    custom_gates = json.load(f)
                    for name, sequence in custom_gates.items():
                        self.gate_palette.add_custom_gate(name, sequence)
        except Exception as e:
            print(f"Error loading custom gates: {e}")
    
    def save_custom_gates(self):
        # Save custom gates to file.
        try:
            custom_gates = self.gate_palette.custom_gates
            with open(self.custom_gates_file, 'w') as f:
                json.dump(custom_gates, f)
        except Exception as e:
            print(f"Error saving custom gates: {e}")
    
    def define_custom_gate(self):
        # Open dialog to define a custom gate.
        dialog = CustomGateDialog(self)
        if dialog.exec():
            name, sequence = dialog.get_gate_definition()
            if name and sequence:
                # Add custom gate to the circuit backend
                circuit = self.circuit_view.get_circuit()
                circuit.define_custom_gate(name, sequence)
                
                # Add custom gate to the gate palette
                self.gate_palette.add_custom_gate(name, sequence)
                
                # Save custom gates to file
                self.save_custom_gates()
                
                # Update QASM editor to show the custom gate definition
                self.update_qasm_from_circuit()
                
    def show_bloch_sphere(self):
        # Show the Bloch sphere visualization for the current circuit.
        # Get the current circuit
        circuit = self.circuit_view.get_circuit()
        
        if circuit.num_qubits == 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Qubits", "The circuit has no qubits to visualize.")
            return
        
        # Show qubit selector dialog
        selector = QubitSelectorDialog(self, circuit.num_qubits)
        if selector.exec():
            selected_qubits = selector.get_selected_qubits()
            
            # Create a window for the Bloch sphere if it doesn't exist
            if self.bloch_window is None or not self.bloch_window.isVisible():
                self.bloch_window = QDialog(self)
                self.bloch_window.setWindowTitle("Bloch Sphere Visualization")
                self.bloch_window.setMinimumSize(500, 500)
                
                # Create layout
                layout = QVBoxLayout()
                
                # Add Bloch sphere widget
                self.bloch_widget = BlochSphereWidget(self.bloch_window)
                layout.addWidget(self.bloch_widget)
                
                # Add button for updating the visualization
                update_button = QPushButton("Update Visualization")
                update_button.clicked.connect(lambda: self.update_bloch_visualization(selected_qubits))
                layout.addWidget(update_button)
                
                self.bloch_window.setLayout(layout)
            
            # Update the visualization with the selected qubits
            self.update_bloch_visualization(selected_qubits)
            
            # Show the window
            self.bloch_window.show()
            self.bloch_window.raise_()
    
    def update_bloch_visualization(self, selected_qubits=None):
        #Update the Bloch sphere visualization with the current circuit state."""
        if not hasattr(self, 'bloch_widget') or self.bloch_widget is None:
            return
        
        # Get the current circuit
        circuit = self.circuit_view.get_circuit()
        
        # Update the Bloch sphere
        self.bloch_widget.update_from_circuit(circuit, selected_qubits)
    
    def change_initial_state(self, index):
        state_map = {0: "0", 1: "1", 2: "+", 3: "-"}
        new_state = state_map[index]
        # Update all selected qubits or the most recently clicked qubit
        scene = self.circuit_view.scene
        selected_wires = [item for item in scene.selectedItems() if isinstance(item, QubitWireGraphicsItem)]
        
        if selected_wires:
            # Update selected wires
            for wire in selected_wires:
                wire.state = new_state
                wire.update()
        else:
            # If no selection, update the last clicked wire if any
            for wire in scene.qubit_wires:
                if wire.isUnderMouse():
                    wire.state = new_state
                    wire.update()
                    break
        
        scene.circuit_changed.emit()
    
    def closeEvent(self, event):
        # Handle application close event.
        # Delete the custom_gates.json file if it exists instead of saving
        if os.path.exists(self.custom_gates_file):
            try:
                os.remove(self.custom_gates_file)
                print(f"Removed custom gates file on exit: {self.custom_gates_file}")
            except Exception as e:
                print(f"Error removing custom gates file: {e}")
        
        super().closeEvent(event)
    
    def resizeEvent(self, event):
        # Override the standard resize event to update the circuit view.
        super().resizeEvent(event)
        self.circuit_view.scene.update_display_size()

    # Add this method to the MainWindow class
    def show_help(self):
        dialog = HelpDialog(self)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()