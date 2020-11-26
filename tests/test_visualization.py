import sys

import networkx as nx
import matplotlib.pyplot as plt
from PySide2.QtWidgets import QApplication

from debuggo.solve.solver import SolverState, annotate_edges_in_nodes
from debuggo.display.graph import HeadlessPysideDisplay, MainWindow, PySideDisplay, NetworkxDisplay
from debuggo.display.detail import HeadlessPySideDetailDisplay
import igraph
def create_simple_diGraph():

    graph = nx.DiGraph()
    a = SolverState("{a, b, c, d}", 0)
    b = SolverState("b", 1)
    graph.add_edge(a, b, rule="rule")
    return graph

def create_diGraph_with_single_branch():
    g = nx.DiGraph()
    empty = SolverState("{}", 0)
    a = SolverState("{a}",1)
    b = SolverState("{a,b}", 2)
    c = SolverState("{a}", 2)
    d = SolverState("{a}",3)
    e = SolverState("{a,b,c}",3)
    g.add_edge(empty, a, rule = "a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b,e, rule="c :- b.")
    g.add_edge(c,d, rule="c :- b.")
    return g, empty

def create_diGraph_with_multiple_branchoffs():
    g = nx.DiGraph()
    empty = SolverState("{}", 0)
    a = SolverState("{a}",1)
    b = SolverState("{a,b}", 2)
    c = SolverState("{a}", 2)
    d = SolverState("{a}",3)
    e = SolverState("{a,b,c}",3)
    f = SolverState("{a,b,d}",3)
    g.add_edge(empty, a, rule = "a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b,e, rule="1{c,d}1 :- b.")
    g.add_edge(c,d, rule="1{c,d}1 :- b.")
    g.add_edge(c,f, rule="1{c,d}1 :- b.")
    g.nodes(data=True)
    return g, empty


def test_print_picture():
    graph = create_simple_diGraph()
    display = HeadlessPysideDisplay(graph)
    pic = display.get_graph_as_np_array()
    plt.imshow(pic)
    plt.show()

def test_application_branching():
    g, empty = create_diGraph_with_single_branch()
    annotate_edges_in_nodes(g, empty)
    app = QApplication()

    w = PySideDisplay(g)
    # QWidget

    # QMainWindow using QWidget as central widget
    window = MainWindow(w)

    window.show()
    sys.exit(app.exec_())

def test_detail_picture():
    graph = nx.DiGraph()
    a = SolverState("{a, b, c, d}", 0)
    b = SolverState("b", 1)
    graph.add_edge(a, b, rule="rule")
    display = HeadlessPySideDetailDisplay(graph)
    display.displayModel(b)

def test_bfs():
    g, empty = create_diGraph_with_single_branch()
    annotate_edges_in_nodes(g, empty)


def test_branching_graph():
    g, empty = create_diGraph_with_single_branch()
    annotate_edges_in_nodes(g, empty)
    display = HeadlessPysideDisplay(g)
    pic = display.get_graph_as_np_array()
    plt.imshow(pic)
    plt.show()

def test_nx_viz():
    g, empty = create_diGraph_with_single_branch()
    display = NetworkxDisplay(g)
    display.draw()

def test_nx_viz_multiple_branches():
    g, _ = create_diGraph_with_multiple_branchoffs()
    display = NetworkxDisplay(g)
    display.draw()
    # for layout in nx.drawing.layout.__all__:
    #     try:
    #         print(f"Doing {layout}..")
    #         display.draw(layout)
    #     except TypeError as e:
    #         print(e)

def test_default_nx_viz():
    g, _ = create_diGraph_with_multiple_branchoffs()
    nx.draw_random(g, with_labels=True)
    plt.show()

def test_foo():
    g = igraph.Graph()
    g.add_edge("a", "b")
    g.add_edge("b", "c")
    g.add_edge("b", "d")
    g.add_edge("d","e")
    g.add_edge("d","f")
    g.layout_reingold_tilford()
    # "bipartite_layout",
    # "circular_layout",
    # "kamada_kawai_layout",
    # "random_layout",
    # "rescale_layout",
    # "rescale_layout_dict",
    # "shell_layout",
    # "spring_layout",
    # "spectral_layout",
    # "planar_layout",
    # "fruchterman_reingold_layout",
    # "spiral_layout",
    # "multipartite_layout",
