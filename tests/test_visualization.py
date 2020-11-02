import networkx as nx
import matplotlib.pyplot as plt
from debuggo.display import folder_display
from debuggo.solve.solver import SolverState
from debuggo.display.folder_display import HeadlessPysideDisplay
def test_print_picture():
    graph = nx.DiGraph()
    a = SolverState("a", 0)
    b = SolverState("b", 1)
    graph.add_edge(a, b, rule="rule")
    display = HeadlessPysideDisplay(graph)
    pic = display.get_graph_as_np_array()
    plt.imshow(pic)
    plt.show()

