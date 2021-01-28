import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from vizlo.solver import SolverState
from vizlo.graph import NetworkxDisplay, get_width_and_height_of_text_label


def create_simple_diGraph():
    graph = nx.DiGraph()
    a = SolverState({"a", " b", " c", " d"}, True, 0)
    b = SolverState({"b"}, True, 1)
    graph.add_edge(a, b, rule="rule")
    return graph


def create_diGraph_with_mergable_nodes():
    g = nx.DiGraph()
    empty = SolverState(set(), True, 0)
    b = SolverState({"a", "b"}, True, 1)
    c = SolverState({"a"}, True, 1)
    d = SolverState(set(), True, 1)
    e = SolverState({"a", "b"}, True, 2)
    f = SolverState({"a", "b"}, True, 2)
    h = SolverState(set(), 2)
    g.add_edge(empty, b, rule="{a ; b}.")
    g.add_edge(empty, c, rule="{a ; b}.")
    g.add_edge(empty, d, rule="{a ; b}.")
    g.add_edge(b, e, rule="b :- a.")
    g.add_edge(c, f, rule="b :- a.")
    g.add_edge(d, h, rule="b :- a.")
    return g


def create_diGraph_with_single_branch():
    g = nx.DiGraph()
    empty = SolverState(set(), True, 0)
    a = SolverState({"a"}, True, 1)
    b = SolverState({"a", "b"},True,  2)
    c = SolverState({"a"},True,  2)
    d = SolverState({"a"},True,  3)
    e = SolverState({"a", "b", "c"},True,  3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, e, rule="c :- b.")
    g.add_edge(c, d, rule="c :- b.")
    return g


def create_recursive_diGraph():
    g = nx.DiGraph()
    empty = SolverState(set(), True, 0)
    a = SolverState({"x(1)"}, True, 1)
    b = SolverState({"x(1)", "y(1)"}, True, 2)
    c = SolverState({"x(2)", "x(1)", "y(1)"}, True, 3)
    d = SolverState({"y(2)", " x(2)", " y(1)", " x(1)"}, True, 4)
    e = SolverState({"x(3)", " y(2)", " x(2)", " y(1)", " x(1)"}, True, 5)
    g.add_edge(empty, a, rule="x(1).")
    g.add_edge(a, b, rule="y(X) :- x(X).")
    g.add_edge(b, c, rule="x(X) :- y(Y); Y=(X-1); X<10.")
    g.add_edge(c, d, rule="y(X) :- x(X).")
    g.add_edge(d, e, rule="x(X) :- y(Y); Y=(X-1); X<10.")
    return g, empty


def create_diGraph_with_multiple_branchoffs():
    g = nx.DiGraph()
    empty = SolverState(set(), True, 0)
    a = SolverState({"a"}, True, 1)
    b = SolverState({"a", "b"}, True, 2)
    c = SolverState({"a"}, True, 2)
    d = SolverState({"a"}, True, 3)
    e = SolverState({"a", "b", "c"},True, 3)
    f = SolverState({"a", "b", "d"}, True, 3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, e, rule="1{c,d}1 :- b.")
    g.add_edge(c, d, rule="1{c,d}1 :- b.")
    g.add_edge(c, f, rule="1{c,d}1 :- b.")
    return g, empty


def create_diGraph_not_a_tree():
    g = nx.DiGraph()
    empty = SolverState(set(), True, 0)
    a = SolverState({"a"}, True, 1)
    b = SolverState({"a","b"},True, 2)
    c = SolverState({"a"}, True, 2)
    d = SolverState({"a",  "b"},True, 3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, d, rule="a :- b.")
    g.add_edge(c, d, rule="a :- b.")
    g.nodes(data=True)
    return g, empty

def create_branching_diGraph_with_unsat():
    g = create_diGraph_with_single_branch()
    d = SolverState({"a"},True,  3)
    e = SolverState({"a", "b", "c"},True,  3)
    sat = SolverState({"a"}, True, 4)
    unsat = SolverState(set(), False, 4)
    g.add_edge(d, sat, rule=":- c.")
    g.add_edge(e, unsat, rule=":- c.")
    return g

def test_drawing_unsat_and_empty_look_different():
    g = create_branching_diGraph_with_unsat()
    display = NetworkxDisplay(g)
    constraint_labels, edge_labels, node_labels, recursive_labels = display.make_labels()
    assert len(constraint_labels) == 1
    assert list(constraint_labels.keys())[0] == SolverState(set(), False, 4)
    assert len(edge_labels) == 7
    assert len(node_labels) == 7




def test_merge_nodes():
    g = create_diGraph_with_mergable_nodes()
    display = NetworkxDisplay(g)
    assert len(display._ng) == 6, "display should merge nodes with identical sets on the same step."


def test_returns_printable_array():
    g = create_simple_diGraph()
    display = NetworkxDisplay(g)
    pic = display.draw()
    assert isinstance(pic, np.ndarray)


def test_branching_graph():
    g = create_diGraph_with_single_branch()
    display = NetworkxDisplay(g)
    pic = display.draw()
    plt.show()


def test_nx_viz():
    g, empty = create_diGraph_with_single_branch()
    display = NetworkxDisplay(g)
    display.draw()


def test_nx_viz_multiple_branches():
    g, _ = create_diGraph_with_multiple_branchoffs()
    display = NetworkxDisplay(g)
    display.draw()


def test_nx_viz_converges_again():
    g, _ = create_diGraph_not_a_tree()
    display = NetworkxDisplay(g)
    display.draw()

# Requirement: a recursive subprogram requires to have a CIRCLE
# of dependencies. As soon as there are more than one path from any node to
# any other, the program fails.

def test_test():
    g = nx.DiGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    g.add_edge(4, 5)
    g.add_edge(5, 6)
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


def test_get_viz_size():
    width, height = get_width_and_height_of_text_label("test")
    assert width > 0
    assert height > 0
    assert width > height
