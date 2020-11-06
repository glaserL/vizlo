from PySide2.QtWidgets import QApplication, QGraphicsView
import numpy as np

class PySideDetailDisplay(QGraphicsView):
    def __init__(self, graph):
        super(PySideDetailDisplay, self).__init__()
        self.graph = graph
        self.inEdges = set()
        self.model = set()

    def displayModel(self, model):
        self.inEdges.clear()
        self.model = model
        if model in self.graph:
            for in_edge, _ in self.graph.in_edges(model):
                self.inEdges.add(in_edge)
        else:
            print(f"ERROR {model} not in graph!")

    def paint(self, painter, option, widget):
        print("Painting??")

class HeadlessPySideDetailDisplay(PySideDetailDisplay):
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
