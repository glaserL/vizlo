import sys
from PySide2 import QtGui, QtCore
import networkx as nx
from PySide2.QtWidgets import (QAction, QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,QGraphicsItem,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QStyle,QGraphicsScene,QGraphicsEllipseItem,
                               QVBoxLayout, QWidget,QDesktopWidget,QGridLayout,QSplitter, QListWidget,QGraphicsView)
from PySide2.QtCore import Slot, qApp
import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
from debuggo.solve.solver import SolveRunner
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import math


class Edge(QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super(Edge, self).__init__()

        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()

        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source

    def setSourceNode(self, node):
        self.source = node
        self.adjust()

    def destNode(self):
        return self.dest

    def setDestNode(self, node):
        self.dest = node
        self.adjust()

    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0),
                self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            edgeOffset = QtCore.QPointF((line.dx() * 10) / length,
                    (line.dy() * 10) / length)

            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = line.p1()
            self.destPoint = line.p1()

    def boundingRect(self):
        if not self.source or not self.dest:
            return QtCore.QRectF()

        penWidth = 1.0
        extra = (penWidth + self.arrowSize) / 2.0

        return QtCore.QRectF(self.sourcePoint,
                QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                        self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Edge.TwoPi - angle

        sourceArrowP1 = self.sourcePoint + QtCore.QPointF(math.sin(angle + Edge.Pi / 3) * self.arrowSize,
                                                          math.cos(angle + Edge.Pi / 3) * self.arrowSize)
        sourceArrowP2 = self.sourcePoint + QtCore.QPointF(math.sin(angle + Edge.Pi - Edge.Pi / 3) * self.arrowSize,
                                                          math.cos(angle + Edge.Pi - Edge.Pi / 3) * self.arrowSize);   
        destArrowP1 = self.destPoint + QtCore.QPointF(math.sin(angle - Edge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - Edge.Pi / 3) * self.arrowSize)
        destArrowP2 = self.destPoint + QtCore.QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)

        painter.setBrush(QtCore.Qt.black)
        painter.drawPolygon(QtGui.QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        painter.drawPolygon(QtGui.QPolygonF([line.p2(), destArrowP1, destArrowP2]))

class Color(QWidget):
    """Just for prototyping purposes"""

    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
        self.setPalette(palette)
# class PrettyWidget(QWidget):
#     def __init__(self, graph):
#         super(PrettyWidget, self).__init__()
#         self.initUI()
#         self.G = graph

#     def initUI(self):

#         self.setGeometry(100, 100, 800, 600)
#         self.center()
#         self.setWindowTitle('Graph')

#         grid = QGridLayout()
#         self.setLayout(grid)

#         btn1 = QPushButton('Plot 1 ', self)
#         btn1.resize(btn1.sizeHint())
#         btn1.clicked.connect(self.plot1)
#         grid.addWidget(btn1, 5, 0)

#         btn2 = QPushButton('Plot 2 ', self)
#         btn2.resize(btn2.sizeHint())
#         btn2.clicked.connect(self.plot2)
#         grid.addWidget(btn2, 5, 1)

#         self.figure = matplotlib.figure.Figure()
#         self.canvas = FigureCanvas(self.figure)
#         self.toolbar = NavigationToolbar(self.canvas, self)
#         grid.addWidget(self.canvas, 3, 0, 1, 2)
#         # grid.addWidget(self.toolbar, ??)

#         self.show()

#     def plot1(self):
#         self.figure.clf()
#         ax2 = self.figure.add_subplot(111)
#         nx.draw(self.G, ax=ax2)
#         print("Drawing..")
#         self.canvas.draw_idle()

#     def plot2(self):
#         self.figure.clf()
#         ax3 = self.figure.add_subplot(111)
#         x = [i for i in range(100)]
#         y = [i**0.5 for i in x]
#         ax3.plot(x, y, 'r.-')
#         ax3.set_title('Square Root Plot')
#         self.canvas.draw_idle()

#     def center(self):
#         qr = self.frameGeometry()
#         cp = QDesktopWidget().availableGeometry().center()
#         qr.moveCenter(cp)
#         self.move(qr.topLeft())


class MainWindow(QMainWindow):
    def __init__(self, leftWidget):
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

        topRight = Color('green')
        bottomRight = Color('yellow')
        rightSplitter = QSplitter(QtCore.Qt.Vertical)
        listWidget = self.createListWidget(leftWidget.graph)
        rightSplitter.addWidget(listWidget)
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

    def createListWidget(self, graph):
        listWidget = QListWidget()
        listWidget.setAlternatingRowColor = True
        for node in graph:
            listWidget.addItem(str(node))
        return listWidget

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

class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, graphWidget, name="N/A"):
        super(Node, self).__init__()
        self.name = name
        self.graph = graphWidget
        self.edgeList = []
        self.newPos = QtCore.QPointF()

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)

    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList

    # def calculateForces(self):
    #     if not self.scene() or self.scene().mouseGrabberItem() is self:
    #         self.newPos = self.pos()
    #         return
    
    #     # Sum up all forces pushing this item away.
    #     xvel = 0.0
    #     yvel = 0.0
    #     for item in self.scene().items():
    #         if not isinstance(item, Node):
    #             continue

    #         line = QtCore.QLineF(self.mapFromItem(item, 0, 0),
    #                 QtCore.QPointF(0, 0))
    #         dx = line.dx()
    #         dy = line.dy()
    #         l = 2.0 * (dx * dx + dy * dy)
    #         if l > 0:
    #             xvel += (dx * 150.0) / l
    #             yvel += (dy * 150.0) / l

    #     # Now subtract all forces pulling items together.
    #     weight = (len(self.edgeList) + 1) * 10.0
    #     for edge in self.edgeList:
    #         if edge.sourceNode() is self:
    #             pos = self.mapFromItem(edge.destNode(), 0, 0)
    #         else:
    #             pos = self.mapFromItem(edge.sourceNode(), 0, 0)
    #         xvel += pos.x() / weight
    #         yvel += pos.y() / weight
    
    #     if QtCore.qAbs(xvel) < 0.1 and QtCore.qAbs(yvel) < 0.1:
    #         xvel = yvel = 0.0

    #     sceneRect = self.scene().sceneRect()
    #     self.newPos = self.pos() + QtCore.QPointF(xvel, yvel)
    #     self.newPos.setX(min(max(self.newPos.x(), sceneRect.left() + 10), sceneRect.right() - 10))
    #     self.newPos.setY(min(max(self.newPos.y(), sceneRect.top() + 10), sceneRect.bottom() - 10))

    def advance(self):
        if self.newPos == self.pos():
            return False

        self.setPos(self.newPos)
        return True

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust, 50 + adjust,
                50 + adjust)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-10, -10, 50, 50)
        return path

    def paint(self, painter, option, widget):

        # painter.setPen(QtGui.QColor(168, 34, 3))
        font = QtGui.QFont("Helvetica [Cronyx]", 12)
        painter.setFont(font)
        painter.setBrush(QtCore.Qt.darkGray)
        #painter.drawEllipse(-7, -7, 20, 20)
        metrics = QtGui.QFontMetrics(font)

        gradient = QtGui.QRadialGradient(-3, -3, 50)
        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.yellow).light(120))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkYellow).light(120))
        else:
            gradient.setColorAt(0, QtCore.Qt.yellow)
            gradient.setColorAt(1, QtCore.Qt.darkYellow)

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-10, -10, 50, 50)
        boundingRectForText = metrics.boundingRect(self.name)
        painter.drawText(QtCore.QPointF(), self.name)
        
        # painter.drawEllipse(self.boundingRect())
        print(f"Painted name {self.name}")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edgeList:
                edge.adjust()
            self.graph.itemMoved()

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        super(Node, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super(Node, self).mouseReleaseEvent(event)

    # # Override
    # def boundingRect(self):
    #     penWidth = 1.0
    #     return QRectF(-10 - penWidth / 2, -10 - penWidth / 2,
    #                   20 + penWidth, 20 + penWidth)
    
    # #Override
    # def paint(self, painter, option, widget):
    #     painter.drawRoundedRect(-10, -10, 20, 20, 5, 5)

class GraphWidget(QGraphicsView):
    def __init__(self, graph):
        super(GraphWidget, self).__init__()

        self.timerId = 0
        self.graph = graph
        scene = QGraphicsScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        drawnNodes = {}
        for node in graph:
            if node not in drawnNodes.keys():
                nodeView = Node(self, str(node))
                drawnNodes[node] = nodeView
                scene.addItem(nodeView)
            for neighbor in graph[node]:
                if neighbor not in drawnNodes.keys():
                    neighborView = Node(self, str(neighbor))
                    drawnNodes[neighbor] = neighborView
                    scene.addItem(neighborView)
                edgeView = Edge(drawnNodes[node], drawnNodes[neighbor])
                scene.addItem(edgeView)
        for nodeData, nodeView in drawnNodes.items():
            nodeView.setPos(0, nodeData.step*60)
            
        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle("Elastic Nodes")

    def itemMoved(self):
        if not self.timerId:
            self.timerId = self.startTimer(1000 / 25)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Up:
            self.centerNode.moveBy(0, -20)
        elif key == QtCore.Qt.Key_Down:
            self.centerNode.moveBy(0, 20)
        elif key == QtCore.Qt.Key_Left:
            self.centerNode.moveBy(-20, 0)
        elif key == QtCore.Qt.Key_Right:
            self.centerNode.moveBy(20, 0)
        elif key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
            for item in self.scene().items():
                if isinstance(item, Node):
                    item.setPos(-150 + QtCore.qrand() % 300, -150 + QtCore.qrand() % 300)
        else:
            super(GraphWidget, self).keyPressEvent(event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))


    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)


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
    w = GraphWidget(G)
    # QWidget
    
    # QMainWindow using QWidget as central widget
    window = MainWindow(w)

    window.show()
    sys.exit(app.exec_())