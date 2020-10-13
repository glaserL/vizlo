
import clingo
import networkx as nx
import logging



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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.program = program
        ctl = clingo.Control()
        ctl.add("base", [], program)
        self.logger.info("Configured SolveRunner.")
        self.ctl = ctl
        self.logger.info("Performing initial grounding..")
        self.ground()
        self.logger.info(". DONE")
        self.graph: nx.Graph() = nx.Graph()
        self.isStable = False
        self.prev = None
        self.current_model = None
        self._step_count = 0
    
    def ground(self):
        self.ctl.ground([("base", [])])

    def update_externals(self, externals):
        for ext in externals:
            self.logger.info(f"Setting {ext.name} to {ext.positive}.")
            self.ctl.assign_external(ext, ext.positive)

    def add_model_to_history(self, model):
        if (self.prev != None):
            self.logger.info(f"Adding ({self.prev})->({model})")
            self.graph.add_edge(self.prev, model)
        else:
            print(f"Adding ({model})")
            self.graph.add_node(model)
        self.prev = model

    def solver_has_reached_stable_model(self):
        if self.current_model == self.prev:
            self.logger.error("Solver has reached a stable model.")
            return True
        else:
            print("Solving..")
            return False 
    
    def step_until_stable(self):
        while not self.solver_has_reached_stable_model():
            self.step()
    
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
        self.current_model = SolverState(self.remove_holds_atoms_from_model(symbols_in_model), self._step_count)
        if (not self.solver_has_reached_stable_model()):
            
            self.add_model_to_history(self.current_model)

            self.update_externals(true_externals)
        self._step_count += 1

    
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
