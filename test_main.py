from debuggo.prototype import main
from debuggo.solve import solver
def test_test():
    print("Test test")
    assert True

def test_full():
    paths = main()
    true_paths = [['d', 'c', 'b', 'a'], ['d', 'c', 'b', 'not_a'], ['d', 'c', 'not_b', 'a'], ['d', 'c', 'not_b', 'not_a'], ['d', 'not_c', 'b', 'a'], ['d', 'not_c', 'b', 'not_a'], ['d', 'not_c', 'not_b', 'a'], ['d', 'not_c', 'not_b', 'not_a']]
    assert true_paths == paths

def test_solver():
    stable_models = [["a"]]
    s = solver.Solver(stable_models)
    assert stable_models == s.stable_models

