from .solve import solver
from .display import folder_display
def main():

    stable_models = [["d"], ["d", "c"], ["d", "c", "b"], ["d", "c", "b", "a"]]
    s = solver.Solver(stable_models)
    definition_history = ["a", "b", "c", "d"] # the sequence of rule heads in the program    
    definition_history = list(reversed(definition_history))

    root = "stack"

    paths = s.generate_path(definition_history)
    
    v = folder_display.FolderVisualizer(paths, root)
    
    return v.write_paths(paths)

main()