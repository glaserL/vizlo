import time

import clingo
import networkx as nx
import pytest

from debuggo import solver, graph
from debuggo.main import Debuggo, PythonModel

from debuggo.solver import SolveRunner


def test_clingo_ast_rules_are_passed_around():
    ctl = Debuggo()
    ctl.add_and_ground("b. a :- b.")

    transformed_program = ctl.program
    mocked_solve_runner = SolveRunner(transformed_program)
    assert isinstance(mocked_solve_runner._solvers[0].rule, clingo.ast.AST)
    assert isinstance(mocked_solve_runner.prg[0], clingo.ast.AST)
    assert isinstance(ctl.program[0], clingo.ast.AST)

## Transformer
def test_networkx():
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    sr = solver.SolveRunner(reified_program)
    for _ in range(5):
        print(".", end="")
        sr.step()
    viz = graph.GraphVisualizer(sr.graph)
    viz.draw_networkx_graph()


def test_instanciation():
    dingo = Debuggo()


@pytest.mark.skip
def test_internal_clingo_also_solves():
    ctl = Debuggo()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.solve()
#    assert not ctl.control.is_conflicting


def test_print_all_models():
    ctl = Debuggo()
    # prg = "a. {b} :- a. c :- b. d :- c."
    prg = "a."
    # prg = "x(1).\n#program recursive.\nx(X) :- x(X-1), X<10.\n#program recursive."
    prg = "x(1).\n#program recursive.\nx(X) :- y(X).\ny(X) :- x(X-1); X<4.\n#program recursive."
    prg = "a.\n{b} :- a.\nc :- b.\n{d} :- b.\ne :- not d.\n:- b."
    # prg = "{a}.\nb :- a. :- b."
    # prg = "x(1..100). {y(X)} :- x(X)."
    # prg = "b :- a."
    # prg = "x(1). x(X) :- x(Y); Y<X; X < 10."
    # prg = "{x(1)}.\n#program recursive.\nx(X) :- y(X).\ny(X) :- x(X-1); X<4.\n#program recursive."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()
    # TODO: Draw choice rules different (arrow dotted)
    # TODO: Draw constraint rules differently (red)
    # TODO: only print what was added (as option) the sudoku program, tsp, from asp class


# Milestones:
# Expand recursion steps NO
# Clickable NO
# Independent of order YES
# Efficiency YES

# Try with a real world program

def test_painting_specific_models_is_fast():
    expensive_program = "a(1..15). {b(X)} :- a(X)."
    begin = time.time()
    interesting_model = [clingo.Function("a", [i], True) for i in range(15)]
    ctl = Debuggo(["0"])
    ctl.add_and_ground(expensive_program)
    ctl.add_to_painter(interesting_model)
    ctl.paint()
    end = time.time()
    assert end-begin < 1


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
    assert len(ctl.painter) > 0


def test_dont_repeat_constraints():
    ctl = Debuggo()
    prg = "{a}. :- not a. b :- a."
    ctl.add_and_ground(prg)
    g = ctl.make_graph()
    nodes = list(g.nodes)
    assert len(nodes) == 5
    assert len(nodes[4].model) == 2
    assert len(nodes[2].model) == 1
    assert len(nodes[1].model) == 0



def test_finding_corresponding_nodes():
    ctl = Debuggo(["0"])
    prg = "{a}. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    stable_models = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            model_as_set = list(model.symbols(atoms=True))
            stable_models.append(model_as_set)
    g = ctl.anotherOne.make_graph()
    assert 2 == len(stable_models) == len(ctl.find_nodes_corresponding_to_stable_models(g, stable_models))


def test_recursion():
    ctl = Debuggo(["0"])
    prg = "a.\n#program recursive.\na :- b.\nb :- a.\n#program recursive."
    prg = "x(1).\n#program recursive.\nx(X) :- y(X).\ny(X) :- x(X-1); X<4.\n#program recursive."

    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()


def test_painting_without_initial_solving():
    ctl = Debuggo(["0"])
    # TODO: why do this global stuff if you can just grab them from the control object after grounding directly?
    ctl.add("base", [], "x(0..3). {y(X)} :- x(X).")
    ctl.ground([("base", [])])
    interesting_model = set()
    interesting_model.add(clingo.Function("y", [clingo.Number(5)]))
    interesting_model.add(clingo.Function("y", [clingo.Number(3)]))
    for x in range(6):
        interesting_model.add(clingo.Function("x", [clingo.Number(x)]))

    interesting_model = PythonModel(interesting_model)
    # ctl.add_to_painter(interesting_model)
    ctl.paint()


def test_that_iterating_over_tree_doesnt_return_node_twice():
    g = nx.DiGraph()
    g.add_edge("a", "b", rule="first")
    g.add_edge("a", "c", rule="second")
    g.add_edge("b", "d", rule="first")
    assert len(g) - 1 == len(list(g.edges(data=True)))


def test_and_viz_queens():
    queens = """
    
% domain
number(1..3).

% alldifferent
1 { q(X,Y) : number(Y) } 1 :- number(X).
1 { q(X,Y) : number(X) } 1 :- number(Y).

% remove conflicting answers
:- q(X1,Y1), q(X2,Y2), X1 < X2, Y1 == Y2.
:- q(X1,Y1), q(X2,Y2), X1 < X2, Y1 + X1 == Y2 + X2.
:- q(X1,Y1), q(X2,Y2), X1 < X2, Y1 - X1 == Y2 - X2.

"""
    queens = "{a}. {b}. {c}. a :- b. b: - c. c:- a."
    queens = "{a; b}. b :- a."
    queens = "{a}. {b} :- a. b :- not a."
    #queens = "{a}. b :- a. c :- not b."
    ctl = Debuggo(["0"])
    # TODO: why do this global stuff if you can just grab them from the control object after grounding directly?
    ctl.add("base", [], queens)
    ctl.ground([("base", [])])
    print("ok??")


def test_calling_paint_should_return_a_plottable_figure():
    pass
