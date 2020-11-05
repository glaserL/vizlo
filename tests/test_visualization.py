import sys

import networkx as nx
import matplotlib.pyplot as plt
from PySide2.QtWidgets import QApplication

from debuggo.display import graph
from debuggo.solve.solver import SolverState
from debuggo.display.graph import HeadlessPysideDisplay, MainWindow, PySideDisplay
from debuggo.display.detail import HeadlessPySideDetailDisplay
def create_simple_diGraph():

    graph = nx.DiGraph()
    a = SolverState("{a, b, c, d}", 0)
    b = SolverState("b", 1)
    graph.add_edge(a, b, rule="rule")
    return graph


def create_branching_diGraph():
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

def test_print_picture():
    graph = create_simple_diGraph()
    display = HeadlessPysideDisplay(graph)
    pic = display.get_graph_as_np_array()
    plt.imshow(pic)
    plt.show()

def test_application_branching():
    g, empty = create_branching_diGraph()
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
    g, empty = create_branching_diGraph()
    annotate_edges_in_nodes(g, empty)

def annotate_edges_in_nodes(g, begin):
    path_id = 0
    prev_step = 0
    for node in nx.bfs_tree(g, begin):
        print(node)
        if prev_step != node.step:
            print(f"Resetting {path_id}.")
            path_id = 0
        print(f"Setting {path_id}")
        node.path = path_id
        prev_step = node.step
        path_id += 1
    for node, target in nx.dfs_edges(g, begin):
        print(f"{node, node.step, node.path} -[{g[node][target]}]> {target, target.step, node.path}")
    return g


def test_branching_graph():
    g, empty = create_branching_diGraph()
    annotate_edges_in_nodes(g, empty)
    display = HeadlessPysideDisplay(g)
    pic = display.get_graph_as_np_array()
    plt.imshow(pic)
    plt.show()
