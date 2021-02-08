import clingo
from clingo import Control, Symbol, Model, SolveHandle, SolveResult
from vizlo.transform import JustTheRulesTransformer
from vizlo.graph import NetworkxDisplay
from vizlo.solver import SolveRunner, INITIAL_EMPTY_SET
from typing import List, Tuple, Any, Union, Set, Collection, Dict
import matplotlib.pyplot as plt
import networkx as nx

# Types
from vizlo.types import Program, ASTProgram
from vizlo.util import log


def program_to_string(program: Program) -> str:
    prg = ""
    for ruleSet in program:
        prg += "\n".join([str(rule) for rule in ruleSet])
    return prg


class PythonModel:
    """
    Container for both clingo.Model and Set[Symbol] to ease interaction.
    """

    def __init__(self, model: Union[Model, Set[Symbol]]):
        if isinstance(model, Model):
            self.model: Set[Symbol] = model.symbols(atoms=True)
        else:
            self.model = model

    def __iter__(self):
        return iter(self.model)


def get_ground_universe(program: Program) -> Set[Symbol]:
    prg = program_to_string(program)
    ctl = Control()
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ground_universe = set([ground_atom.symbol for ground_atom in ctl.symbolic_atoms])
    log(f"Ground universe: {ground_universe}")
    return ground_universe


def extract_ground_universe_from_control(ctl: Control) -> Set[Symbol]:
    return set([ground_atom.symbol for ground_atom in ctl.symbolic_atoms])


def make_global_assumptions(universe: Set[Symbol], models: Collection[PythonModel]) -> Set[Tuple[Symbol, bool]]:
    true_symbols: Set[Symbol] = set()
    for model in models:
        true_symbols.update(model.model)
    log(f"Global truths: {true_symbols}")
    global_assumptions = set(((symbol, False) for symbol in universe if not symbol in true_symbols))
    global_assumptions.update(set(((symbol, True) for symbol in universe if symbol in true_symbols)))
    log(f"Global assumptions: {global_assumptions}")
    return global_assumptions


class VizloControl(Control):

    def add_to_painter(self, model: Union[Model, PythonModel, Collection[clingo.Symbol]]):
        self.painter.append(PythonModel(model))

    def __init__(self, arguments: List[str] = [], logger=None, message_limit: int = 20, print_entire_models=False,
                 atom_draw_maximum=15):
        self.control = Control(arguments, logger, message_limit)
        self.painter: List[PythonModel] = list()
        self.program: ASTProgram = list()
        self.raw_programs: Dict[str, str] = {}
        self.raw_program: str = ""
        self.transformer = JustTheRulesTransformer()
        self._print_changes_only = not print_entire_models
        self._atom_draw_maximum = atom_draw_maximum

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
        self.raw_programs[name] = self.raw_programs.get(name, "") + program
        self.raw_program += program
        self.control.add(name, parameters, program)

    def find_nodes_corresponding_to_stable_models(self, g, stable_models):
        correspoding_nodes = set()
        for model in stable_models:
            for node in g.nodes():
                log(f"{node} {type(node.model)} == {model} {type(model)} -> {set(node.model) == model}")
                if set(node.model) == model and len(g.edges(node)) == 0:  # This is a leaf
                    log(f"{node} <-> {model}")
                    correspoding_nodes.add(node)
                    break
        return correspoding_nodes

    def prune_graph_leading_to_models(self, graph: nx.DiGraph, models_as_nodes):
        before = len(graph)
        relevant_nodes = set()
        for model in models_as_nodes:
            for relevant_node in nx.all_simple_paths(graph, INITIAL_EMPTY_SET, model):
                relevant_nodes.update(relevant_node)
        all_nodes = set(graph.nodes())
        irrelevant_nodes = all_nodes - relevant_nodes
        graph.remove_nodes_from(irrelevant_nodes)
        after = len(graph)
        log(f"Removed {before - after} of {before} nodes ({(before - after) / before})")

    def _make_graph(self, _sort=True):
        """
        Ties together transformation and solving. Transforms the already added program parts and creates a solving tree.
        :param _sort: Whether the program should be sorted automatically. Setting this to false will likely result into
        wrong results!
        :return:
        :raises ValueError:
        """
        if not len(self.raw_program):
            raise ValueError("Can't paint an empty program.")
        else:
            t = JustTheRulesTransformer()
            program = t.transform(self.raw_program, _sort)
        if len(self.painter):
            universe = get_ground_universe(program)
            global_assumptions = make_global_assumptions(universe, self.painter)
            solve_runner = SolveRunner(program, global_assumptions, t.rule2signatures)
        else:
            solve_runner = SolveRunner(program, symbols_in_heads_map=t.rule2signatures)
        g = solve_runner.make_graph()
        return g

    def paint(self, atom_draw_maximum=20, show_entire_model=False, sort_program=True, **kwargs):
        g = self._make_graph(sort_program)
        display = NetworkxDisplay(g, atom_draw_maximum, not show_entire_model)
        img = display.draw(**kwargs)
        return img

    def _add_and_ground(self, prg):
        """Short cut for complex add and ground calls, should only be used for debugging purposes."""
        self.add("base", [], prg)
        self.ground([("base", [])])
