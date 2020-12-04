from debuggo.solve import solver
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

def test_long_distance_branching():
    prg = ["a.","{b} :- a.", "c :- b.", "{d} :- b.", "e :- not d."]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 12
    nodes = list(g.nodes)
    lengths = [0,1,1,2,1,3,1,3,4,2,4,4]
    for i, l in enumerate(lengths):
        assert len(nodes[i].model) == l

def test_simple_recursive():
    prg = [["a."], ["c :- b.", "b :- c, not a."]]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 3

def test_recursive_with_choice_before():
    prg = [["{a}."], ["c :- b.", "b :- c, not a."]]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
    assert len(g) == 5

def test_recursive_with_choice_within():
    prg = [["c :- b.", "{b} :- c, not a."]]
    slv = solver.SolveRunner(prg)
    g = slv.make_graph()
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
    prg = [["x(a)."], ["y(X) :- x(X)."]]
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

def test_recursion():
    prg = [["{a}."], ["c :- b.", "b :- c; not a."]]
    slv = solver.SolveRunner(prg)
    slv._g.add_node(solver.INITIAL_EMPTY_SET)
    slv._recursive2(prg[1], 0)
