from debuggo.prototype import main
from debuggo.solve import solver
from debuggo.types import SolvingHistory
from debuggo.transform import transform

def test_test():
    print("Test test")
    assert True

def test_full():
    paths = main()
    true_paths = [['d', 'c', 'b', 'a'], ['d', 'c', 'b', 'not_a'], ['d', 'c', 'not_b', 'a'], ['d', 'c', 'not_b', 'not_a'], ['d', 'not_c', 'b', 'a'], ['d', 'not_c', 'b', 'not_a'], ['d', 'not_c', 'not_b', 'a'], ['d', 'not_c', 'not_b', 'not_a']]
    assert true_paths == paths

def test_solver_prototype():
    stable_models = [["a"]]
    s = solver.Solver(stable_models)
    assert stable_models == s.stable_models

## Transformer

def test_identity_transformer():
    it = transform.IdentityTransformer()
    with open("tests/program.lp", encoding="utf-8") as f:
        program = "".join(f.readlines())
        assert program == it.transform(program)

def test_abstract_transformer():
    error = None
    try:
        _ = transform.ASPTransformer()
    except NotImplementedError as e:
        error = e
    assert isinstance(error, NotImplementedError)



## Solver History and State
def testSolverHistoryType():
    sh: SolvingHistory = []
    sh.append(solver.SolverState(None, None, None))
    sh.pop()

def testSurvivabilityOfModelObject():
    pass

def test_single_solver_runner_step():
    it = transform.IdentityTransformer()
    reified_program = it.transform("")
    sr = solver.SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    print()
    history = sr.history
    print(history)
