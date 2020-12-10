import math
import os

import igraph
import networkx as nx
import pathlib
import matplotlib.pyplot as plt
import numpy as np
import sys
from PySide2 import QtGui, QtCore
from PySide2.QtCore import Slot, QRect, Qt, QPoint
from PySide2.QtGui import QImage, QPainter
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QStyle, QApplication, QHBoxLayout, \
    QMainWindow, QAction, QSplitter, QVBoxLayout, QWidget, QListWidget
from networkx.drawing.nx_pydot import graphviz_layout

from debuggo.solve.solver import SolverState

class Color(QWidget):
    """Just for prototyping purposes"""

    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
        self.setPalette(palette)
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
class Visualizer(object):

    def __init__(self, solver_paths):
        self.solver_paths = solver_paths


class FolderVisualizer(Visualizer):

    def __init__(self, solver_paths, target_dir):
        super().__init__(solver_paths)
        self.target_dir = target_dir

    def write_paths(self, paths):
        print(f"Root directory for visualization: {self.target_dir}")
        COMMIT = False # Change this to true to actually write stuff.
        if COMMIT:
            if not os.path.exists(self.target_dir):
                os.mkdir(self.target_dir)

        for path in paths:
            mkpath = f"{self.target_dir}/{'/'.join(path)}"
            print(f"Path: {mkpath}")
            if COMMIT:
                if not os.path.exists(mkpath):
                    pathlib.Path(mkpath).mkdir(parents=True)
        return paths


class GraphVisualizer(Visualizer):
    def __init__(self, solver_graph):
        super().__init__(None)
        self.solver_graph = solver_graph

    def create_graph(self):
        pass

    def transform_to_neo4j(self):
        pass

    def transform_to_d3js(self):
        pass

    def draw_networkx_graph(self, draw = False):
        G = self.solver_graph
        if (draw):
            nx.draw(G, with_labels=True)
            plt.show()


class Edge(QGraphicsItem):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode, rule="N/A"):
        super(Edge, self).__init__()
        self._rule = rule
        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()

        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()
        self._font = QtGui.QFont("times", 10)
        self._fm = QtGui.QFontMetrics(self._font)

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
        middle = QtCore.QPointF((self.sourcePoint + self.destPoint) / 2)
        br_for_text = self._fm.boundingRect(self._rule)
        br_for_text.moveTo(middle.x(), middle.y())
        return QtCore.QRectF(self.sourcePoint,
                             QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                           self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra,
                                                                                                             -extra,
                                                                                                             extra,
                                                                                                             extra).united(
            br_for_text)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)
        middle = QtCore.QPointF((self.sourcePoint + self.destPoint) / 2)

        # Adjusting position of Rule text.
        middle.setX(self.source.boundingRect().x() + self.source.boundingRect().width())
        middle.setY(middle.y()+self._fm.height())

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine,
                                  QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Edge.TwoPi - angle
        destArrowP1 = self.destPoint + QtCore.QPointF(math.sin(angle - Edge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - Edge.Pi / 3) * self.arrowSize)
        destArrowP2 = self.destPoint + QtCore.QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)

        painter.setBrush(QtCore.Qt.black)

        painter.drawPolygon(QtGui.QPolygonF([line.p2(), destArrowP1, destArrowP2]))

        painter.drawText(middle, self._rule)
class PySideDisplay(QGraphicsView):
    def __init__(self, graph):
        super(PySideDisplay, self).__init__()
        print(f"Initializing PySideDisplay with {len(graph)} nodes.")
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
        # ({}, 0) - [{'rule': 'a.'}] > ({a}, 1)
        # ({a}, 1) - [{'rule': '{b} :- a.'}] > ({a, b}, 2)
        # ({a}, 1) - [{'rule': '{b} :- a.'}] > ({a}, 2)
        # layer = 0
        # ROOT = SolverState("{}",0)
        # for node, target in nx.bfs_edges(graph, SolverState()):
        #     if node not in drawnNodes.keys():
        #         nodeView = Node(self, str(node))
        #         drawnNodes[node] = nodeView
        #         scene.addItem(nodeView)
        #
        #     print(f"{node, node.step} -[{g[node][target]}]> {target, target.step}")
        for node, nbrsdict in graph.adjacency():
            if node not in drawnNodes.keys():
                nodeView = Node(self, str(node))
                drawnNodes[node] = nodeView
                scene.addItem(nodeView)
            for neighbor, eattr in nbrsdict.items():

                if neighbor not in drawnNodes.keys():
                    neighborView = Node(self, str(neighbor))
                    drawnNodes[neighbor] = neighborView
                    scene.addItem(neighborView)
                edgeView = Edge(drawnNodes[node], drawnNodes[neighbor], eattr["rule"])
                scene.addItem(edgeView)
        for nodeData, nodeView in drawnNodes.items():
            nodeView.setPos(nodeData.path*100, nodeData.step*100)

        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.scaleView(1)
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
            super(PySideDisplay, self).keyPressEvent(event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))


    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)

class HeadlessPysideDisplay(PySideDisplay):
    """
    Creates an artificial QApplication as nothing can be rendered without it.
    Only use this is if you do not want to actually create a GUI but only grab
    a render.
    """
    def __init__(self, graph):
        _ = QApplication()
        super().__init__(graph)

    def get_graph_as_np_array(self):
        # TODO: Coloring looks different, fix?
        p = self.grab()
        img = p.toImage()
        width = img.width()
        height = img.height()
        ptr = img.constBits()
        arr = np.array(ptr).reshape(height, width, 4)
        return arr


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
        # painter.drawEllipse(-7, -7, 20, 20)
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
        center = QRect(-10, -10, 50, 50)
        painter.drawEllipse(center)
        textAreaLeft = QPoint(center.left()+2,((center.bottomLeft().y()+center.topLeft().y()) / 2)+metrics.height()/2)
        elided = metrics.elidedText(self.name, Qt.ElideLeft, center.width())

        painter.drawText(textAreaLeft, elided)

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

class NetworkxDisplay():

    def __init__(self, graph):
        self._ng : nx.DiGraph = graph
        self._ig : igraph.Graph = self.nxgraph_to_igraph(graph)

    def model_to_string(self, model):
        result_str = ""
        how_many_per_line = math.sqrt(len(model))
        tmp = []
        for m in model:
            print(f"Consuming {str(m)}, current_state = {tmp}")
            if len(tmp) >= how_many_per_line:
                result_str += ", ".join(tmp)+"\n"
                tmp.clear()
            tmp.append(str(m))
        result_str += ", ".join(tmp)
        return f"{{{result_str}}}"

    def draw(self):
        # nx.draw(self._ng)
        print(f"Drawing graph with {len(self._ng)} nodes.")
        print(self._ig)
        node_size = 1000
        layout = self._ig.layout_reingold_tilford(root=[0])
        layout.rotate(180)
        # igraph.plot(self._ig, layout=layout)
        nx_map = {i: node for i, node in enumerate(self._ng.nodes())}
        pos = self.igraph_to_networkx_layout(layout, nx_map)

        for node in self._ng:
            print(f"{node.model} ({type(node)})")

        # pos = layouting_func(self._ng,
        #                      scale=100,
        #                      #subset_key="model"
        #                      )

        nx.draw_networkx_nodes(self._ng, pos,
                               # node_color=node_color,
                               alpha=0.9,
                               node_size=node_size,
                               # cmap=plt.get_cmap(colormap))
                               )
        nx.draw_networkx_edges(self._ng, pos,
                               alpha=0.5,
                               node_size=node_size)

        node_labels = {}
        edge_labels = {}
        recursive_labels = {}
        rec_edge_c = 0
        for node, nbrsdict in self._ng.adjacency():
            node_labels[node] = self.model_to_string(node.model)
            for neighbor, edge_attrs in nbrsdict.items():
                if str(edge_attrs["rule"]).count(":-") > 1:
                    rec_label = self.make_rec_label(edge_attrs['rule'])
                    recursive_labels[(node, neighbor)] = f"[{rec_edge_c}] {rec_label}"
                    rec_edge_c += 1
                else:
                    edge_labels[(node, neighbor)] = edge_attrs["rule"]

        nx.draw_networkx_labels(self._ng, pos,
                                font_size=8,
                                labels=node_labels)

        nx.draw_networkx_edge_labels(self._ng, pos,
                                     label_pos=.5,
                                     rotate=False,
                                     font_size=7,
                                     font_family="monospace",
                                     bbox={'facecolor' : 'White',
                                           'edgecolor' : 'Red',
                                           'boxstyle':'round'},
                                     edge_labels=recursive_labels)
        nx.draw_networkx_edge_labels(self._ng, pos,
                                     label_pos=.5,
                                     rotate=False,
                                     font_size=7,
                                     font_family="monospace",
                                     bbox={'facecolor' : 'White',
                                           'edgecolor' : 'Black',
                                           'boxstyle':'round'},
                                     edge_labels=edge_labels)

    @staticmethod
    def _inject_for_drawing(g):
        for v, dat in g.nodes(data=True):
            dat["step"] = v.rule
            print(dat)
        # pos = graphviz_layout(self._g, prog="twopi")
        # nx.draw(self._g, pos)
        # plt.show()
    @staticmethod
    def igraph_to_networkx_layout(i_layout, nx_map):
        nx_layout = {}
        for i, pos in enumerate(i_layout.coords):
            nx_layout[nx_map[i]] = pos
        return nx_layout

    @staticmethod
    def nxgraph_to_igraph(nxgraph):
        return igraph.Graph.Adjacency((nx.to_numpy_matrix(nxgraph) > 0).tolist())

    def make_rec_label(self, param):
        return "\n".join(param)

