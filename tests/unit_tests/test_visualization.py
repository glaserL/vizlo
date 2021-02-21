import clingo
import networkx as nx
import matplotlib.pyplot as plt

from vizlo.solver import SolverState
from vizlo.graph import NetworkxDisplay
from vizlo.util import filter_prg


def create_simple_diGraph():
    graph = nx.DiGraph()
    a = SolverState({"a", " b", " c", " d"}, True, 0)
    b = SolverState({"b"}, True, 1)
    graph.add_edge(a, b, rule=str_to_ast("b."))
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
    b = SolverState({"a", "b"}, True, 2, adds={"b"})
    c = SolverState({"a"}, True, 2, adds=set())
    d = SolverState({"a"}, True, 3, adds=set())
    e = SolverState({"a", "b", "c"}, True, 3, adds={"c"})
    g.add_edge(empty, a, rule=str_to_ast("a."))
    g.add_edge(a, b, rule=str_to_ast("{b} :- a."))
    g.add_edge(a, c, rule=str_to_ast("{b} :- a."))
    g.add_edge(b, e, rule=str_to_ast("c :- b."))
    g.add_edge(c, d, rule=str_to_ast("c :- b."))
    return g


def create_branching_diGraph_with_unsat():
    g = create_diGraph_with_single_branch()
    d = SolverState({"a"}, True, 3, adds=set())
    e = SolverState({"a", "b", "c"}, True, 3, adds={"c"})
    sat = SolverState({"a"}, True, 4, adds=set())
    unsat = SolverState(set(), False, 4, adds=set())
    g.add_edge(d, sat, rule=str_to_ast(":- c."))
    g.add_edge(e, unsat, rule=str_to_ast(":- c."))
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
    e = SolverState({"a", "b", "c"}, True, 3)
    f = SolverState({"a", "b", "d"}, True, 3)
    g.add_edge(empty, a, rule="a.")
    g.add_edge(a, b, rule="{b} :- a.")
    g.add_edge(a, c, rule="{b} :- a.")
    g.add_edge(b, e, rule="1{c,d}1 :- b.")
    g.add_edge(c, d, rule="1{c,d}1 :- b.")
    g.add_edge(c, f, rule="1{c,d}1 :- b.")
    return g, empty


def str_to_ast(rule):
    ast = []
    clingo.parse_program(
        rule,
        lambda stm: filter_prg(stm, ast))
    return ast


def single_to_ast(rule):
    return str_to_ast(rule)[0]


def create_diGraph_not_a_tree():
    g = nx.DiGraph()
    empty = SolverState(set(), True, 0)
    a = SolverState({"a"}, True, 1)
    b = SolverState({"a", "b"}, True, 2)
    c = SolverState({"a"}, True, 2)
    d = SolverState({"a", "b"}, True, 3)
    g.add_edge(empty, a, rule=str_to_ast("a."))
    g.add_edge(a, b, rule=str_to_ast("{b} :- a."))
    g.add_edge(a, c, rule=str_to_ast("{b} :- a."))
    g.add_edge(b, d, rule=str_to_ast("a :- b."))
    g.add_edge(c, d, rule=str_to_ast("a :- b."))
    g.nodes(data=True)
    return g, empty


def test_drawing_unsat_and_empty_look_different():
    g = create_branching_diGraph_with_unsat()
    assert len(g) == 10
    display = NetworkxDisplay(g, False)
    normal_models, recursive_models, constraint_models, stable_models, rule_labels = display.make_labels()
    assert len(constraint_models) == 1
    assert list(constraint_models.keys())[0] == SolverState(set(), False, 4)
    assert len(normal_models) == 6
    assert len(rule_labels) == 7


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


def test_only_new_models_are_shown():
    g = create_branching_diGraph_with_unsat()
    display = NetworkxDisplay(g)
    normal_models, recursive_models, constraint_models, stable_models, rule_labels = display.make_labels()

    for node, label in normal_models.items():
        label = set() if label == "\u2205" else set(label.split())
        if node.step != 4:
            assert node.adds == label, "inner nodes should only represent partial models."
        else:
            assert node.model == label, "The last node should represent the stable model."

    display = NetworkxDisplay(g, print_changes_only=False)
    normal_models, recursive_models, constraint_models, stable_models, rule_labels = display.make_labels()

    for node, label in normal_models.items():
        label = set() if label == "\u2205" else set(label.split())
        assert node.model == label, "inner nodes should only represent partial models."


def test_print_empty_graph():
    pass


def test_max_model_size_parameter():
    for maximum in [0, 1, 5, 20, 25]:
        g = nx.DiGraph()
        a = SolverState(set(str(x) for x in range(30)), 0, True)
        b = SolverState(set(str(x) for x in range(30)), 1, True)
        g.add_edge(a, b, rule=str_to_ast("a."))
        display = NetworkxDisplay(g, atom_draw_maximum=maximum, print_changes_only=False)
        normal_models, recursive_models, constraint_models, stable_models, rule_labels = display.make_labels()
        all_node_labels = list(set().union(
            *[normal_models.values(), recursive_models.values(), constraint_models.values(), stable_models.values()]))
        maximum_label_length = max((len(model.split()) for model in all_node_labels))
        assert maximum_label_length <= maximum, "display should only print <= maximum atoms."
        del g
