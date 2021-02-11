import time

import clingo
import pytest

from vizlo.graph import NetworkxDisplay
from vizlo.main import VizloControl, PythonModel
import matplotlib.pyplot as plt


def test_instanciations():
    _ = VizloControl()
    _ = VizloControl(["0"])


def test_parameters_exist():
    debuggo = VizloControl()
    debuggo.add("base", [], "a.")
    debuggo.paint(atom_draw_maximum=True)
    debuggo.paint(show_entire_model=False)
    debuggo.paint(sort_program=False)
    debuggo.paint(figsize=(3, 4))
    debuggo.paint(model_font_size=23)
    debuggo.paint(rule_font_size=13)
    debuggo.paint(dpi=100)


def test_empty_program_raises_value_error():
    debuggo = VizloControl()
    with pytest.raises(ValueError):
        debuggo.paint()


def test_inherits_control_methods():
    debuggo = VizloControl()
    ctl = clingo.Control()
    attrs = [attr for attr in dir(ctl) if not attr.startswith("_")]
    print(attrs)
    result = (hasattr(debuggo, a) for a in attrs)
    assert result, "Debuggo object should inherit functions from clingo.Control"


@pytest.mark.skip
def test_internal_clingo_also_solves():
    ctl = VizloControl()
    ctl.add("base", [], "a :- b.\nb.")
    ctl.solve()


#    assert not ctl.control.is_conflicting

def test_painting_specific_models_is_fast():
    expensive_program = "a(1..3). {b(X)} :- a(X)."
    begin = time.time()
    interesting_model = [clingo.Function("a", [i], True) for i in range(15)]
    ctl = VizloControl(["0"])
    ctl._add_and_ground(expensive_program)
    ctl.add_to_painter(interesting_model)
    ctl.paint()
    end = time.time()
    assert end - begin < 1, "Painting a small subset of a large program should be fast."


def test_print_only_specific_model_complete_definition():
    ctl = VizloControl(["0"])
    prg = "{a}. b :- a."
    ctl._add_and_ground(prg)

    interesting_model = {clingo.Function("a", []), clingo.Function("b", [])}
    ctl.add_to_painter(interesting_model)

    g = ctl._make_graph()
    nodes = list(g.nodes)
    assert len(nodes) == 3
    assert len(nodes[0].model) == 0
    assert len(nodes[2].model) == 2


def test_painter_doesnt_print_constraint_models():
    ctl = VizloControl(["0"])
    ctl.add("base", [], "{a}. {b}. :- a.")
    ctl.ground([("base", [])])
    g1 = ctl._make_graph()
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            if m.contains(clingo.Function("b", [])):
                ctl.add_to_painter(m)

    g2 = ctl._make_graph()
    assert len(g2) > 1 and len(g1) > 1, "Using painter should not make everything invalid."
    assert len(g2) != len(g1), "Adding clingo models to painter should have an effect."


def test_adding_clingo_models_to_painter():
    prg = "a(1..3). {b(X)} :- a(X)."
    ctl = VizloControl(["0"])
    ctl.add("base", [], prg)
    ctl.ground([("base", [])])
    g1 = ctl._make_graph()
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            if m.contains(clingo.Function("b", [clingo.Number(1)])):
                ctl.add_to_painter(m)

    g2 = ctl._make_graph()
    assert len(g2) > 1 and len(g1) > 1, "Using painter should not make everything invalid."
    assert len(g2) != len(g1), "Adding clingo models to painter should have an effect."
    ctl = VizloControl(["0"])
    ctl.add("base", [], prg)
    interesting_model = []
    for i in range(1, 4):
        interesting_model.append(clingo.Function("a", [clingo.Number(i)]))
    interesting_model.append(clingo.Function("b", [clingo.Number(1)]))
    ctl.add_to_painter(interesting_model)

    g2 = ctl._make_graph()
    assert len(g2) > 1 and len(g2) > 1, "Using painter should not make everything invalid."
    assert len(g2) != len(g1), "Adding clingo models to painter should have an effect."


def test_dont_repeat_constraints():
    ctl = VizloControl()
    prg = "{a}. {b}. :- a. {c}."
    ctl._add_and_ground(prg)
    g = ctl._make_graph(False)
    assert len(g.nodes) == 15, "Internal solver state should not merge nodes."
    display = NetworkxDisplay(g, merge_nodes=False)
    assert len(display._ng) == 15, "Display graph should not be merged if not told to do so."
    display = NetworkxDisplay(g, merge_nodes=True)
    assert len(display._ng), "Constrained partial models should not show up in the visualization."


def test_painting_without_initial_solving():
    ctl = VizloControl(["0"])
    ctl.add("base", [], "x(0..3). {y(X)} :- x(X).")
    ctl.ground([("base", [])])
    interesting_model = set()
    interesting_model.add(clingo.Function("y", [clingo.Number(5)]))
    interesting_model.add(clingo.Function("y", [clingo.Number(3)]))
    for x in range(6):
        interesting_model.add(clingo.Function("x", [clingo.Number(x)]))

    interesting_model = PythonModel(interesting_model)
    ctl.add_to_painter(interesting_model)
    g = ctl._make_graph()
    assert len(g) > 0, "Painter should work independently of solving process."


def test_painting_with_adding_rules_during_solving():
    ctl = VizloControl(["0"])
    ctl.add("base", [], "{a; b; c}.")
    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            ctl.add_to_painter(m)
            break
    g = ctl._make_graph()
    assert len(g) == 2


def test_calling_paint_should_return_a_plottable_figure():
    ctl = VizloControl(["0"])
    ctl.add("base", [], "a.")
    result = ctl.paint()
    assert result is not None, "Debuggo.paint() should return a result."
    assert isinstance(result, plt.Figure), "Debuggo.paint() should return a plottable array."


@pytest.mark.skip
def test_make_documentation_img():
    ctl = VizloControl(["0"])
    prg = "{a}. :- a. {b}."
    ctl.add("base", [], prg)
    ctl.paint(show_entire_model=True, dpi=300)
    plt.savefig("../docs/img/sample.png", dpi=300)


def testy_test():
    ctl = VizloControl(["0"])
    prg = "{a}. :- a. {b}. c :- d. d :- c, not d."
    ctl.add("base", [], prg)
    ctl.paint(show_entire_model=True, dpi=300)


def test_pretty_import():
    from vizlo import VizloControl
    c = VizloControl()


def test_dont_accept_false_as_model_length():
    ctl = VizloControl(["0"])
    prg = "{a}. :- a. {b}. c :- d. d :- c, not d."
    ctl.add("base", [], prg)
    with pytest.raises(ValueError):
        ctl.paint(True)
