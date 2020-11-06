import sys

from PySide2.QtWidgets import QApplication, QHBoxLayout
from clingo import Control, Symbol, StatisticsMap, Model, SolveHandle, SolveResult
from debuggo.transform.transform import HeadBodyTransformer, JustTheRulesTransformer
from debuggo.display.graph import HeadlessPysideDisplay, PySideDisplay, MainWindow
from debuggo.solve.solver import SolveRunner, AnotherOne, annotate_edges_in_nodes, INITIAL_EMPTY_SET
from typing import List, Tuple, Any, Union
import matplotlib.pyplot as plt



class Debuggo(Control):
    def __init__(self, arguments: List[str] = [], logger=None, message_limit: int = 20):
        self.control = Control(arguments, logger, message_limit)
        self.transformer = JustTheRulesTransformer()

    def ground(self, parts: List[Tuple[str, List[Symbol]]], context: Any = None) -> None:
        self.control.ground(parts, context)

    def solve(self, assumptions: List[Union[Tuple[Symbol, bool], int]] = [],
              on_model=None,
              on_statistics=None,
              on_finish=None,
              yield_: bool = False,
              async_: bool = False) -> Union[SolveHandle, SolveResult]:
        return self.control.solve(assumptions, on_model, on_statistics, on_finish, yield_, async_)

    def add(self, name: str, parameters: List[str], program: str) -> None:
        self.control.add(name, parameters, program)
        rules = self.transformer.transform(program)
        self.anotherOne = AnotherOne(rules)
        print(f"Created {len(rules)} rules:\n{rules}")

    def paint(self):
        if self.anotherOne:
            g = self.anotherOne.make_graph()
            annotate_edges_in_nodes(g, (0,INITIAL_EMPTY_SET))
            print(f"Painting graph with {len(g)} nodes.")
            display = HeadlessPysideDisplay(g)
            pic = display.get_graph_as_np_array()
            return pic
        else:
            print("NO SOLVE RUNNER")

    def _show(self, pic):
        if len(pic):
            plt.imshow(pic)
            plt.show()
        else:
            print("PIC IS NONE")


class Dingo(Control):

    def __init__(self, arguments: List[str] = [], logger=None, message_limit: int = 20):
        self.control = Control(arguments, logger, message_limit)
        self.debuggo = Control(arguments, logger, message_limit)
        self.solveRunner = SolveRunner("", self.debuggo)
        self.transformer = HeadBodyTransformer()

    def paint(self, model: Model) -> None:
        self.display = HeadlessPysideDisplay(self.solveRunner.graph)
        return self.display.get_graph_as_np_array()

    def add(self, name: str, parameters: List[str], program: str) -> None:
        # TODO: prettify this.
        self.control.add(name, parameters, program)
        _ = self.transformer.transform(program)
        self.solveRunner.program = program
        reified_program = self.transformer.get_reified_program_as_str()
        print(reified_program)
        self.debuggo.add(name, parameters, reified_program)

    def ground(self, parts: List[Tuple[str, List[Symbol]]], context: Any = None) -> None:
        print("Grounding..")
        self.control.ground(parts, context)
        self.debuggo.ground(parts, context)
        print("Done.")

    def solve(self, assumptions: List[Union[Tuple[Symbol, bool], int]] = [],
              on_model=None,
              on_statistics=None,
              on_finish=None,
              yield_: bool = False,
              async_: bool = False) -> Union[SolveHandle, SolveResult]:
        self.solveRunner.step_until_stable()
        return self.control.solve(assumptions, on_model, on_statistics, on_finish, yield_, async_)


def _main():
    prg = "s(1..2). {b} :- s(X), X == 2. c :- b. :- c."
    ctl = Debuggo()

    #
    # g = ctl.anotherOne.make_graph()
    # annotate_edges_in_nodes(g, (0, INITIAL_EMPTY_SET))
    #
    # app = QApplication(sys.argv)
    #
    # layout = QHBoxLayout()
    # w = PySideDisplay(g)
    # # QWidget
    #
    # # QMainWindow using QWidget as central widget
    # window = MainWindow(w)
    #
    # window.show()
    # sys.exit(app.exec_())


if __name__ == "__main__":
    _main()
