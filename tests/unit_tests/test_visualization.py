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
    empty = SolverState(set(), True, 0, adds=set())
    a = SolverState({"a"}, True, 1, adds={"a"})
    b = SolverState({"a", "b"},True,  2, adds={"b"})
    c = SolverState({"a"},True,  2, adds=set())
    d = SolverState({"a"},True,  3, adds=set())
    e = SolverState({"a", "b", "c"},True,  3, adds={"c"})
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, e, rule="c :- b.")
    g.add_edge(c, d, rule="c :- b.")
    return g

def create_branching_diGraph_with_unsat():
    g = create_diGraph_with_single_branch()
    d = SolverState({"a"},True,  3, adds = set())
    e = SolverState({"a", "b", "c"},True,  3, adds={"c"})
    sat = SolverState({"a"}, True, 4, adds=set())
    unsat = SolverState(set(), False, 4, adds=set())
    g.add_edge(d, sat, rule=":- c.")
    g.add_edge(e, unsat, rule=":- c.")
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


def test_drawing_unsat_and_empty_look_different():
    g = create_branching_diGraph_with_unsat()
    assert len(g) == 10
    display = NetworkxDisplay(g, False)
    constraint_labels, edge_labels, node_labels, recursive_labels = display.make_labels()
    assert len(constraint_labels) == 1
    assert list(constraint_labels.keys())[0] == SolverState(set(), False, 4)
    assert len(edge_labels) == 7
    assert len(node_labels) == 7




def test_merge_nodes():
    g = create_diGraph_with_mergable_nodes()
    display = NetworkxDisplay(g, False)
    assert len(display._ng) == 6, "display should merge nodes with identical sets on the same step."


def test_returns_printable_array():
    g = create_simple_diGraph()
    display = NetworkxDisplay(g, print_changes_only=False)
    result = display.draw()
    assert result is not None, "display.draw() should return a result."
    assert isinstance(result, plt.Figure), "display.draw() should return a plottable array."


def test_branching_graph():
    g = create_diGraph_with_single_branch()
    display = NetworkxDisplay(g, False)
    pic = display.draw()


def test_nx_viz():
    g = create_diGraph_with_single_branch()
    display = NetworkxDisplay(g, False)
    display.draw()


def test_nx_viz_multiple_branches():
    g, _ = create_diGraph_with_multiple_branchoffs()
    display = NetworkxDisplay(g, False)
    display.draw()


def test_nx_viz_converges_again():
    g, _ = create_diGraph_not_a_tree()
    display = NetworkxDisplay(g, False)
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
#    plt.clf()
#    nx.draw(g, pos, with_labels=True)


def test_get_viz_size():
    width, height = get_width_and_height_of_text_label("test")
    assert width > 0
    assert height > 0
    assert width > height

def test_only_new_models_are_shown():
    g = create_branching_diGraph_with_unsat()
    display = NetworkxDisplay(g)
    constraint_labels, edge_labels, node_labels, recursive_labels = display.make_labels()

    for node, label in node_labels.items():
        label = set() if label == "\u2205" else set(label.split())
        if node.step != 4:
            assert node.adds == label, "inner nodes should only represent partial models."
        else:
            assert node.model == label, "The last node should represent the stable model."

    display = NetworkxDisplay(g, print_changes_only=False)
    constraint_labels, edge_labels, node_labels, recursive_labels = display.make_labels()

    for node, label in node_labels.items():
        label = set() if label == "\u2205" else set(label.split())
        assert node.model == label, "inner nodes should only represent partial models."

def test_print_empty_graph():
    pass

def test_max_model_size_parameter():
    for maximum in [0, 1, 5, 20, 25]:
        g = nx.DiGraph()
        a = SolverState(set(str(x) for x in range(40)), 0, True)
        b = SolverState(set(str(x) for x in range(40)), 1, True)
        g.add_edge(a, b, rule="Wow")
        display = NetworkxDisplay(g, atom_draw_maximum=maximum, print_changes_only=False)
        display.draw()
        constraint_labels, edge_labels, node_labels, recursive_labels = display.make_labels()
        print(node_labels)
        print(constraint_labels)
        print(edge_labels)
        print(recursive_labels)
        label_length = len(list(node_labels.values())[0].split())
        assert label_length <= maximum, "display should only print <= maximum atoms."
