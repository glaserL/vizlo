import sys

import networkx as nx
import matplotlib.pyplot as plt
from PySide2.QtWidgets import QApplication

from debuggo.solve.solver import SolverState, annotate_edges_in_nodes
from debuggo.display.graph import NetworkxDisplay
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

def create_recursive_diGraph():
    g = nx.DiGraph()
    empty = SolverState("{}", 0, rule="x(1).")
    a = SolverState("x(1)", 1, rule=1)
    b = SolverState("x(1), y(1)",2, rule=2)
    c = SolverState("x(2), x(1), y(1)", 3,rule=1)
    d = SolverState("y(2), x(2), y(1), x(1)", 4, rule=2)
    e = SolverState("x(3), y(2), x(2), y(1), x(1)", 5,rule=1)
    #g.add_edge(empty, a, rule = "x(1).")
    g.add_edge(a, b, rule = "y(X) :- x(X).")
    g.add_edge(b, c, rule = "x(X) :- y(Y); Y=(X-1); X<10.")
    g.add_edge(c, d, rule = "y(X) :- x(X).")
    g.add_edge(d, e, rule = "x(X) :- y(Y); Y=(X-1); X<10.")
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

def create_diGraph_not_a_tree():
    g = nx.DiGraph()
    empty = SolverState("{}", 0)
    a = SolverState("{a}",1)
    b = SolverState("{a,b}", 2)
    c = SolverState("{a}", 2)
    d = SolverState("{a,b}",3)
    g.add_edge(empty, a, rule = "a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b,d, rule="a :- b.")
    g.add_edge(c,d, rule="a :- b.")
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

def test_paint_returns_image():
    assert False

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

def test_nx_viz_converges_again():
    g, _ = create_diGraph_not_a_tree()
    display = NetworkxDisplay(g)
    display.draw()

def test_default_nx_viz():
    g, _ = create_diGraph_with_multiple_branchoffs()
    nx.draw_random(g, with_labels=True)
    plt.show()

def test_recursive_viz():
    g, _ = create_recursive_diGraph()
    NetworkxDisplay._inject_for_drawing(g)
    nx.multipartite_layout(g, "step")
    plt.show()

# TODO: there should be some mapping, RECURSIVE_RULE -> RULE_ID
def get_column_positions(pos, rule_mapping):
    """For a position mapping node -> pos and a rule mapping rule -> rule_id,
    returns the x position for each rule."""
    column_positions = {} # RULE_ID -> X POSITION
    for rule, rule_id in rule_mapping.items():
        for node, xy in pos.items():
            if node.rule_id == rule_id:
                column_positions[rule] = xy[0]
                break
    return column_positions

# Requirement: a recursive subprogram requires to have a CIRCLE
# of dependencies. As soon as there are more than one path from any node to
# any other, the program fails.

def test_test():
    g = nx.DiGraph()
    g.add_edge(1,2)
    g.add_edge(2,3)
    g.add_edge(3,4)
    g.add_edge(4,5)
    g.add_edge(5,6)
    g.nodes[1]["rule"] = 1
    g.nodes[2]["rule"] = 2
    g.nodes[3]["rule"] = 1
    g.nodes[4]["rule"] = 2
    g.nodes[5]["rule"] = 3
    g.nodes[6]["rule"] = 3

    pos = nx.multipartite_layout(g, "rule")
    print(f"???{pos}")
    plt.clf()
    nx.draw(g, pos, with_labels=True)
    plt.show()

def test_get_viz_size():
    display = NetworkxDisplay(nx.DiGraph())
    width, height = get_width_and_height_of_text_label("test")
    assert width > 0
    assert height > 0
    assert width > height
