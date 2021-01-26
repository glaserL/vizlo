import time

import clingo
import numpy as np
import networkx as nx
import pytest

from debuggo import solver, graph
from debuggo.main import Debuggo, PythonModel
import matplotlib.pyplot as plt

from debuggo.solver import SolveRunner


def test_clingo_ast_rules_are_passed_around():
    ctl = Debuggo()
    ctl.add_and_ground("b. a :- b.")

    transformed_program = ctl.program
    mocked_solve_runner = SolveRunner(transformed_program)
    assert isinstance(mocked_solve_runner._solvers[0].rule, clingo.ast.AST)
    assert isinstance(mocked_solve_runner.prg[0], clingo.ast.AST)
    assert isinstance(ctl.program[0], clingo.ast.AST)


def test_instanciations():
    _ = Debuggo()
    _ = Debuggo(["0"])


def test_parameters():
    _ = Debuggo(["1"], print_previous=True)
    _ = Debuggo(["1"], print_previous=True)


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
    expensive_program = "a(1..15). {b(X)} :- a(X)."
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
    prg = "{a}. :- not a. b :- a."
    ctl.add_and_ground(prg)
    g = ctl.make_graph()
    nodes = list(g.nodes)
    assert len(nodes) == 5, "Constrained partial models should not show up in the visualization."
    assert len(nodes[4].model) == 2
    assert len(nodes[2].model) == 1
    assert len(nodes[1].model) == 0


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
    assert isinstance(result, np.ndarray), "Debuggo.paint() should return a plottable array."
