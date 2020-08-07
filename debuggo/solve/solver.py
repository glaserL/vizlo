
import clingo
import networkx as nx


class Solver():
    
    def __init__(self, stable_models):
        self.stable_models = stable_models

    def get_branch(self, head, stable_models):
        trues, falses = [], []
        for stable_model in stable_models:
            if head in stable_model:
                trues.append(stable_model)
            else:
                falses.append(stable_model)
        return trues, falses

    def next_try(self, prev_stack_until_now, definition_history, i):
        trues, falses = self.get_branch(definition_history[i], self.stable_models)
        # abbruch bedingung
        if i == len(definition_history) - 1:
            final_paths = []
            if len(trues):
                new_path = prev_stack_until_now + [definition_history[i]]
                final_paths.append(new_path)
            if len(falses):
                new_path = prev_stack_until_now + [f"not_{definition_history[i]}"]
                final_paths.append(new_path)
            return final_paths
        else:
            paths = []
            if len(trues):
                new_path = prev_stack_until_now + [definition_history[i]]
                paths.extend(self.next_try(new_path, definition_history, i+1))
            if len(falses):
                new_path = prev_stack_until_now + [f"not_{definition_history[i]}"]
                paths.extend(self.next_try(new_path, definition_history, i+1))
            return paths

    def generate_path(self, definition_history):
        paths = self.next_try([], definition_history, 0)
        return paths



class SolveRunner():
    """
    Interacts with the clingo solver to produce a full solving history. 
    """
    def __init__(self, program):
        self.program = program
        ctl = clingo.Control()
        ctl.add("base", [], program)
        print("Configured SolveRunner.")
        self.ctl = ctl
        print("Performing initial grounding..",end="")
        self.ground()
        print(". DONE")
        self.history = []
        self.graph: nx.Graph() = nx.Graph()
        self.isStable = False
        self.prev = None
    
    def next(self):

        pass

    def solve(self):
        with self.ctl.solve(yield_=True) as handle:
            for m in handle:
                for symbol in m.symbols(atoms=True):
                    head = symbol.arguments[0]

    def ground(self):
        self.ctl.ground([("base", [])])

    def update_externals(self, externals):
        for ext in externals:
            print(f"Setting {ext.name} to {ext.positive}.")
            self.ctl.assign_external(ext, ext.positive)

    def update_and_solve(self, externals):
        self.update_externals(externals)
        self.solve()

    def step(self):
        #ctl.solve(on_model=on_model)
        true_externals = []
        with self.ctl.solve(yield_=True) as handle:
            for m in handle:
                symbols_in_model = m.symbols(atoms=True)
                print(f"Found {len(symbols_in_model)} symbols in model.")
                for symbol in symbols_in_model:
                    # TODO: match expression here??
                    if len(symbol.arguments)>0:
                        head = symbol.arguments[0]
                        true_externals.append(head)
                #ctl.assign_external(clingo.String("d"),True)
        
        sose = SolverState.create_state_from_old_and_new_model(self.history, symbols_in_model)
        only_atoms = self.remove_holds_atoms_from_model(symbols_in_model)
        if (self.prev != None):
            self.graph.add_edge(self.prev, only_atoms)
        else:
            self.graph.add_node(only_atoms)
        self.prev = only_atoms

        # TODO: Update here if we reached the stable model
        self.history.append(sose)
        for ext in true_externals:
            print(f"Setting {ext.name} to {ext.positive}.")
            self.ctl.assign_external(ext,ext.positive)
    
    def remove_holds_atoms_from_model(self, model):
        cleaned_model = set()
        for symbol in model:
            if not symbol.name == "h":
                cleaned_model.add(symbol)
        return frozenset(cleaned_model)
    

class SolverState():
    """ 
    Represents a single solver state that is created during execution. 
    A SolverState consists of the current stable model, what became true and what became false
    after the last step.

    TODO: Also try to represent multi-model stable models
    """

    def __init__(self, model, added_trues, added_falses):
        self.model = model
        self.added_trues = added_trues
        self.added_falses = added_falses
    
    def __repr__(self):
        return f"SolverState{{\n\t{self.model}\n\t+{self.added_trues}\n\t-{self.added_falses}\n}}"

    @staticmethod
    def create_state_from_old_and_new_model(history, symbols):
        if len(history)==0:
            return SolverState(set(symbols),set(),set())
        else:
            previous: SolverState = history[-1]
            symbols_as_set = set(symbols)
            assert len(list(symbols_as_set)) == len(symbols)

            added_trues = symbols_as_set.difference(previous.model)
            added_falses = previous.model.difference(symbols_as_set)
            return SolverState(symbols_as_set, added_trues, added_falses)
