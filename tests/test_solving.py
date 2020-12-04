from debuggo.solve import solver
from debuggo.types import SolvingHistory
from clingo import Control

def get_transformed_test_program():
    with open("/Users/glaser/Developer/cogsys/3_cci/debuggo/tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    return reified_program

def get_test_program():
    with open("/Users/glaser/Developer/cogsys/3_cci/debuggo/tests/program.lp", encoding="utf-8") as f:
        program = "".join(f.readlines())
    return program

def create_ctl(program):
    ctl = Control()
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    return ctl

def test_new_solver():
    anotherOne = solver.SolveRunner(["a.", "{b} :- a.", "c :- b."])
    g = anotherOne.make_graph()
    assert len(g) == 6

def test_simple_fact():
    prg = ["a."]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 2
    nodes = list(g.nodes)
    assert len(nodes[0].model) == 0
    assert len(nodes[1].model) == 1

def test_function():
    prg = ["x(a)."]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 2
    nodes = list(g.nodes)
    assert len(nodes[0].model) == 0
    assert len(nodes[1].model) == 1


def test_variable():
    prg = ["x(a).", "y(X) :- x(X)."]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 3
    nodes = list(g.nodes)
    assert len(nodes[0].model)==0
    assert len(nodes[1].model) == 1
    assert len(nodes[2].model) == 2


def test_choice():
    prg = ["{a}."]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 3
    nodes = list(g.nodes)
    assert len(nodes[0].model) == 0
    assert len(nodes[1].model) == 0
    assert len(nodes[2].model) == 1

def test_has_reached_stable_model_function():
    one = solver.SolverState(set(["A","B"]))
    two = solver.SolverState(set(["A","B"]))
    assert one == two


def test_solver_state_is_hashable():
    solver_state = solver.SolverState(None)
    assert hash(solver_state)
