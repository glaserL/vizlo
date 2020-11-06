import clingo
import networkx as nx
from copy import copy
import matplotlib.pyplot as plt
class SolverState():
    """
    Represents a single solver state that is created during execution.
    A SolverState consists of the current stable model, what became true and what became false
    after the last step.

    TODO: Also try to represent multi-model stable models
    """

    def __init__(self, model, falses = set(), step = -1):
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

assumption_sets = []

g = nx.DiGraph()
#g.add_edge((0,""), (1,"p"), rule="p.")
g.add_node((0,SolverState([])))
prg = [
"p.",
"q :- p.",
"{r;t} :- q.",
"s :- r."
]
prg = [
"a.",
"{b(2)} :- a.",
"c :- b(X), X==2.",
"d :- c."
]
prg = [
"p.",
"q :- p.",
"{r;t} :- q.",
":- r."
]
def find_nodes_at_timestep(G, step):
    nodes = []
    for node in g:
        if node[0] == step:
            nodes.append(node)
    return nodes

current_prg = []
def create_true_symbols_from_solver_state(ss):
    syms = []
    for true in ss.model:
        syms.append((true, True))
    for false in ss.falses:
        syms.append((false, False))
    return syms

def add_falses_to_ss(sss):
    all_possible = set()
    for ss in sss:
        all_possible.update(ss.model)
    print(all_possible)
    for ss in sss:
        falses = all_possible - set(ss.model)
        ss.falses = falses


for i, rule in enumerate(prg):
    print(f"Adding rule {rule}")
    current_prg.append(rule)
    ctl = clingo.Control("0")
    ctl.add("base", [], "\n".join(current_prg))
    ctl.ground([("base", [])])
    assumptions = find_nodes_at_timestep(g, i)
    print(f"{rule} with {len(assumptions)} assumpts.")
    for ass in assumptions:
        print(f"Continuing with {ass}")
        assumpts = create_true_symbols_from_solver_state(ass[1])
        print(f"Assumptions: {assumpts}")
        with ctl.solve(assumptions=assumpts,yield_=True) as handle:
            solver_states_to_create = []
            print("?")
            hacky_counter = 0
            for m in handle:
                print("!")
                syms = SolverState(m.symbols(atoms=True))
                print(f"({ass})-[{rule}]->({(i+1,syms)})")
                solver_states_to_create.append(syms)
                hacky_counter += 1
            if hacky_counter == 0:
                # HACK: This point makes the model unsolvable, so we artificially create empty
                solver_states_to_create.append(SolverState(set()))
            add_falses_to_ss(solver_states_to_create)
            for ss in solver_states_to_create:
                g.add_edge(ass, (i+1, ss), rule=rule)

nx.draw(g, with_labels=True, font_weight='bold')
plt.show()
print(len(g))
    # with c.solve(yield_=True) as handle:
    #     print(type(handle))
    #     for m in handle:
    #         print(type(m))
    #
    #         symbols_in_model = m.symbols(atoms=True)
    #         print(symbols_in_model)
