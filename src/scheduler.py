
from enum import Enum, EnumMeta

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QHBoxLayout, QGridLayout, QFileDialog, QPushButton
from PyQt5.QtGui import QMouseEvent
from PyQt5 import QtCore

UIState = Enum('UIState', 'MENTORS COMPANIES AVAILABILITY MENTOR_ASSIGNMENT AMBIGUITIES FINISHED')
class UIWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.set_state(UIState.MENTORS)
    def set_state(self, state):
        if not isinstance(state, UIState):
            print("Invalid state, exiting")
            exit(-1)
        elif state is UIState.MENTORS:
            window_layout = QGridLayout()
            self.setLayout(window_layout)
            label = QLabel("Step 1/6: Mentor list\nInput a newline-separated list of all attending mentors")
            label.setAlignment(QtCore.Qt.AlignCenter)
            window_layout.addWidget(label, 0, 0, 0, 10)

            buttons = QWidget()
            button_layout = QHBoxLayout()
            buttons.setLayout(button_layout)
            window_layout.addWidget(buttons, 10,0, 1, 10)
            
            files = QLabel("Select file")
            files.setAlignment(QtCore.Qt.AlignHCenter)
            files.mousePressEvent = (lambda _: files.setText(QFileDialog.getOpenFileName(self, "Select mentors file")[0]))
            button_layout.addWidget(files)

            next = QPushButton("Next")
            next.mousePressEvent = (lambda _: self.set_state(UIState.COMPANIES))
            button_layout.addWidget(next)
        elif state is UIState.COMPANIES:
            pass
        elif state is UIState.AVAILABILITY:
            pass
        elif state is MENTOR_ASSIGNMENT:
            pass
        elif state is AMBIGUITIES:
            pass
        else:
            pass

application = QApplication([])
ui = UIWidget()
window = QMainWindow()

window.resize(800, 600)
window.setCentralWidget(ui)
window.show()

application.exec()