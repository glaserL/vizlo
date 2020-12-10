import sys
from copy import copy
from typing import List, Dict

import clingo
import networkx as nx
import logging

EMERGENCY_EXIT_COUNTER = 0
RuleSet = List[str]
Program = List[RuleSet]


class SolverState():
    """
    Represents a single solver state that is created during execution.
    A SolverState consists of the current stable model, what became true and what became false
    after the last step.

    TODO: Also try to represent multi-model stable models
    """

    def __init__(self, model, step=-1, falses=set()):
        self.model = model
        self.step = step
        self.falses = falses

    def __repr__(self):
        return f"{self.model}"

    def __eq__(self, other):
        if isinstance(other, SolverState):
            return self.model == other.model
        return False

    def __hash__(self):
        return id(self)


class SolveRunner():

    def __init__(self, program: Program):
        self.EMERGENCY_EXIT_COUNTER = 0
        self.ctls = self.generate_ctl_objects_for_rules(program)
        self.prg: Program = program
        print(f"Created AnotherOne with {len(self.prg)} rules.")
        print(f"{self.ctls}")
        self._g: nx.Graph = nx.DiGraph()

    def generate_ctl_objects_for_rules(self, program: Program) -> Dict[str, clingo.Control]:
        ctls = {}
        partial_program = []
        for rule_set in program:
            print(ctls)
            if len(rule_set) > 1:
                for rule in rule_set:
                    print(f"Adding {rule}")
                    tmp_list = partial_program.copy()
                    tmp_list.append(rule)
                    ctls[rule] = tmp_list.copy()
#                    ctls[rule] = self._make_new_control_and_ground(tmp_list)
                partial_program.extend(rule_set)
            else:
                rule = rule_set[-1]
                partial_program.append(rule)
                # print(f"Create partial program for {partial_program}")
                ctls[rule] = self._make_new_control_and_ground(partial_program)
                ctls[rule] = partial_program.copy()
        print(f"Created {len(ctls)} Control objects for {len(program)} rule sets.")
        return ctls

    def find_nodes_at_timestep(self, step: int) -> List[SolverState]:
        nodes: List[SolverState] = []
        for node in self._g:
            print(f"{node} at {node.step}")
            if node.step == step:
                nodes.append(node)
        return nodes

    # TODO: move this into solverstate class?
    def create_true_symbols_from_solver_state(self, s):
        syms = []
        for true in s.model:
            syms.append((true, True))
        for false in s.falses:
            syms.append((false, False))
        return syms

    # TODO: move this into solverstate class as a classmethod?
    def update_falses_in_solver_states(self, sss):
        all_possible = set()
        for s in sss:
            all_possible.update(s.model)
        print(f"All atoms that have been added in this time step: {all_possible}")
        for s in sss:
            falses = all_possible - set(s.model)
            s.falses = falses

    def do_one_rule(self, rule, partial_model, i) -> bool:
        print(f"Doing rule {rule} for {partial_model} at step {i}")
        assumptions = self.create_true_symbols_from_solver_state(partial_model)
        print(f"Assumption: {assumptions}")
        ctl = self._get_ctl_for_rule(rule)
        print(f"Working with {ctl}")
        new_partial_models = self._get_new_partial_models(assumptions, ctl, i)
        print(f"Recieved new_partial_models: {new_partial_models}")
        if len(new_partial_models) and any(new_partial_model != partial_model for new_partial_model in new_partial_models):
            print(f"Change in models occured: {new_partial_models}")
            self._consolidate_new_solver_states(assumptions, new_partial_models)
            self._update_graph(partial_model, rule, new_partial_models)
            return True
        else:
            return False

    def _recursive2(self, rule_set, i):
        if self.EMERGENCY_EXIT_COUNTER > 100:
            print("HUGE RECURSIVE DEPTH")
            sys.exit(1)
        else:
            self.EMERGENCY_EXIT_COUNTER += 1

        partial_models: List[SolverState] = self.find_nodes_at_timestep(i)
        print(f"Partial models: {partial_models}, applied on {rule_set} at timestep {i}")
        results: List[bool] = []

        for partial_model in partial_models:
            for rule in rule_set:
                print(f"Calling do one rule with {rule}, {partial_model} and {i}")
                results.append(self.do_one_rule(rule, partial_model, i))
                print(f"did sth")
        print(f"results: {results}")
        if any(results):
            print(f"Next! {rule_set} at {i+1}")
            self._recursive2(rule_set, i + 1)

    def make_graph2(self):
        print(f"Making graph2")
        self._g.add_node(INITIAL_EMPTY_SET)
        for i, rule_set in enumerate(self.prg):
            self._recursive2(rule_set, i)
        return self._g

    def _recursive(self, partial_model, rule, all_rules, i):
        if (i > 20):
            return
        assumptions = self.create_true_symbols_from_solver_state(partial_model)
        ctl = self._get_ctl_for_rule(rule)
        new_partial_models = self._get_new_partial_models(assumptions, ctl, i)
        if assumptions == new_partial_models:  # this didnt add anything
            return False
        else:
            self._consolidate_new_solver_states(assumptions, new_partial_models)
            self._update_graph(partial_model, rule, new_partial_models)
            did_below_return_anything = []
            for new_partial_model in new_partial_models:
                for other_rule in all_rules:
                    if other_rule != rule:
                        did_below_return_anything.append(
                            self._recursive(new_partial_model, other_rule, all_rules, i + 1))
            return True

    def make_graph(self):

        # TODO: REFACTOR THIS FUCKING ABOMINATION

        self._g.add_node(INITIAL_EMPTY_SET)
        current_prg: List[str] = []
        for i, rule in enumerate(self.prg):
            print(f"========{i}========Adding rule {rule}")
            current_prg.extend(rule)
            ctl = self._make_new_control_and_ground(current_prg)
            # analytically find recursive components and add them at once
            partial_models = self.find_nodes_at_timestep(i)
            print(f"{rule} with {len(partial_models)} previous partial models.")
            for partial_model in partial_models:
                # print(f"Continuing with {partial_model}")
                assumptions = self.create_true_symbols_from_solver_state(partial_model)
                print(f"Assumptions: {assumptions}")
                new_partial_models = self._get_new_partial_models(assumptions, ctl, i)
                self._consolidate_new_solver_states(assumptions, new_partial_models)
                self._update_graph(partial_model, rule, new_partial_models)
        return self._g

    def _get_new_partial_models(self, assumptions, ctl, i):
        solver_states_to_create = []
        for x in ctl.symbolic_atoms.by_signature("y",1):
            print(x.symbol, x.is_fact, x.is_external)
        print(f"Symbolic atoms: {ctl.symbolic_atoms}")
        with ctl.solve(assumptions=assumptions, yield_=True) as handle:
            hacky_counter = 0
            for m in handle:
                print(f"Model in handle:{m}")
                syms = SolverState(m.symbols(atoms=True), i + 1)
                print(f"{assumptions} yielded {syms}")
                solver_states_to_create.append(syms)
                hacky_counter += 1
            if hacky_counter == 0:
                # HACK: This means the candidate model became conflicting.
                print(f"Something broke on {assumptions} at {i}")
                solver_states_to_create.append(SolverState(set()))
            handle.wait()
            handle.get()
        return solver_states_to_create

    def _update_graph(self, assmpts, rule, solver_states_to_create):
        for ss in solver_states_to_create:
            self._g.add_edge(assmpts, ss, rule=rule)

    def _consolidate_new_solver_states(self, assumpts, solver_states_to_create):
        self.update_falses_in_solver_states(solver_states_to_create)
        self.assert_falses_from_assumptions(solver_states_to_create, assumpts)

    def _make_new_control_and_ground(self, current_prg):
        prg_as_str = "\n".join(current_prg)
        print(f"Creating Control for \'{prg_as_str}\'")
        ctl = clingo.Control("0")
        ctl.add("base", [], prg_as_str)
        ctl.ground([("base", [])])
        return ctl

    def assert_falses_from_assumptions(self, syms: List[SolverState], assumpts):
        for sym in syms:
            for atom, value in assumpts:
                print(f"Updating {sym} with {atom}={value}")
                if not value:
                    sym.falses.add(atom)

    def _get_ctl_for_rule(self, rule: str) -> clingo.Control:
        print(f"Getting ctl for {rule}")
        corresponding_prg = self.ctls[rule]
        corresponding_ctl = self._make_new_control_and_ground(corresponding_prg)

#        corresponding_ctl.ground([("base", [])])
        print(f"Returning {corresponding_prg} for {rule}")
        return corresponding_ctl


def annotate_edges_in_nodes(g, begin):
    path_id = 0
    prev_step = 0
    for node in nx.bfs_tree(g, begin):
        if prev_step != node.step:
            print(f"Resetting {path_id}.")
            path_id = 0
        print(f"Setting {path_id}")
        node.path = path_id
        prev_step = node.step
        path_id += 1
    for node, target in nx.dfs_edges(g, begin):
        print(f"{node, node.step, node.path} -[{g[node][target]}]> {target, target.step, node.path}")
    return g


INITIAL_EMPTY_SET = SolverState(model=set(), step=0)
