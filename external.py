from clingo import Function, Number, String, Tuple
import random
import os

class Solver():

    def __init__(self):
        self.all_atoms = []
        self.current_models = []

    def solve(self):
        self.current_models.clear()
        for number_of_models in range(random.randint(1,len(self.all_atoms))):
            new_model = []
            for number_of_atoms in range(random.randint(0, len(self.all_atoms))):
                new_model.append(self.all_atoms[number_of_atoms])
            self.current_models.append(new_model)
    def add(self, atom):
        self.all_atoms.append(atom)

    def stable_models(self):
        return self.current_models


def display_model_stack(model_stack, root_path):
    """This will display the generation stack of a model recursively"""
    if not os.path.exists(root_path):
        os.mkdir(root_path)
        

def compute_diff(before, after):
    """Computes the changes of atoms between two models"""
    adds, deletes = [], []
    for bf in before:
        if not bf in after:
            deletes.append(bf)
    for af in after:
        if not af in before:
            adds.append(af)
    return adds, deletes


class h:
    def __init__(self, head, id, body):
        self.head = head
        self.id = id
        self.body = body

sample_input = [
    Function("h", [String("a"), Number(1), Tuple("b")]),
    Function("h", [String("b"), Number(2), Tuple("c")]),
    Function("h", [String("c"), Number(3), Tuple("d")]),
    Function("h", [String("d"), Number(4), Tuple("")])
]
# Above should encode h(a,1,(b)), ..., it doesn't, right?

solver = Solver()
solving_history = []
previous = []
for rule in sample_input:
    print(f"Adding rule {rule} to solver") # This isn't really correct? Use a SymbolicAtom I think
    solver.add(rule) # Add the rules that should now be 
    print("Solving..")
    solver.solve()
    current = solver.stable_models()[0] # we enforce on normal (?) programs without multiple stablemodels right now
    diff = compute_diff(previous, current)
    solving_history.append(diff)

print(solving_history)

#display_model_stack(solving_history, "stack")


# solving_history = []
# previous = []
# while solver.models_still_change:
#     solver.update_externals(previous)
#     current = solver.solve()
#     diff = compute_diff(previous, current)
#     solving_history.append(diff)

# display_model_stack(solving_history)