
import sys
from debuggo.solver import SolveRunner
import networkx as nx
from PySide2.QtWidgets import (QApplication, QHeaderView, QMainWindow, QPushButton, QWidget, QDesktopWidget)
from PySide2.QtCharts import QtCharts
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib as mpl

class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Debuggo")
        self.setCentralWidget(widget)


class Widget(QWidget):
    def __init__(self, networkx_graph):
        QWidget.__init__(self)
        self.figure = mpl.figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.center()
        self.G = networkx_graph
        self.show()

    def draw(self):
        print("Drawing..")
        self.figure.clf()
        G = self.G
        print(f"Graph of size {len(G)}")
        nx.draw(G, with_labels=True)
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def plot1(self):
        self.figure.clf()
        ax1 = self.figure.add_subplot(211)
        x1 = [i for i in range(100)]
        y1 = [i**0.5 for i in x1]
        ax1.plot(x1, y1, 'b.-')

if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)

    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    sr = SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    G = sr.graph
    widget = Widget(G)
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    widget.draw()
    window.resize(800, 600)
    window.show()
    widget.plot1()

    # Execute application
    sys.exit(app.exec_())
