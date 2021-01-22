import sys

import clingo
from clingo import Control, Symbol, StatisticsMap, Model, SolveHandle, SolveResult
from debuggo.transform.transform import JustTheRulesTransformer
from debuggo.display.graph import NetworkxDisplay, assert_no_bi_edges
from debuggo.solve.solver import SolveRunner, SolveRunner, INITIAL_EMPTY_SET
from typing import List, Tuple, Any, Union, Set, Collection
import matplotlib.pyplot as plt
import networkx as nx

# Types
# TODO: can you add them to a single file and import them from child folders?
RuleSet = List[str]
Program = List[RuleSet]


def program_to_string(program: Program) -> str:
    prg = ""
    for ruleSet in program:
        prg += "\n".join([str(rule) for rule in ruleSet])
    return prg

class PythonModel():
    """"Lazy model that allows us to store stuff from a clingo model in python"""
    def __init__(self, model : Union[Model, Set[Symbol]]):
        if isinstance(model, Model):
            self.model : Set[Symbol] = model.symbols(atoms=True)
        else:
            self.model = model

    def __iter__(self):
        return iter(self.model)

def get_ground_universe(program : Program) -> Set[Symbol]:
    prg = program_to_string(program)
    ctl = Control()
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ground_universe = set([ground_atom.symbol for ground_atom in ctl.symbolic_atoms])
    print(f"Ground universe: {ground_universe}")
    return ground_universe

def extract_ground_universe_from_control(ctl : Control) -> Set[Symbol]:
    return set([ground_atom.symbol for ground_atom in ctl.symbolic_atoms])

def make_global_assumptions(universe : Set[Symbol], models : Collection[PythonModel]) -> Set[Tuple[Symbol, bool]]:
    true_symbols : Set[Symbol] = set()
    for model in models:
        true_symbols.update(model.model)
    print(f"Global truths: {true_symbols}")
    global_assumptions = set(((symbol, False) for symbol in universe if not symbol in true_symbols))
    print(f"Global assumptions: {global_assumptions}")
    return global_assumptions

class Debuggo(Control):

    def add_to_painter(self, model: Union[Model, PythonModel]):
        self.painter.append(PythonModel(model))


    def __init__(self, arguments: List[str] = [], logger=None, message_limit: int = 20):
        self.control = Control(arguments, logger, message_limit)
        self.painter : List[PythonModel] = list()
        self.program : Program = list()
        self.transformer = JustTheRulesTransformer()
        self._print_changes_only = True

    def _set_print_only_changes(self, value: bool) -> None:
        self._print_changes_only = value

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
        new_rules = self.transformer.transform(program)
        self.program.extend(new_rules)
        print(f"Recieved {len(new_rules)} rules from transformer:\n{new_rules}")

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

    def make_graph(self):
        if len(self.painter):
            universe = get_ground_universe(self.program)
            global_assumptions = make_global_assumptions(universe, self.painter)
            solve_runner = SolveRunner(self.program, global_assumptions)
        else:
            solve_runner = SolveRunner(self.program)
        # if len(self.painter):
        #     # User decided to print specific models.
        #
        #     interesting_nodes = self.find_nodes_corresponding_to_stable_models(g, self.painter)
        #     self.prune_graph_leading_to_models(g, interesting_nodes)
        # # we simply print all
        g = solve_runner.make_graph()
        return g
    def paint(self):
        g = self.make_graph()
        display = NetworkxDisplay(g)
        img = display.draw()
        return img

    def add_and_ground(self, prg):
        """Short cut for complex add and ground calls, should only be used for debugging purposes.s"""
        self.add("base", [], prg)
        self.ground([("base", [])])


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
