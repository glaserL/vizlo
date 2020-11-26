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
    prg = "a. b. c. :- b. :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    ctl.paint()
    plt.show()


def test_print_only_specific_models():
    ctl = Debuggo()
    prg = "{a}. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    for model in ctl.solve(yield_=True):
        if model.hasSomeThingSpecial():
            ctl.addToPainter(model)

        ctl.paintModels()
    img = ctl.paint()
    ctl._show(img)


def test_adding_model_to_painter():
    ctl = Debuggo()
    prg = "{a}. b :- a."
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    for model in ctl.solve(yield_=True):
        ctl.add_to_painter(model)
    assert len(ctl.painter) > 0