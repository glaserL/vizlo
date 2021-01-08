import clingo
import networkx as nx

from debuggo.solve import solver
from debuggo.display import graph
from debuggo.main import Debuggo, PythonModel
import matplotlib.pyplot as plt

## Transformer
def test_networkx():
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    sr = solver.SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    viz = graph.GraphVisualizer(sr.graph)
    viz.draw_networkx_graph()
    
def test_instanciation():
    dingo = Debuggo()

def test_anotherOne():
    ctl = Debuggo()
    img = ctl.add("base", [], "a. {b} :- a. c :- b.")
    ctl._show(img)

def test_paint_first_model():
    ctl = Dingo()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.solve()
    ctl.paint("")

#def test_app():
#    from debuggo.main import _main
#    _main()

def test_print_all_models():
    ctl = Debuggo()
    # prg = "a. {b} :- a. c :- b. d :- c."
    prg = "a."
    # prg = "x(1).\n#program recursive.\nx(X) :- x(X-1), X<10.\n#program recursive."
    prg = "x(1).\n#program recursive.\nx(X) :- y(X).\ny(X) :- x(X-1); X<4.\n#program recursive."
    prg = "a.\n{b} :- a.\nc :- b.\n{d} :- b.\ne :- not d.\n:- b."
    #prg = "{a}.\nb :- a. :- b."
    #prg = "x(1..100). {y(X)} :- x(X)."
    #prg = "b :- a."
    #prg = "x(1). x(X) :- x(Y); Y<X; X < 10."
    #prg = "{x(1)}.\n#program recursive.\nx(X) :- y(X).\ny(X) :- x(X-1); X<4.\n#program recursive."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()
    plt.show()
    # TODO: Draw choice rules different (arrow dotted)
    # TODO: Draw constraint rules differently (red)
    # TODO: only print what was added (as option) the sudoku program, tsp, from asp class

# Milestones:
# Expand recursion steps
# Clickable
# Independent of order
# Efficiency

# Try with a real world program

def test_print_only_specific_models():
    ctl = Debuggo(["0"])
    prg = "{a}. b :- a."
    prg = "a. {b} :- a. c :- b. d :- not c."
    #prg = "{a}.\n{b} :- a."
    #prg = "{a}.\n{b}.\n#program recursive.\n a :- b.\n b:- a.\n#program recursive.\n c :- b." # TODO: FIX
    #prg = "a(1..2). {y(X)\n    \t } :- a(X). "

# TODO: test with this {a}. {b}. {c}. a :- b. b: - c. c:- a.
    # TODO: paint only on
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    with ctl.solve(yield_ = True) as handle:
        for model in handle:
            print(f"!!!{model}")
            symbols = model.symbols(atoms=True)
            #if len(symbols) != 1:
            print(f"Oh, what an interesting model! {model}")
            ctl.add_to_painter(symbols)
    ctl.paint()

    img = ctl.paint()
    plt.show()


def test_adding_model_to_painter():
    ctl = Debuggo()
    prg = "{a}. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    with ctl.solve(yield_ = True) as handle:
        for model in handle:
            ctl.add_to_painter(model)
    assert len(ctl.painter) > 0

def test_dont_repeat_constraints():
    ctl = Debuggo()
    prg = "{a}. :- not a. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()
    plt.show()


def test_finding_corresponding_nodes():
    ctl = Debuggo(["0"])
    prg = "{a}. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    stable_models = []
    with ctl.solve(yield_ = True) as handle:
        for model in handle:
            model_as_set = list(model.symbols(atoms=True))
            stable_models.append(model_as_set)
    g = ctl.anotherOne.make_graph()
    assert 2 == len(stable_models) == len(ctl.find_nodes_corresponding_to_stable_models(g, stable_models))

def test_recursion():
    ctl = Debuggo(["0"])
    prg = "a.\n#program recursive.\na :- b.\nb :- a.\n#program recursive."
    prg = "x(1).\n#program recursive.\nx(X) :- y(X).\ny(X) :- x(X-1); X<4.\n#program recursive."

    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()
    plt.show()

def test_painting_without_initial_solving():
    ctl = Debuggo(["0"])
    # TODO: why do this global stuff if you can just grab them from the control object after grounding directly?
    ctl.add("base", [], "x(0..3). {y(X)} :- x(X).")
    ctl.ground([("base", [])])
    interesting_model = set()
    interesting_model.add(clingo.Function("y", [clingo.Number(5)]))
    interesting_model.add(clingo.Function("y", [clingo.Number(3)]))
    for x in range(6):
        interesting_model.add(clingo.Function("x", [clingo.Number(x)]))

    interesting_model = PythonModel(interesting_model)
    #ctl.add_to_painter(interesting_model)
    ctl.paint()
    plt.show()

def test_that_iterating_over_tree_doesnt_return_node_twice():
    g = nx.DiGraph()
    g.add_edge("a", "b", rule="first")
    g.add_edge("a", "c", rule="second")
    g.add_edge("b", "d", rule="first")
    assert len(g)-1 == len(list(g.edges(data=True)))

def test_and_viz_queens():
    queens = """
    
% domain
number(1..3).

% alldifferent
1 { q(X,Y) : number(Y) } 1 :- number(X).
1 { q(X,Y) : number(X) } 1 :- number(Y).

% remove conflicting answers
:- q(X1,Y1), q(X2,Y2), X1 < X2, Y1 == Y2.
:- q(X1,Y1), q(X2,Y2), X1 < X2, Y1 + X1 == Y2 + X2.
:- q(X1,Y1), q(X2,Y2), X1 < X2, Y1 - X1 == Y2 - X2.

"""
    queens = "{a}. {b}. {c}. a :- b. b: - c. c:- a."
    queens = "{a; b}. b :- a."
    queens = "{a}. b :- a. c :- b."
    ctl = Debuggo(["0"])
    # TODO: why do this global stuff if you can just grab them from the control object after grounding directly?
    ctl.add("base", [], queens)
    ctl.ground([("base", [])])
    print("ok??")

    # interesting_model = set()
    # interesting_model.add(clingo.Function("y", [clingo.Number(5)]))
    # interesting_model.add(clingo.Function("y", [clingo.Number(3)]))
    # for x in range(6):
    #     interesting_model.add(clingo.Function("x", [clingo.Number(x)]))
    #
    # interesting_model = PythonModel(interesting_model)
    #ctl.add_to_painter(interesting_model)
    ctl.paint()
    plt.show()