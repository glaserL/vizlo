from debuggo.solve import solver
from debuggo.display import folder_display
## Transformer
def test_networkx():
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        reified_program = "".join(f.readlines())
    sr = solver.SolveRunner(reified_program)
    for _ in range(5):
        print(".",end="")
        sr.step()
    viz = folder_display.GraphVisualizer(sr.history)
    viz.draw_networkx_graph()
    