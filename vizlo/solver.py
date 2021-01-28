from typing import List, Set, Union

import clingo
import networkx as nx

from clingo import Control, Symbol

from vizlo.types import ASTRuleSet, FlatASTProgram, ASTProgram

EMERGENCY_EXIT_COUNTER = 0


def get_all_trues_from_assumption(assumptions) -> Set[Symbol]:
    return set(atom for atom, truth in assumptions if truth)


class SolverState:
    """
    Represents a single solver state that is created during execution.
    A SolverState consists of the current stable model, what became true and what became false
    after the last step.
    """

    def __init__(self, model: Set, is_still_active, step: int = -1, falses: Set = set(), adds=set()):
        if isinstance(model, list):
            model = set(model)
        self.model: Set = model
        self.step: int = step
        self.falses: Set = falses
        self.is_still_active: bool = is_still_active
        self.adds: Union[Set, None] = adds

    def __repr__(self):
        return f"{self.model}"

    def __eq__(self, other):
        if isinstance(other, SolverState):
            return self.model == other.model and self.step == other.step
        return False

    def __hash__(self):
        return id(self)

    def is_still_a_candidate(self) -> bool:
        return self.step == 0 or len(self.model) > 0


class OneSolveMaker:

    def __init__(self, main, ctl: clingo.Control, rule: ASTRuleSet, symbols_in_heads=set()):
        self.main = main
        self.ctl = ctl
        self.rule = rule
        self.singatures_in_heads = symbols_in_heads

    def run(self, i):
        # analytically find recursive components and add them at once
        partial_models = self.main.find_nodes_at_timestep(i)
        print(f"{self.rule} with {len(partial_models)} previous partial models.")
        for partial_model in partial_models:
            # print(f"Continuing with {partial_model}")
            assumptions = self.create_true_symbols_from_solver_state(partial_model)
            assumptions.extend(self.main.global_assumptions)
            print(f"Assumptions: {assumptions}")
            new_partial_models = self._get_new_partial_models(assumptions, self.ctl, i)
            _consolidate_new_solver_states(assumptions, new_partial_models)
            self.main.update_graph(partial_model, self.rule, new_partial_models)

    def _get_new_partial_models(self, assumptions, ctl, i):
        solver_states_to_create = []
        with ctl.solve(assumptions=assumptions, yield_=True) as handle:
            hacky_counter = 0
            for m in handle:
                model = set(m.symbols(atoms=True))
                adds = model - get_all_trues_from_assumption(assumptions)
                syms = SolverState(m.symbols(atoms=True), True, i + 1, adds=adds)
                print(f"{assumptions} yielded {syms}")
                solver_states_to_create.append(syms)
                hacky_counter += 1
            if hacky_counter == 0:
                # HACK: This means the candidate model became conflicting.
                print(f"Unsatisfiable partial model {assumptions} at step {i}.")
                solver_states_to_create.append(SolverState(set(), False, i + 1))
            print(f"Is conflicting: {ctl.is_conflicting}")
            handle.wait()  # TODO: Necessary??
            result = handle.get()
            print(f"Solve Result: {result} ({hacky_counter})")
            print(f"{result.satisfiable}")
        return solver_states_to_create

    def create_true_symbols_from_solver_state(self, s):
        syms = []
        for true in s.model:
            syms.append((true, True))
        for false in s.falses:
            print(f"Sigs: {self.singatures_in_heads}")
            if not any((false.match(s[0], s[1]) for s in self.singatures_in_heads)):
                syms.append((false, False))
        return syms

def update_falses_in_solver_states(sss):
    all_possible = set()
    for s in sss:
        all_possible.update(s.model)
    print(f"All atoms that have been added in this time step: {all_possible}")
    for s in sss:
        falses = all_possible - set(s.model)
        s.falses = falses


def assert_falses_from_assumptions(syms: List[SolverState], assumpts):
    for sym in syms:
        for atom, value in assumpts:
            print(f"Updating {sym} with {atom}={value}")
            if not value:
                sym.falses.add(atom)


def _consolidate_new_solver_states(assumpts, solver_states_to_create):
    update_falses_in_solver_states(solver_states_to_create)
    assert_falses_from_assumptions(solver_states_to_create, assumpts)


def _make_new_control_and_ground(current_prg: FlatASTProgram) -> Control:
    prg_as_str = " ".join([str(rule) for rule in current_prg])
    print(f"Creating Control for \'{prg_as_str}\'")
    ctl = clingo.Control(["0"])
    ctl.add("base", [], prg_as_str)
    ctl.ground([("base", [])])
    return ctl


class SolveRunner:
    def __init__(self, program: ASTProgram, global_assumptions=None, symbols_in_heads_map=dict()):
        self.EMERGENCY_EXIT_COUNTER = 0
        self.prg: ASTProgram = program
        print(f"Created AnotherOne with {len(self.prg)} rules and {symbols_in_heads_map} sigs.")
        self.global_assumptions = global_assumptions if global_assumptions is not None else set()
        self._g: nx.Graph = nx.DiGraph()
        self._g.add_node(INITIAL_EMPTY_SET)
        self._solvers: List[OneSolveMaker] = []
        current_prg: FlatASTProgram = []
        self.symbols_in_heads_map = symbols_in_heads_map

        for rule_set in self.prg:
            current_prg.extend(rule_set)
            print(rule_set)
            ctl = _make_new_control_and_ground(current_prg)
            signatures_of_heads = set()
            for rule in rule_set:
                signatures_of_heads.update(symbols_in_heads_map.get(str(rule), set()))
            self._solvers.append(OneSolveMaker(self, ctl, rule_set, signatures_of_heads))

    def find_nodes_at_timestep(self, step: int) -> List[SolverState]:
        nodes: List[SolverState] = []
        for node in self._g:
            print(f"{node} at {node.step}")
            if node.step == step and node.is_still_active:
                nodes.append(node)
        return nodes

    def make_graph(self):
        for i, s in enumerate(self._solvers):
            s.run(i)
        return self._g

    def update_graph(self, assmpts, rule, solver_states_to_create):
        for ss in solver_states_to_create:
            self._g.add_edge(assmpts, ss, rule=rule)



INITIAL_EMPTY_SET = SolverState(model=set(), is_still_active=True, step=0)
