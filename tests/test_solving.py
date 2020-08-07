from debuggo.solve import solver
from debuggo.types import SolvingHistory


def get_transformed_test_program():
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    return reified_program

def testSurvivabilityOfModelObject():
    assert False == True

def test_solver_prototype():
    stable_models = [["a"]]
    s = solver.Solver(stable_models)
    assert stable_models == s.stable_models

def test_single_solver_runner_step():
    reified_program = get_transformed_test_program()
    sr = solver.SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    history = sr.history
    print(history)
    assert len(history) == 5


## Solver History and State
def testSolverHistoryType():
    sh: SolvingHistory = []
    sh.append(solver.SolverState(None, None, None))
    sh.pop()
