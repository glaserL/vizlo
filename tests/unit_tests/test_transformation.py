import clingo
import networkx as nx
import matplotlib.pyplot as plt
import pytest

from debuggo.transform import transform
from debuggo.transform.transform import sort_program_by_dependencies, make_dependency_graph


def are_two_lists_identical(a, b):
    print(a)
    print(b)
    return len((set(a) ^ set(b))) == 0


def is_str_list_and_ast_list_identical(ast, string):
    ast = [str(a) for a in ast]
    return are_two_lists_identical(ast, string)


def test_simple_program():
    prg = "a. b :- a."
    t = transform.JustTheRulesTransformer()
    parse = t.transform(prg)
    assert len(parse) == 2
    assert is_str_list_and_ast_list_identical(parse[0], ["a."])
    assert is_str_list_and_ast_list_identical(parse[1], ["b :- a."])


def test_choice_rule():
    prg = "{a}."
    t = transform.JustTheRulesTransformer()
    parse = t.transform(prg)
    assert len(parse) == 1
    assert is_str_list_and_ast_list_identical(parse[0], ["{ a :  }."])


def test_single_circle_within_already_sorted():
    prg = "a. b :- a. c :- b. b:-c. d :- b."
    t = transform.JustTheRulesTransformer()
    sorted_program = t.transform(prg)
    assert len(sorted_program) == 4
    assert is_str_list_and_ast_list_identical(sorted_program[0], ["a."])
    assert is_str_list_and_ast_list_identical(sorted_program[1], ["b :- a."])
    assert is_str_list_and_ast_list_identical(sorted_program[2], ["c :- b.", "b :- c."])
    assert is_str_list_and_ast_list_identical(sorted_program[3], ["d :- b."])


def test_sort_single():
    prg = "b :- a. a."
    t = transform.JustTheRulesTransformer()
    sorted_program = t.transform(prg)
    assert len(sorted_program) == 2
    assert is_str_list_and_ast_list_identical(sorted_program[0], ["a."])
    assert is_str_list_and_ast_list_identical(sorted_program[1], ["b :- a."])


def test_sort_single_circular_dependency():
    prg = "b :-a. a :- b."
    t = transform.JustTheRulesTransformer()
    sorted_program = t.transform(prg)
    assert len(sorted_program) == 1


def test_transform_returns_lists_of_lists():
    prg = "a."
    t = transform.JustTheRulesTransformer()
    parse = t.transform(prg)
    try:
        _ = parse[0][0]
    except IndexError:
        assert False
    assert True


def test_return_type_is_AST():
    prg = "a."
    t = transform.JustTheRulesTransformer()
    parse = t.transform(prg)
    assert len(parse) == 1
    assert isinstance(parse[0][0], clingo.ast.AST)


def test_dependent_choice_rule():
    prg = "a. {b} :- a. b :- a."
    t = transform.JustTheRulesTransformer()
    split = t._split_program_into_rules(prg)
    print(f"??{split}")
    g = make_dependency_graph(split)
    assert len(g) == 3


def test_single_rule_dependency_graph():
    prg = "a."
    t = transform.JustTheRulesTransformer()
    split = t._split_program_into_rules(prg)
    g = make_dependency_graph(split)
    assert len(g) == 1

def test_parameterized_sort():
    prg = "b :- a. a."
    t = transform.JustTheRulesTransformer()
    unsorted = t.transform(prg, sort=False)
    assert len(unsorted) == 2
    assert is_str_list_and_ast_list_identical(unsorted[0], ["b :- a."])
    assert is_str_list_and_ast_list_identical(unsorted[1], ["a."])
    sorted = t.transform(prg, sort=True)
    assert len(sorted)
    assert is_str_list_and_ast_list_identical(sorted[0], ["a."])
    assert is_str_list_and_ast_list_identical(sorted[1], ["b :- a."])


def test_transform_without_instanciation():
    prg = "b :- a. a."
    unsorted = transform.transform(prg, sort=False)
    assert len(unsorted) == 2
    assert is_str_list_and_ast_list_identical(unsorted[0], ["b :- a."])
    assert is_str_list_and_ast_list_identical(unsorted[1], ["a."])
    sorted = transform.transform(prg, sort=True)
    assert len(sorted)
    assert is_str_list_and_ast_list_identical(sorted[0], ["a."])
    assert is_str_list_and_ast_list_identical(sorted[1], ["b :- a."])

def test_dependency_transformation():
    prg = "x(1..10). {y(X)} :- x(X). {a;b;c;d;e} :- x(10)."
    t = transform.DependentAtomsTransformer()
    _ = t.make(prg)
    assert len(t.dependency_map) > 0
