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

def test_solver_runner_stepping():
    reified_program = get_transformed_test_program()
    ctl = create_ctl(reified_program)
    sr = solver.SolveRunner(get_test_program(),ctl)
    for _ in range(5):
        print(".",end="")
        sr.step()
    graph = sr.graph
    assert len(graph) == 5

def test_until_stable():
    reified_program = get_transformed_test_program()
    sr = solver.SolveRunner(get_test_program(), create_ctl(reified_program))
    sr.step_until_stable()
    graph = sr.graph
    assert len(graph) == 5


def test_has_reached_stable_model_function():
    one = solver.SolverState(set(["A","B"]))
    two = solver.SolverState(set(["A","B"]))
    assert one == two

def test_early_stopping_of_solver():
    reified_program = get_transformed_test_program()
    sr = solver.SolveRunner(get_test_program(), create_ctl(reified_program))
    for _ in range(20):
        sr.step()
    graph = sr.graph
    assert len(graph) == 5

def test_solver_state_is_hashable():
    solver_state = solver.SolverState(None)
    assert hash(solver_state)

def test_minimal_solving_program():
    prg = "a."
    prg_reified = "h(a,1,()) :- a.\na.\n#external a."
    sr = solver.SolveRunner(prg, create_ctl(prg_reified))
    for _ in range(5):
        sr.step()
    assert (len(sr.graph)) == 2
