import sys
from PySide2 import QtGui, QtCore
import networkx as nx
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget,QDesktopWidget,QGridLayout,QSplitter)
from PySide2.QtCore import Slot, qApp
import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
from debuggo.solve.solver import SolveRunner
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class Color(QWidget):
    """Just for prototyping purposes"""

    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
        self.setPalette(palette)
class PrettyWidget(QWidget):
    def __init__(self, graph):
        super(PrettyWidget, self).__init__()
        self.initUI()
        self.G = graph

    def initUI(self):

        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('Graph')

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
        ax2 = self.figure.add_subplot(111)
        nx.draw(self.G, ax=ax2)
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


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Debuggo")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Data loaded and plotted")

        # Window dimensions
        # geometry = qApp.desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)

        leftWidget = Color('red')
        topRight = Color('green')
        bottomRight = Color('yellow')
        rightSplitter = QSplitter(QtCore.Qt.Vertical)
        rightSplitter.addWidget(topRight)
        rightSplitter.addWidget(bottomRight)
        rightStack = QVBoxLayout()
        rightStack.addWidget(rightSplitter)

        horizontalStack = QHBoxLayout()
        horizontalSplitter = QSplitter(QtCore.Qt.Horizontal)
        horizontalSplitter.addWidget(leftWidget)
        horizontalSplitter.addWidget(rightSplitter)
        horizontalSplitter.setStretchFactor(1, 1)
        horizontalSplitter.setSizes([1200, 200])

        self.setGeometry(300, 300, 1400, 800)
        
        self.setCentralWidget(horizontalSplitter)


    @Slot()
    def exit_app(self, checked):
        sys.exit()

# def createWidgets(self):
#     topFrame = tk.Frame(self)
#     buttonFrame = tk.Frame(self)
#     bottomFrame = tk.Frame(self)

#     topFrame.pack(side="top", fill="both", expand=True)
#     buttonFrame.pack(side="top", fill="x")
#     bottomFrame.pack(side="bottom", fill="both", expand=True)

#     listBox = tk.Listbox(topFrame, width=30)
#     listBox.pack(side="top", fill="both", expand=True)

#     tk.Button(buttonFrame, text="Add").pack(side="left")
#     tk.Button(buttonFrame, text="Remove").pack(side="left")
#     tk.Button(buttonFrame, text="Edit").pack(side="left")

#     textBox = tk.Text(bottomFrame, height=10, width=30)
#     textBox.pack(fill="both", expand=True)
if __name__ == "__main__":
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    sr = SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    G = sr.graph
    app = QApplication(sys.argv)
        
    layout = QHBoxLayout() 
    w = QLabel("This is the main view")
    # QWidget
    
    # QMainWindow using QWidget as central widget
    window = MainWindow(w)

    window.show()
    sys.exit(app.exec_())