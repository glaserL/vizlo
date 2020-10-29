from debuggo.solve import solver
from debuggo.types import SolvingHistory


def get_transformed_test_program():
    with open("/Users/glaser/Developer/cogsys/3_cci/debuggo/tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    return reified_program


def test_single_solver_runner_step():
    reified_program = get_transformed_test_program()
    sr = solver.SolveRunner(reified_program)
    sr.ctl.ground([("base", [])])
    for _ in range(5):
        print(".",end="")
        sr.step()
    graph = sr.graph
    assert len(graph) == 5

def test_until_stable():
    reified_program = get_transformed_test_program()
    sr = solver.SolveRunner(reified_program)
    sr.ctl.ground([("base", [])])
    sr.step_until_stable()
    graph = sr.graph
    assert len(graph) == 5

def test_has_reached_stable_model_function():
    one = solver.SolverState(set(["A","B"]))
    two = solver.SolverState(set(["A","B"]))
    assert one == two

def test_early_stopping_of_solver():
    reified_program = get_transformed_test_program()
    sr = solver.SolveRunner(reified_program)
    for _ in range(20):
        sr.step()
    graph = sr.graph
    assert len(graph) == 5

def test_solver_state_is_hashable():
    solver_state = solver.SolverState(None)
    assert hash(solver_state)