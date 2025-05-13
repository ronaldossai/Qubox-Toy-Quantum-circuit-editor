import sys
from PyQt6.QtWidgets import QApplication
from CircuitBackend import QuantumCircuit, Qubit
from CircuitUI import MainWindow
from QuboxWelcome import QuboxWelcome  

# Start program
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the welcome popup before launching the main window
    QuboxWelcome.show_welcome()

    # Now launch the main application window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
