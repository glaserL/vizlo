import time

import clingo
import numpy as np
import networkx as nx
import pytest

from vizlo import solver, graph
from vizlo.graph import NetworkxDisplay
from vizlo.main import Debuggo, PythonModel
import matplotlib.pyplot as plt

from vizlo.solver import SolveRunner


def test_instanciations():
    _ = Debuggo()
    _ = Debuggo(["0"])


def test_parameters_exist():
    debuggo = Debuggo()
    with pytest.raises(ValueError):
        debuggo.paint(atom_draw_maximum=True)
        debuggo.paint(print_entire_models=False)
        debuggo.paint(sort_program=False)

def test_empty_program_raises_value_error():
    debuggo = Debuggo()
    with pytest.raises(ValueError):
        debuggo.paint()

def test_paint_without_program_doesnt_throw():
    pass


def test_inherits_control_methods():
    debuggo = Debuggo()
    ctl = clingo.Control()
    attrs = [attr for attr in dir(ctl) if not attr.startswith("_")]
    print(attrs)
    result = (hasattr(debuggo, a) for a in attrs)
    assert result, "Debuggo object should inherit functions from clingo.Control"


@pytest.mark.skip
def test_internal_clingo_also_solves():
    ctl = Debuggo()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.solve()


#    assert not ctl.control.is_conflicting

def test_painting_specific_models_is_fast():
    expensive_program = "a(1..3). {b(X)} :- a(X)."
    begin = time.time()
    interesting_model = [clingo.Function("a", [i], True) for i in range(15)]
    ctl = Debuggo(["0"])
    ctl.add_and_ground(expensive_program)
    ctl.add_to_painter(interesting_model)
    ctl.paint()
    end = time.time()
    assert end - begin < 1, "Painting a small subset of a large program should be fast."


def test_print_only_specific_model_complete_definition():
    ctl = Debuggo(["0"])
    prg = "{a}. b :- a."
    ctl.add_and_ground(prg)

    interesting_model = {clingo.Function("a", []), clingo.Function("b", [])}
    ctl.add_to_painter(interesting_model)

    g = ctl.make_graph()
    nx.draw(g, with_labels=True)
    plt.show()
    nodes = list(g.nodes)
    assert len(nodes) == 3
    assert len(nodes[0].model) == 0
    assert len(nodes[2].model) == 2


def test_adding_model_to_painter():
    ctl = Debuggo()
    prg = "{a}. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            ctl.add_to_painter(model)
    assert len(ctl.painter) > 0, "Models added to the painter should "


def test_dont_repeat_constraints():
    ctl = Debuggo()
    prg = "{a}. {b}. :- a. {c}."
    ctl.add_and_ground(prg)
    g = ctl.make_graph(False)
    assert len(g.nodes) == 15, "Internal solver state should not merge nodes."
    display = NetworkxDisplay(g, merge_nodes=False)
    assert len(display._ng) == 15, "Display graph should not be merged if not told to do so."
    display = NetworkxDisplay(g, merge_nodes=True)
    assert len(display._ng), "Constrained partial models should not show up in the visualization."


def test_painting_without_initial_solving():
    ctl = Debuggo(["0"])
    ctl.add("base", [], "x(0..3). {y(X)} :- x(X).")
    ctl.ground([("base", [])])
    interesting_model = set()
    interesting_model.add(clingo.Function("y", [clingo.Number(5)]))
    interesting_model.add(clingo.Function("y", [clingo.Number(3)]))
    for x in range(6):
        interesting_model.add(clingo.Function("x", [clingo.Number(x)]))

    interesting_model = PythonModel(interesting_model)
    ctl.add_to_painter(interesting_model)
    g = ctl.make_graph()
    assert len(g) > 0, "Painter should work independently of solving process."


def test_painting_with_adding_rules_during_solving():
    ctl = Debuggo(["0"])
    ctl.add("base", [], "{a; b; c}.")
    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            ctl.add_to_painter(m)
            break
    g = ctl.make_graph()
    assert len(g) == 2

def test_calling_paint_should_return_a_plottable_figure():
    ctl = Debuggo(["0"])
    ctl.add("base", [], "a.")
    result = ctl.paint()
    assert result is not None, "Debuggo.paint() should return a result."
    assert isinstance(result, plt.Figure), "Debuggo.paint() should return a plottable array."

def testy_test():
    # Just for playing around purposes
    ctl = Debuggo(["0"])
    long_prg = ""
    for x in "abcdefghijklmopqrstuvwxyz":
        long_prg += f"{x}."
    prg = "{a}. :- not a. b :- c, a. c :- not b."
    prg = "a. b :- a. {c}. d :- c. {f} :- d. :- f."
    ctl.add("base", [], prg)
    ctl.paint(sort_program=True, print_entire_models=True)
    plt.show()
