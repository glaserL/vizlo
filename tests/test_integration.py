from debuggo.solve import solver
from debuggo.display import folder_display
from debuggo.main import Dingo
## Transformer
def test_networkx():
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    sr = solver.SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    viz = folder_display.GraphVisualizer(sr.graph)
    viz.draw_networkx_graph()
    
def test_instanciation():
    dingo = Dingo()

def test_paint_first_model():
    ctl = Dingo()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.solve()
    ctl.paint("")

def test_app():
    from debuggo.main import _main
    _main()
