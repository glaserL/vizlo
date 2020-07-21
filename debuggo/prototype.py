import os
import pathlib
from .solve import solver

def main():

    stable_models = [["d"], ["d", "c"], ["d", "c", "b"], ["d", "c", "b", "a"]]
    s = solver.Solver(stable_models)
    definition_history = ["a", "b", "c", "d"] # the sequence of rule heads in the program    
    definition_history = list(reversed(definition_history))

    ROOT = "stack"
    if not os.path.exists(ROOT):
        os.mkdir(ROOT)
        

    paths = s.generate_path(definition_history)

    COMMIT = False
    for path in paths:
        mkpath = f"{ROOT}/{'/'.join(path)}"
        print(f"Path: {mkpath}")
        if COMMIT:
            if not os.path.exists(mkpath):
                pathlib.Path(mkpath).mkdir(parents=True)
    return paths

main()