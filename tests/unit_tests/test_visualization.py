import sys

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from debuggo.solve.solver import SolverState, annotate_edges_in_nodes
from debuggo.display.graph import NetworkxDisplay, get_width_and_height_of_text_label
import igraph


def create_simple_diGraph():
    graph = nx.DiGraph()
    a = SolverState({"a", " b", " c", " d"}, 0)
    b = SolverState({"b"}, 1)
    graph.add_edge(a, b, rule="rule")
    return graph


def create_diGraph_with_mergable_nodes():
    g = nx.DiGraph()
    empty = SolverState(set(), 0)
    b = SolverState({"a", "b"}, 1)
    c = SolverState({"a"}, 1)
    d = SolverState(set(), 1)
    e = SolverState({"a", "b"}, 2)
    f = SolverState({"a", "b"}, 2)
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
    empty = SolverState(set(), 0)
    a = SolverState({"a"}, 1)
    b = SolverState({"a", "b"}, 2)
    c = SolverState({"a"}, 2)
    d = SolverState({"a"}, 3)
    e = SolverState({"a", "b", "c"}, 3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, e, rule="c :- b.")
    g.add_edge(c, d, rule="c :- b.")
    return g, empty


def create_recursive_diGraph():
    g = nx.DiGraph()
    empty = SolverState(set(), 0)
    a = SolverState({"x(1)"}, 1)
    b = SolverState({"x(1)", "y(1)"}, 2)
    c = SolverState({"x(2)", "x(1)", "y(1)"}, 3)
    d = SolverState({"y(2)", " x(2)", " y(1)", " x(1)"}, 4)
    e = SolverState({"x(3)", " y(2)", " x(2)", " y(1)", " x(1)"}, 5)
    g.add_edge(empty, a, rule="x(1).")
    g.add_edge(a, b, rule="y(X) :- x(X).")
    g.add_edge(b, c, rule="x(X) :- y(Y); Y=(X-1); X<10.")
    g.add_edge(c, d, rule="y(X) :- x(X).")
    g.add_edge(d, e, rule="x(X) :- y(Y); Y=(X-1); X<10.")
    return g, empty


def create_diGraph_with_multiple_branchoffs():
    g = nx.DiGraph()
    empty = SolverState(set(), 0)
    a = SolverState({"a"}, 1)
    b = SolverState({"a", "b"}, 2)
    c = SolverState({"a"}, 2)
    d = SolverState({"a"}, 3)
    e = SolverState({"a", "b", "c"}, 3)
    f = SolverState({"a", "b", "d"}, 3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, e, rule="1{c,d}1 :- b.")
    g.add_edge(c, d, rule="1{c,d}1 :- b.")
    g.add_edge(c, f, rule="1{c,d}1 :- b.")
    g.nodes(data=True)
    return g, empty


def create_diGraph_not_a_tree():
    g = nx.DiGraph()
    empty = SolverState(set(), 0)
    a = SolverState({"a"}, 1)
    b = SolverState({"a", "b"}, 2)
    c = SolverState({"a"}, 2)
    d = SolverState({"a", "b"}, 3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, d, rule="a :- b.")
    g.add_edge(c, d, rule="a :- b.")
    g.nodes(data=True)
    return g, empty


def test_merge_nodes():
    g = create_diGraph_with_mergable_nodes()
    display = NetworkxDisplay(g)
    assert len(display._ng) == 6, "display should merge nodes with identical sets on the same step."

def test_bfs():
    g, empty = create_diGraph_with_single_branch()
    annotate_edges_in_nodes(g, empty)


def test_returns_printable_array():
    g = create_simple_diGraph()
    display = NetworkxDisplay(g)
    pic = display.draw()
    assert isinstance(pic, np.ndarray)


def test_branching_graph():
    g, empty = create_diGraph_with_single_branch()
    display = NetworkxDisplay(g)
    pic = display.draw()


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


def test_default_nx_viz():
    g, _ = create_diGraph_with_multiple_branchoffs()
    nx.draw_random(g, with_labels=True)



def get_column_positions(pos, rule_mapping):
    """For a position mapping node -> pos and a rule mapping rule -> rule_id,
    returns the x position for each rule."""
    column_positions = {}  # RULE_ID -> X POSITION
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
