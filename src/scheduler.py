
'''
This file contains all the logic necessary for scheduling the mentor/company meetings.
It does so by first walking through the list of already-booked mentors, assigning times
and validating the schedule.
After doing so, it walks the list of non-booked mentors and assigning them days and shifts.
The software also validates the total schedule at every step of this process, before finally
outputting a CSV-formatted schedule named 'output.csv'.

Initially, my solution was much more stochastic. The step_1 and step_2 functions, which I had
named 'monte_carlo_1' and 'monte_carlo_2', assigned random values at each step. I designed the
program this way initially because I assumed this would be an NP-Complete problem, and my experience
in an AI class made me assume that the Monte Carlo method would work best here.

My Monte Carlo solution was getting results, but it was doing so after millions of permutations.
Just to see, I replaced the first step with a deterministic algorithm and was shocked to find that
it was outperforming my initial code by several orders of magnitude. I suspect this is because I
overestimated the complexity of the problem at hand. Looking at the problem more closely, I
think it is probably O(n**3) instead of the O(2**n) I assumed at first.

I opted to use Qt5 because it is the GUI framework I know best. Python is the easiest way to write
Qt code, in my experience - C++ is too slow to prototype and the other language bindings aren't
nearly as mature. I was initially going to make this a CLI program, but I decided that a simple
GUI would be both more straightforward both to code and use. I'm not sure I was right on the first
count, but I definitely don't think a CLI I would make would have the simplicity that this GUI does.
'''

from enum import Enum
from random import randint, shuffle
import sys
import csv

from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QLabel, QHBoxLayout,
    QGridLayout, QFileDialog, QPushButton, QGroupBox, QComboBox, QCheckBox)
from PyQt5 import QtCore

from flowlayout import FlowLayout

def is_valid(schedule):
    '''
    Validates a given schedule
    Input:
        schedule: of the form {(mentor, company, (day, time)) ...}
    Output:
        True if the schedule is valid (i.e. there are no conflicts), False otherwise
    '''
    mentor_schedules = {}
    company_schedules = {}
    for (mentor, company, (day, time)) in schedule:
        if mentor not in mentor_schedules and company not in company_schedules:
            mentor_schedules[mentor] = [(day, time)]
            company_schedules[company] = [(day, time)]
            continue
        if mentor not in mentor_schedules:
            mentor_schedules[mentor] = []
        if company not in company_schedules:
            company_schedules[company] = []

        if (day, time) in company_schedules[company] or (day, time) in mentor_schedules[mentor]:
            return False
        else:
            mentor_schedules[mentor].append((day, time))
            company_schedules[company].append((day, time))
    return True

# def possible_collisions(mentors, companies, m_times, c_mentors):
#     '''
#     Filters out possible collisions, to simplify the scheduling process
#     Inputs:
#         mentors: [mentor ...]
#         companies: [company ...]
#         m_times: {mentor: (day, time) ...}
#         c_mentors: {company: [mentor ...] ...}
#     Output:
#         possible collisions in the form {(mentor, company, (day, time)) ...}
#    '''
#     conflicts = set()
#     seen = {}
    
#     for company in companies:
#         for mentor in mentors:
#             if mentor not in c_mentors[company]:
#                 continue
#             time = m_times[mentor]
#             if time in seen and company in seen[time]:
#                 conflicts.add((mentor, company, time))
#                 for other_mentor in seen[time][company]:
#                     conflicts.add((other_mentor, company, time))
#             if time not in seen:
#                 seen[time] = {}
#             if company not in seen[time]:
#                 seen[time][company] = []
#             seen[time][company].append(mentor)

#     return conflicts

def step_1(matrix):
    '''
    Steps through the proto-schedule, assigning times to each mentor/company pair,
    checking for collisions at every step.
    Input:
        matrix: {(mentor, company, (day, time)) ...}
    output:
        The previous but with numerical times {(mentor, company, (day, time)) ...},
            or None if no valid schedule is found
    '''

    # Turn AM/PM and an offset to an actual time
    def deterministic_time(time, i):
        if time == "AM":
            return (9 + int(i/3), i%3*20)
        else:
            return (12 + int(i/3), i%3*20)

    for _ in range(len(matrix)**2*2):
        schedule = set()
        matrix = list(matrix)
        shuffle(matrix)
        for (mentor, company, (day, time)) in matrix:
            for j in range(8):
                new_time = deterministic_time(time, j)
                schedule.add((mentor, company, (day, new_time)))
                if not is_valid(schedule):
                    schedule.remove((mentor, company, (day, new_time)))
                    continue
                else:
                    break

        if is_valid(schedule):
            return schedule

    return None

# Returns a set of (mentor, company, (day, time)) or None for the unscheduled mentors
def step_2(unassigned, m_to_c, proto_schedule):
    '''
    Randomly assigns dates and times to the unscheduled mentors, adding the results to
    the existing schedule and ensuring that is valid each step of the way
    Inputs:
        unassigned: {mentor ...}
        m_to_c: {mentor: [company ...] ...}
        proto_schedule: {(mentor, company, (day, time)) ...}
    '''

    def random_assignment():
        return ["AM", "PM"][randint(0, 1)]

    def random_day():
        return randint(1,5)

    def deterministic_time(time, i):
        if time == "AM":
            return (9 + int(i/3), i%3*20)
        else:
            return (12 + int(i/3), i%3*20)

    for _ in range(len(unassigned)**2*2):

        times = {}
        for mentor in unassigned:
            times[mentor] = (random_day(), random_assignment())

        assignments = set()
        for (mentor, company) in m_to_c:
            def run_simulation():
                for j in range(9):
                    entry = (mentor, company, (times[mentor][0],
                        deterministic_time(times[mentor][1], j)))
                    assignments.add(entry)
                    if not is_valid(assignments.union(proto_schedule)):
                        if j < 8:
                            assignments.remove(entry)
                            continue
                        return False
                    return True
            if run_simulation():
                continue
            break

        if is_valid(assignments.union(proto_schedule)):
            return assignments.union(proto_schedule)
        continue

    return None

UIState = Enum('UIState', 'MENTORS COMPANIES AVAILABILITY MENTOR_ASSIGNMENT FINISHED')
class UIWidget(QWidget):
    '''
    Container widget, handles user input and contains much of the scheduling logic
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        QHBoxLayout(self)
        self.mentors = {}
        self.companies = []
        self.set_state(UIState.MENTORS)
    def clear(self):
        '''
        Removes child widgets, used when switching between states
        '''
        child = self.layout().takeAt(0)
        if child is not None:
            child.widget().setParent(None)
    def import_mentors(self, filename):
        '''
        Imports mentors from mentor file (a newline-delimited text file), then steps to state 2
        Inputs:
            filename: name of the mentor file
        '''
        if filename != "" and filename != "Select file":

            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if line != "":
                        self.mentors[line] = None

            if self.mentors == {}:
                print("Error: no mentors provided")
                sys.exit(-1)

            self.set_state(UIState.COMPANIES)
    def import_companies(self, filename):
        '''
        Imports companies from company file (a newline-delimited text file), then steps to state 3
        Inputs:
            filename: name of the company file
        '''
        if filename != "" and filename != "Select file":

            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if line != "":
                        self.companies.append(line)

            if self.companies == []:
                print("Error: no companies provided")
                sys.exit(-1)

            self.set_state(UIState.AVAILABILITY)
    def schedule_logic(self):
        '''
        The function where most of the scheduling logic takes place
        Arranges data, calls step_1 and step_2, then writes to the output file
        '''

        assigned = {}
        unassigned = set()
        for mentor in self.mentors:
            (day, time) = self.mentors[mentor]
            if day is None or time is None:
                unassigned.add(mentor)
            else:
                assigned[mentor] = (day, time)

        assigned_schedule = set()
        unassigned_schedule = set()
        for company in self.company_assignments:
            mentors = self.company_assignments[company]
            for mentor in mentors:
                if mentor in assigned:
                    assigned_schedule.add((mentor, company, assigned[mentor]))
                else:
                    unassigned_schedule.add((mentor, company))

        part_1 = step_1(assigned_schedule)
        if part_1 is None:
            print("No solution found")
            sys.exit(0)

        part_2 = step_2(unassigned, unassigned_schedule, part_1)
        if part_2 is None:
            print("No solution found")
            sys.exit(0)

        output = {}
        for (mentor, company, (day, time)) in part_2:
            if mentor not in output:
                output[mentor] = []
            output[mentor].append(((day, time), company))
        for mentor in output:
            output[mentor].sort()

        def format_day(day):
            return ["Mon", "Tue", "Wed", "Thur", "Fri"][day-1]
        def format_time(time):
            h = time[0]
            m = time[1]
            return (("{0}".format(h) if h <= 12 else "{0}".format(h-12)) +
                ":" + "{0:02}".format(m) + (" PM" if h >= 12 else " AM"))

        with open('output.csv', 'w') as f:
            out = csv.writer(f, delimiter=",")
            out.writerow(['Name', 'Day'] + 
                ["Meeting {}".format(x+1) for x in range(len(self.companies))])
            for mentor in sorted(output.keys()):
                out_list = [mentor]
                first = True
                for ((day, time), company) in output[mentor]:
                    if first:
                        out_list += [format_day(day)]
                        first = False
                    out_list += [format_time(time) + ": " + company]
                out.writerow(out_list)

        sys.exit(0)

    def set_state(self, state):
        '''
        Handles most of the input logic, specifically that
        which requires user input
        '''
        if not isinstance(state, UIState):
            print("Invalid state, exiting")
            sys.exit(-1)
        elif state is UIState.MENTORS:
            self.clear()

            central = QWidget()
            self.layout().addWidget(central)

            window_layout = QGridLayout()
            central.setLayout(window_layout)

            label = QLabel("Step 1/4: Mentor list\n"+
                "Input a newline-separated list of all attending mentors")
            label.setAlignment(QtCore.Qt.AlignCenter)
            window_layout.addWidget(label, 0, 0, 0, 10)

            buttons = QWidget()
            button_layout = QHBoxLayout()
            buttons.setLayout(button_layout)
            window_layout.addWidget(buttons, 10,0, 1, 10)

            files = QLabel("Select file")

            def set_text(val):
                if val != "" and val != "Select file":
                    files.setText(val)

            files.setAlignment(QtCore.Qt.AlignHCenter)
            files.mousePressEvent = (lambda _:
                set_text(QFileDialog.getOpenFileName(self, "Select mentors file")[0]))
            button_layout.addWidget(files)

            next_button = QPushButton("Next")
            next_button.mousePressEvent = (lambda _: self.import_mentors(files.text()))
            button_layout.addWidget(next_button)
        elif state is UIState.COMPANIES:
            self.clear()

            central = QWidget()
            self.layout().addWidget(central)

            window_layout = QGridLayout()
            central.setLayout(window_layout)

            label = QLabel("Step 2/4: Companies list\n"+
                "Input a newline-separated list of all companies taking part")
            label.setAlignment(QtCore.Qt.AlignCenter)
            window_layout.addWidget(label, 0, 0, 0, 10)

            buttons = QWidget()
            button_layout = QHBoxLayout()
            buttons.setLayout(button_layout)
            window_layout.addWidget(buttons, 10,0, 1, 10)

            files = QLabel("Select file")

            def set_text(val):
                if val != "" and val != "Select file":
                    files.setText(val)

            files.setAlignment(QtCore.Qt.AlignHCenter)
            files.mousePressEvent = (lambda _: set_text(QFileDialog.getOpenFileName(self,
                "Select companies file")[0]))
            button_layout.addWidget(files)

            next_button = QPushButton("Next")
            next_button.mousePressEvent = (lambda _: self.import_companies(files.text()))
            button_layout.addWidget(next_button)
        elif state is UIState.AVAILABILITY:
            self.clear()

            daytonum = {"Monday": 1, "Tuesday": 2, "Wednesday": 3,
                "Thursday": 4, "Friday": 5, "Undefined": None}

            if "csv_file" in dir(self) and self.csv_file is not None:
                with open(self.csv_file, newline='\n') as f:
                    reader = csv.reader(f, delimiter=',')
                    self.company_assignments = {company: set() for company in self.companies}
                    first = True
                    for row in reader:
                        if first:
                            first = False
                            continue
                        mentor = row[0].strip()
                        (day, time) = (row[1].strip(), row[2].strip())
                        companies = [x.strip() for x in row[3:] if x != '']

                        self.mentors[mentor] = ((None if day == "Undefined" or
                            time == "Undefined" else daytonum[day]),
                            (None if time == "Undefined" or day == "Undefined" else time))
                        for company in companies:
                            self.company_assignments[company].add(mentor)
                self.schedule_logic()

            count = 0
            total = len(self.mentors)
            for mentor in self.mentors:
                count += 1
                central = QWidget()
                self.layout().addWidget(central)

                central.setLayout(QGridLayout(central))

                msg = QLabel("Step 3/4: Please choose availability for {0} ({1}/{2})"
                    .format(mentor, count, total))
                msg.setAlignment(QtCore.Qt.AlignCenter)
                central.layout().addWidget(msg, 0, 0, 10, 10)

                selection = QWidget()
                QHBoxLayout(selection)

                dropdowns = QWidget()
                QHBoxLayout(dropdowns)
                selection.layout().addWidget(dropdowns)

                day = QComboBox()
                day.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Undefined"])
                dropdowns.layout().addWidget(day)

                time = QComboBox()
                time.addItems(["AM", "PM", "Undefined"])
                dropdowns.layout().addWidget(time)

                next_button = QPushButton("Next")
                selection.layout().addWidget(next_button)

                central.layout().addWidget(selection, 10, 0, 1, 10)

                wait = QtCore.QEventLoop()
                def exit_loop():
                    self.mentors[mentor] = ((None if time.currentText() == "Undefined" or 
                        day.currentText() == "Undefined" else daytonum[day.currentText()]),
                        (None if time.currentText() == "Undefined" or 
                        day.currentText() == "Undefined" else time.currentText()))
                    wait.quit()
                next_button.pressed.connect(exit_loop)
                wait.exec()

                self.clear()
            self.set_state(UIState.MENTOR_ASSIGNMENT)
        elif state is UIState.MENTOR_ASSIGNMENT:
            self.clear()

            self.company_assignments = {company: set() for company in self.companies}
            count = 0
            total = len(self.mentors.keys())
            for mentor in self.mentors:
                count += 1
                central = QWidget()
                self.layout().addWidget(central)

                central.setLayout(QGridLayout(central))

                msg = QLabel("Step 4/4: Please choose companies assigned to {0} ({1}/{2})"
                    .format(mentor, count, total))
                msg.setAlignment(QtCore.Qt.AlignCenter)
                central.layout().addWidget(msg, 0, 0, 10, 10)

                selection = QWidget()
                QHBoxLayout(selection)

                buttons = QGroupBox()
                buttons.setLayout(FlowLayout())
                for company in self.companies:
                    button = QCheckBox(company)
                    buttons.layout().addWidget(button)
                selection.layout().addWidget(buttons)

                next_button = QPushButton("Next")
                selection.layout().addWidget(next_button)

                central.layout().addWidget(selection, 10, 0, 1, 10)

                wait = QtCore.QEventLoop()
                def exit_loop():
                    # Loop through all check buttons, adding to the assignments
                    for item in buttons.children():
                        if isinstance(item, QCheckBox) and item.isChecked():
                            self.company_assignments[item.text()].add(mentor)
                    wait.quit()
                next_button.pressed.connect(exit_loop)
                wait.exec()

                self.clear()
            self.set_state(UIState.FINISHED)
        else:
            self.schedule_logic()

if __name__ == "__main__":
    application = QApplication([])
    ui = UIWidget()
    window = QMainWindow()

    if len(sys.argv) > 1:
        ui.csv_file = sys.argv[1]

    window.resize(800, 600)
    window.setCentralWidget(ui)
    window.show()

    application.exec()
