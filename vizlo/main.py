import clingo
from clingo import Control, Symbol, Model, SolveHandle, SolveResult
from vizlo.transform import JustTheRulesTransformer
from vizlo.graph import NetworkxDisplay
from vizlo.solver import SolveRunner, INITIAL_EMPTY_SET
from typing import List, Tuple, Any, Union, Set, Collection, Dict
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


def make_global_assumptions(universe: Set[Symbol], models: Collection[PythonModel]) -> List[Set[Tuple[Symbol, bool]]]:
    assumption_sets: List[Set[Tuple[Symbol, bool]]] = []
    for model in models:
        assumption_set = set(((symbol, False) for symbol in universe if not symbol in model.model))
        assumption_set.update(set(((symbol, True) for symbol in universe if symbol in model.model)))
        assumption_sets.append(assumption_set)

    return assumption_sets


class VizloControl(Control):

    def add_to_painter(self, model: Union[Model, PythonModel, Collection[clingo.Symbol]]):
        """
        will register model with the internal painter. On all consecutive calls to paint(), this model will be painted.
        :param model: the model to add to the painter.
        :return:
        """
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
            solve_runner = SolveRunner(program, t.rule2signatures)
            g = solve_runner.make_graph(global_assumptions)
        else:
            solve_runner = SolveRunner(program, symbols_in_heads_map=t.rule2signatures)
            g = solve_runner.make_graph()
        return g

    def paint(self, atom_draw_maximum: int = 20, show_entire_model: bool = False, sort_program: bool = True, **kwargs):
        """
         Will create a graph visualization of the solving process. If models have been added using add_to_painter,
         only the solving paths that lead to these models will be drawn.
         :param atom_draw_maximum: int
             The maximum amount of atoms that will be printed for each partial model. (default=20)
         :param show_entire_model: bool
             If false, only the atoms that have been added at a solving step will be printed (up to atom_draw_maximum).
             If true, all atoms will always be printed (up to atom_draw_maximum). (default=False)
         :param sort_program:
             If true, the rules of a program will be sorted and grouped by their dependencies.
             Each set of rules will contain all rules in which each atom in its heads is contained in a head.
         :param kwargs:
             kwargs will be forwarded to the visualisation module. See graph.draw()
         :return:
         """
        if type(atom_draw_maximum) != int:
            raise ValueError(f"Argument atom_draw_maximum should be an integer (received {atom_draw_maximum}).")
        g = self._make_graph(sort_program)
        display = NetworkxDisplay(g, atom_draw_maximum, not show_entire_model)
        img = display.draw(**kwargs)
        return img

    def _add_and_ground(self, prg):
        """Short cut for complex add and ground calls, should only be used for debugging purposes."""
        self.add("base", [], prg)
        self.ground([("base", [])])
