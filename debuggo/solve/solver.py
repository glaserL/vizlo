
import clingo
import networkx as nx
import logging




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

    def __init__(self, model, step = -1):
        self.model = model
        self.step = step

    def __repr__(self):
        return f"{self.model}"

    def __eq__(self, other):
        if isinstance(other, SolverState):
            return self.model == other.model
        return False

    def __hash__(self):
        return id(self)
