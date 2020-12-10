import sys

from PySide2.QtWidgets import QApplication, QHBoxLayout
from clingo import Control, Symbol, StatisticsMap, Model, SolveHandle, SolveResult
from debuggo.transform.transform import HeadBodyTransformer, JustTheRulesTransformer
from debuggo.display.graph import HeadlessPysideDisplay, PySideDisplay, MainWindow, NetworkxDisplay
from debuggo.solve.solver import SolveRunner, SolveRunner, annotate_edges_in_nodes, INITIAL_EMPTY_SET
from typing import List, Tuple, Any, Union
import matplotlib.pyplot as plt
import networkx as nx


class Debuggo(Control):
    def add_to_painter(self, model):
        if not hasattr(self, "painter"):
            self.painter = list()
        self.painter.append(set(model))


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
        print(f"Recieved {len(rules)} rules from transformer:\n{rules}")
        self.anotherOne = SolveRunner(rules)
        print(f"Created {len(rules)} rules:\n{rules}")

    def find_nodes_corresponding_to_stable_models(self, g, stable_models):
        correspoding_nodes = set()
        for model in stable_models:
            for node in g.nodes():
                print(f"{node} {type(node.model)} == {model} {type(model)} -> {set(node.model) == model}")
                if set(node.model) == model and len(g.edges(node)) == 0: # This is a leaf
                    print(f"{node} <-> {model}")
                    correspoding_nodes.add(node)
                    break
        return correspoding_nodes

    def prune_graph_leading_to_models(self, graph, models_as_nodes):
        before = len(graph)
        relevant_nodes = set()
        for model in models_as_nodes:
            for relevant_node in nx.all_simple_paths(graph, INITIAL_EMPTY_SET, model):
                print(f"???{relevant_node}")
                relevant_nodes.update(relevant_node)
        all_nodes = set(graph.nodes())
        irrelevant_nodes = all_nodes - relevant_nodes
        graph.remove_nodes_from(irrelevant_nodes)
        after = len(graph)
        print(f"Removed {before-after} of {before} nodes ({(before-after)/before})")


    def paint(self):
        g = self.anotherOne.make_graph()
        if hasattr(self, "painter"):
            # User decided to print specific models.
            interesting_nodes = self.find_nodes_corresponding_to_stable_models(g, self.painter)
            self.prune_graph_leading_to_models(g, interesting_nodes)
        # we simply print all
        display = NetworkxDisplay(g)
        img = display.draw()
        return img




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
    prg = "a. {b} :- a."
    ctl = Debuggo()
    ctl.add("base", [], prg)
    x = ctl.paint()

    plt.imshow(x)
    plt.show()
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
