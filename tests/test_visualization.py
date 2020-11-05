import networkx as nx
import matplotlib.pyplot as plt
from debuggo.display import graph
from debuggo.solve.solver import SolverState
from debuggo.display.graph import HeadlessPysideDisplay
from debuggo.display.detail import HeadlessPySideDetailDisplay
def test_print_picture():
    graph = nx.DiGraph()
    a = SolverState("{a, b, c, d}", 0)
    b = SolverState("b", 1)
    graph.add_edge(a, b, rule="rule")
    display = HeadlessPysideDisplay(graph)
    pic = display.get_graph_as_np_array()
    plt.imshow(pic)
    plt.show()

def test_detail_picture():
    graph = nx.DiGraph()
    a = SolverState("{a, b, c, d}", 0)
    b = SolverState("b", 1)
    graph.add_edge(a, b, rule="rule")
    display = HeadlessPySideDetailDisplay(graph)
    display.displayModel(b)
