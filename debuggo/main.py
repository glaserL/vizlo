import sys

from PySide2.QtWidgets import QApplication, QHBoxLayout
from clingo import Control, Symbol, StatisticsMap, Model, SolveHandle, SolveResult
from debuggo.transform.transform import HeadBodyTransformer
from debuggo.display.folder_display import HeadlessPysideDisplay, PySideDisplay, MainWindow
from debuggo.solve.solver import SolveRunner
from typing import List, Tuple, Any, Union

class Dingo(Control):

    def __init__(self, arguments:List[str]=[], logger=None, message_limit:int=20):
        self.control = Control(arguments, logger, message_limit)
        self.debuggo = Control(arguments, logger, message_limit)
        self.solveRunner = SolveRunner("",control = self.debuggo)
        self.transformer = HeadBodyTransformer()

    def paint(self, model: Model) -> None:
        self.display = HeadlessPysideDisplay(self.solveRunner.graph)
        return self.display.get_graph_as_np_array()

    def add(self, name:str, parameters:List[str], program:str) -> None:
        # TODO: prettify this.
        self.control.add(name, parameters, program)
        _ = self.transformer.transform(program)
        self.solveRunner.program = program
        reified_program = self.transformer.get_reified_program_as_str()
        print(reified_program)
        self.debuggo.add(name, parameters, reified_program)
        
    def ground(self, parts:List[Tuple[str,List[Symbol]]], context:Any=None) -> None:
        print("Grounding..")
        self.control.ground(parts, context)
        self.debuggo.ground(parts, context)
        print("Done.")

    def solve(self, assumptions:List[Union[Tuple[Symbol,bool],int]]=[], 
                    on_model=None, 
                    on_statistics=None, 
                    on_finish=None, 
                    yield_:bool=False, 
                    async_:bool=False) -> Union[SolveHandle,SolveResult]:
        self.solveRunner.step_until_stable()
        return self.control.solve(assumptions, on_model, on_statistics, on_finish, yield_, async_)



def _main():
    with open("../tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    ctl = Dingo()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.ground([("base", [])])
    sat = ctl.solve()

    G = ctl.solveRunner.graph
    app = QApplication(sys.argv)

    layout = QHBoxLayout()
    w = PySideDisplay(G)
    # QWidget

    # QMainWindow using QWidget as central widget
    window = MainWindow(w)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    _main()
