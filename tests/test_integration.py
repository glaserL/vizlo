import clingo

from debuggo.solve import solver
from debuggo.display import graph
from debuggo.main import Dingo, Debuggo
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
    dingo = Dingo()

def test_anotherOne():
    ctl = Debuggo()
    img = ctl.add("base", [], "a. {b} :- a. c :- b.")
    ctl._show(img)

def test_paint_first_model():
    ctl = Dingo()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.solve()
    ctl.paint("")

def test_app():
    from debuggo.main import _main
    _main()

def test_print_all_models():
    ctl = Debuggo()
    prg = "a. {b} :- a. c :- b. d :- c."
    prg = "a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()
    plt.show()



def test_print_only_specific_models():
    ctl = Debuggo("0")
    prg = "{a}. b :- a."
    prg = "a. {b} :- a. c :- b. d :- not c."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    with ctl.solve(yield_ = True) as handle:
        for model in handle:
            print(f"!!!{model}")
            symbols = model.symbols(atoms=True)
            if len(symbols) > 1:
                print(f"Oh, what an interesting model! {model}")
                ctl.add_to_painter(symbols)
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