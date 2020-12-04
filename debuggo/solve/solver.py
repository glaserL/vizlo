from typing import List

import clingo
import networkx as nx
import logging


class SolverState():
    """
    Represents a single solver state that is created during execution.
    A SolverState consists of the current stable model, what became true and what became false
    after the last step.

    TODO: Also try to represent multi-model stable models
    """

    def __init__(self, model, step = -1, falses=set()):
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

    def __init__(self, program : [str]): # TODO: Change this to clingo.Rule
        self.prg = [str(rule) for rule in program]
        print(f"Created AnotherOne with {len(self.prg)} rules.")
        self._g : nx.Graph = nx.DiGraph()


    def find_nodes_at_timestep(self, step : int):
        nodes = []
        for node in self._g:
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


    def _generate_with_recursive(self, base_program, initial_partial_model: SolverState, recursive_component):
        changed = True
        previous_partial_model = initial_partial_model
        while changed:
            for rule in recursive_component:
                # We call the recursive component with one of the recursive rules
                ctl = self._make_new_control_and_ground(base_program+rule)
                assumptions = self.create_true_symbols_from_solver_state(previous_partial_model)


    def make_graph(self):

        # TODO: REFACTOR THIS FUCKING ABOMINATION

        self._g.add_node(INITIAL_EMPTY_SET)
        current_prg = []
        for i, rule in enumerate(self.prg):
            print(f"========{i}========Adding rule {rule}")
            current_prg.append(rule)
            ctl = self._make_new_control_and_ground(current_prg)
            # analytically find recursive components and add them at once
            partial_models = self.find_nodes_at_timestep(i)
            print(f"{rule} with {len(partial_models)} previous partial models.")
            for partial_model in partial_models:
                #print(f"Continuing with {partial_model}")
                assumptions = self.create_true_symbols_from_solver_state(partial_model)
                print(f"Assumptions: {assumptions}")
                new_partial_models = self._get_new_partial_models(assumptions, ctl, i)
                self._consolidate_new_solver_states(assumptions, new_partial_models)
                self._update_graph(partial_model, rule, new_partial_models)
        return self._g

    def _get_new_partial_models(self, assumptions, ctl, i):
        solver_states_to_create = []
        with ctl.solve(assumptions=assumptions, yield_=True) as handle:
            hacky_counter = 0
            for m in handle:
                syms = SolverState(m.symbols(atoms=True), i + 1)
                # print(f"({partial_model})-[{rule}]->({(i + 1, syms)})")
                solver_states_to_create.append(syms)
                hacky_counter += 1
            if hacky_counter == 0:
                # HACK: This means the candidate model became conflicting.
                solver_states_to_create.append(SolverState(set()))
        return solver_states_to_create

    def _update_graph(self, assmpts, rule, solver_states_to_create):
        for ss in solver_states_to_create:
            self._g.add_edge(assmpts, ss, rule=rule)

    def _consolidate_new_solver_states(self, assumpts, solver_states_to_create):
        self.update_falses_in_solver_states(solver_states_to_create)
        self.assert_falses_from_assumptions(solver_states_to_create, assumpts)

    def _make_new_control_and_ground(self, current_prg):
        ctl = clingo.Control("0")
        ctl.add("base", [], "\n".join(current_prg))
        ctl.ground([("base", [])])
        return ctl

    def assert_falses_from_assumptions(self, syms: List[SolverState], assumpts):
        for sym in syms:
            for atom, value in assumpts:
                print(f"Updating {sym} with {atom}={value}")
                if not value:
                    sym.falses.add(atom)


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
