
import clingo
import networkx as nx
import logging


class AnotherOne():

    def __init__(self, program : [str]): # TODO: Change this to clingo.Rule
        self.prg = [str(rule) for rule in program]
        print(f"Created AnotherOne with {len(self.prg)} rules.")
        self._g : nx.Graph = nx.DiGraph()


    def find_nodes_at_timestep(self, step):
        nodes = []
        for node in self._g:
            if node[0] == step:
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
        print(all_possible)
        for s in sss:
            falses = all_possible - set(s.model)
            s.falses = falses

    def make_graph(self):

        # TODO: REFACTOR THIS FUCKING ABOMINATION

        self._g.add_node((0,INITIAL_EMPTY_SET))
        current_prg = []
        for i, rule in enumerate(self.prg):
            print(f"Adding rule {rule}")
            current_prg.append(rule)
            ctl = clingo.Control("0")
            ctl.add("base", [], "\n".join(current_prg))
            ctl.ground([("base", [])])
            # analytically find recursive components and add them at once
            assumptions = self.find_nodes_at_timestep(i)
            print(f"{rule} with {len(assumptions)} assumpts.")
            for assmpts in assumptions:
                print(f"Continuing with {assmpts}")
                assumpts = self.create_true_symbols_from_solver_state(assmpts[1])
                print(f"Assumptions: {assumpts}")
                with ctl.solve(assumptions=assumpts, yield_=True) as handle:
                    solver_states_to_create = []
                    hacky_counter = 0
                    for m in handle:
                        print("!")
                        syms = SolverState(m.symbols(atoms=True), i)
                        print(f"({assmpts})-[{rule}]->({(i + 1, syms)})")
                        solver_states_to_create.append(syms)
                        hacky_counter += 1
                    if hacky_counter == 0:
                        # HACK: This means the candidate model became conflicting.
                        solver_states_to_create.append(SolverState(set()))
                    self.update_falses_in_solver_states(solver_states_to_create)
                    for ss in solver_states_to_create:
                        self._g.add_edge(assmpts, (i + 1, ss), rule=rule)
        return self._g

class StupidRunner():
    def __init__(self, rules : [str]):
        self.prg = rules
        self.graph: nx.Graph() = nx.DiGraph()


class SolveRunner():
    """
    Interacts with the clingo solver to produce a full solving history.
    """
    def __init__(self, program : str, control :clingo.Control):
        self.program = program
        self.ctl = control
        self.graph: nx.Graph() = nx.DiGraph()
        self.isStable = False
        self.prev = None
        self.current_model = None
        self._step_count = 0
        self.has_reached_stable_model = False

    def update_externals(self, externals):
        for ext in externals:
            print(f"Setting {ext.name} to {ext.positive}.")
            self.ctl.assign_external(ext, ext.positive)

    def add_model_to_history(self, model, rule):
        if (self.prev != None):
            print(f"Adding ({self.prev})-[{rule}]>({model})")
            self.graph.add_edge(self.prev, model, rule=rule)
        else:
            print(f"Adding ({model})")
            self.graph.add_node(model)
        self.prev = model

    def solver_has_reached_stable_model(self):
        print(self.current_model)
        print(self.prev)
        if self.current_model == self.prev:
            print("Solver has reached a stable model.")
            return True
        else:
            print("Solving..")
            return False

    def step_until_stable(self):
        while not self.has_reached_stable_model:
            self.step()

    def update(self, model, atoms_to_update, rule_nr):
        rule_edge = self.program.split("\n")[rule_nr-1]
        print(model)
        print(atoms_to_update)
        new_solver_state = SolverState(model, self._step_count)
        self.add_model_to_history(new_solver_state, rule_edge)
        self.update_externals(atoms_to_update)
        self._step_count += 1

    def step(self):
        current_model, atoms_to_update, rule_nr = self.get_changes_in_model()
        if not self.has_reached_stable_model:
            self.update(current_model, atoms_to_update, rule_nr)
        if len(atoms_to_update) == 0:
            self.has_reached_stable_model = True

    def get_changes_in_model(self):
        true_externals = []
        rule_no_because_of_which_true_externals_are_true = -1
        current_model = set()
        with self.ctl.solve(yield_=True) as handle:
            for m in handle:
                symbols_in_model = m.symbols(atoms=True)
                print(f"Found {len(symbols_in_model)} symbols in model.")
                for symbol in symbols_in_model:
                    # TODO: match expression here?? if we have more complex programs, below will be true for different things
                    if len(symbol.arguments)>0:
                        head = symbol.arguments[0]
                        print(f"head: {head}")
                        rule_no_because_of_which_true_externals_are_true = symbol.arguments[1].number
                        true_externals.append(head)
                    else:
                        # This is the "real model" without meta atoms
                        current_model.add(symbol)
        return current_model, true_externals, rule_no_because_of_which_true_externals_are_true


    def remove_holds_atoms_from_model(self, model):
        cleaned_model = set()
        for symbol in model:
            if not symbol.name == "h":
                cleaned_model.add(symbol)
        return cleaned_model


class SolverState():
    """
    Represents a single solver state that is created during execution.
    A SolverState consists of the current stable model, what became true and what became false
    after the last step.

    TODO: Also try to represent multi-model stable models
    """

    def __init__(self, model, step = -1,falses=set()):
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


def annotate_edges_in_nodes(g, begin):
    path_id = 0
    prev_step = 0
    for node in nx.bfs_tree(g, begin):
        node = node[1]
        if prev_step != node.step:
            print(f"Resetting {path_id}.")
            path_id = 0
        print(f"Setting {path_id}")
        node.path = path_id
        prev_step = node.step
        path_id += 1
    for node, target in nx.dfs_edges(g, begin):
        print(f"{node, node[1].step, node[1].path} -[{g[node][target]}]> {target, target[1].step, node[1].path}")
    return g

INITIAL_EMPTY_SET = SolverState(set(), 0)
