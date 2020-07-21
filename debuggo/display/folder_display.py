import os
import pathlib

class Visualizer(object):
    
    def __init__(self, solver_paths):
        self.solver_paths = solver_paths


class FolderVisualizer(Visualizer):

    def __init__(self, solver_paths, target_dir):
        super().__init__(solver_paths)
        self.target_dir = target_dir

    def write_paths(self, paths):
        print(f"Root directory for visualization: {self.target_dir}")  
        COMMIT = False # Change this to true to actually write stuff.
        if COMMIT:
            if not os.path.exists(self.target_dir):
                os.mkdir(self.target_dir)
                    
        for path in paths:
            mkpath = f"{self.target_dir}/{'/'.join(path)}"
            print(f"Path: {mkpath}")
            if COMMIT:
                if not os.path.exists(mkpath):
                    pathlib.Path(mkpath).mkdir(parents=True)
        return paths