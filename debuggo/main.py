from clingo import Control, Symbol, StatisticsMap, Model, SolveHandle, SolveResult
from debuggo.transform.transform import HeadBodyTransformer
from debuggo.display.folder_display import PySideDisplay
from debuggo.solve.solver import SolveRunner
from typing import List, Tuple, Any, Union

class Dingo(Control):

    def __init__(self, arguments:List[str]=[], logger=None, message_limit:int=20):
        self.control = Control(arguments, logger, message_limit)
        self.debuggo = Control(arguments, logger, message_limit)
        self.solveRunner = SolveRunner(control = self.debuggo)
        self.transformer = HeadBodyTransformer()
        self.display = PySideDisplay()

    def paint(self, model: Model) -> None:
        return self.display.render(self.solveRunner.graph, model)

    def add(self, name:str, parameters:List[str], program:str) -> None:
        self.control.add(name, parameters, program)
        reified_program = self.transformer.transform(program)
        self.debuggo.add(name, parameters, reified_program)
        
    def ground(self, parts:List[Tuple[str,List[Symbol]]], context:Any=None) -> None:
        self.control.ground(parts, context)
        self.debuggo.ground(parts, context)

    def solve(self, assumptions:List[Union[Tuple[Symbol,bool],int]]=[], 
                    on_model=None, 
                    on_statistics=None, 
                    on_finish=None, 
                    yield_:bool=False, 
                    async_:bool=False) -> Union[SolveHandle,SolveResult]:
        self.solveRunner.step_until_stable()
        return self.control.solve(assumptions, on_model, on_statistics, on_finish, yield_, async_)