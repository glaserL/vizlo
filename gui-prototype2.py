import sys
from PySide2 import QtGui
import networkx as nx
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget,QDesktopWidget,QGridLayout)
import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
from debuggo.solve.solver import SolveRunner
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class PrettyWidget(QWidget):
    def __init__(self, graph):
        super(PrettyWidget, self).__init__()
        self.initUI()
        self.G = graph

    def initUI(self):

        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('S Plot')

        grid = QGridLayout()
        self.setLayout(grid)

        btn1 = QPushButton('Plot 1 ', self)
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.plot1)
        grid.addWidget(btn1, 5, 0)

        btn2 = QPushButton('Plot 2 ', self)
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.plot2)
        grid.addWidget(btn2, 5, 1)

        self.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid.addWidget(self.canvas, 3, 0, 1, 2)
        # grid.addWidget(self.toolbar, ??)

        self.show()

    def plot1(self):
        self.figure.clf()
        plt.subplots(1)
        nx.draw(self.G)
        plt.show()
        print("Drawing..")
        self.canvas.draw_idle()

    def plot2(self):
        self.figure.clf()
        ax3 = self.figure.add_subplot(111)
        x = [i for i in range(100)]
        y = [i**0.5 for i in x]
        ax3.plot(x, y, 'r.-')
        ax3.set_title('Square Root Plot')
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
    reified_program = "".join(f.readlines())
sr = SolveRunner(reified_program)
for _ in range(5):
    print(".",end="")
    sr.step()
G = sr.graph
app = QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
GUI = PrettyWidget(G)
sys.exit(app.exec_())