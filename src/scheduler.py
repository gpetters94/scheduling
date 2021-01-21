
from enum import Enum, EnumMeta

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QHBoxLayout, QGridLayout, QFileDialog, QPushButton
from PyQt5.QtGui import QMouseEvent
from PyQt5 import QtCore

def detect_collisions(mentors, companies, assignments):
    pass

UIState = Enum('UIState', 'MENTORS COMPANIES AVAILABILITY MENTOR_ASSIGNMENT FINISHED')
class UIWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        QHBoxLayout(self)
        self.set_state(UIState.MENTORS)
    def clear(self):
        child = self.layout().takeAt(0)
        if child is not None:
            child.widget().setParent(None)
    def import_mentors(self, filename):
        if filename != "" and filename != "Select file":
            self.mentors = {}

            with open(filename) as f:
                for line in f:
                   line = line.strip()
                   if line != "":
                        self.mentors[line] = None

            if self.mentors == {}:
                print("Error: no mentors provided")
                exit(-1)

            self.set_state(UIState.COMPANIES)
    def import_companies(self, filename):
        if filename != "" and filename != "Select file":
            self.companies = []

            with open(filename) as f:
                for line in f:
                   line = line.strip()
                   if line != "":
                        self.companies.append(line)

            if self.companies == []:
                print("Error: no companies provided")
                exit(-1)

            self.set_state(UIState.AVAILABILITY)
    def set_state(self, state):
        if not isinstance(state, UIState):
            print("Invalid state, exiting")
            exit(-1)
        elif state is UIState.MENTORS:
            self.clear()

            central = QWidget()
            self.layout().addWidget(central)
            
            window_layout = QGridLayout()
            central.setLayout(window_layout)

            label = QLabel("Step 1/6: Mentor list\nInput a newline-separated list of all attending mentors")
            label.setAlignment(QtCore.Qt.AlignCenter)
            window_layout.addWidget(label, 0, 0, 0, 10)

            buttons = QWidget()
            button_layout = QHBoxLayout()
            buttons.setLayout(button_layout)
            window_layout.addWidget(buttons, 10,0, 1, 10)

            files = QLabel("Select file")
            updated = False

            def set_text(val):
                if val != "" and val != "Select file":
                    files.setText(val)
                    updated = True

            files.setAlignment(QtCore.Qt.AlignHCenter)
            files.mousePressEvent = (lambda _: set_text(QFileDialog.getOpenFileName(self, "Select mentors file")[0]))
            button_layout.addWidget(files)

            next = QPushButton("Next")
            next.mousePressEvent = (lambda _: self.import_mentors(files.text()))
            button_layout.addWidget(next)
        elif state is UIState.COMPANIES:
            self.clear()

            central = QWidget()
            self.layout().addWidget(central)
            
            window_layout = QGridLayout()
            central.setLayout(window_layout)

            label = QLabel("Step 2/6: Companies list\nInput a newline-separated list of all companies taking part")
            label.setAlignment(QtCore.Qt.AlignCenter)
            window_layout.addWidget(label, 0, 0, 0, 10)

            buttons = QWidget()
            button_layout = QHBoxLayout()
            buttons.setLayout(button_layout)
            window_layout.addWidget(buttons, 10,0, 1, 10)

            files = QLabel("Select file")
            updated = False

            def set_text(val):
                if val != "" and val != "Select file":
                    files.setText(val)
                    updated = True

            files.setAlignment(QtCore.Qt.AlignHCenter)
            files.mousePressEvent = (lambda _: set_text(QFileDialog.getOpenFileName(self, "Select companies file")[0]))
            button_layout.addWidget(files)

            next = QPushButton("Next")
            next.mousePressEvent = (lambda _: self.import_companies(files.text()))
            button_layout.addWidget(next)
        elif state is UIState.AVAILABILITY:
            self.clear()

            for mentor in self.mentors.keys():
                central = QWidget()
                self.layout().addWidget(central)
            
                window_layout = QGridLayout()
                central.setLayout(window_layout)

                self.clear()
        elif state is MENTOR_ASSIGNMENT:
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