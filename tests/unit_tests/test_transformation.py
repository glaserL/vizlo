import clingo
import networkx as nx
import matplotlib.pyplot as plt

from vizlo import transform
from vizlo.transform import make_dependency_graph


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
    assert len(sorted_program) == 3
    assert is_str_list_and_ast_list_identical(sorted_program[0], ["a."])
    assert is_str_list_and_ast_list_identical(sorted_program[1], ["b :- c.", "c :- b.","b :- a."])
    assert is_str_list_and_ast_list_identical(sorted_program[2], ["d :- b."])


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
    prg = "{a}. {b} :- a. b :- a."
    t = transform.JustTheRulesTransformer()
    _ = t.transform(prg)
    g = t._deps
    assert len(g) == 2

def test_formula_in_rule():
    prg = "x(X) :- y(X), X != 2. y(1..5)."
    sort = transform.transform(prg)
    assert len(sort) == 2
    assert is_str_list_and_ast_list_identical(sort[0], ["y((1..5))."])
    assert is_str_list_and_ast_list_identical(sort[1], ["x(X) :- y(X); X!=2."])



def test_creation_of_dependency_maps_during_transformation():
    prg = "{a;f;g}. {b} :- a. b :- a."
    t = transform.JustTheRulesTransformer()
    sort = t.transform(prg)
    assert len(sort) == 2, "Transformation should recognize two rulesets"
    heads = t._head_signature2rule
    bodies = t._body_signature2rule
    assert len(heads) == 4
    assert len(bodies) == 1
    assert len(heads[("a",0)]) == 1
    assert len(heads[("f",0)]) == 1
    assert len(heads[("g",0)]) == 1
    assert len(heads[("b",0)]) == 2
    assert len(bodies[("a",0)]) == 2

def test_single_rule_dependency_graph():
    prg = "a."
    t = transform.JustTheRulesTransformer()
    split = t._split_program_into_rules(prg)
    g = make_dependency_graph(split, t._head_signature2rule, t._body_signature2rule)
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

def test_sort_with_variables():
    prg = "x(X) :- y(X). y(X) :- z(X). z(1..3)."
    sorted = transform.transform(prg)
    assert len(sorted) == 3
    assert is_str_list_and_ast_list_identical(sorted[0], ["z((1..3))."])
    assert is_str_list_and_ast_list_identical(sorted[1], ["y(X) :- z(X)."])
    assert is_str_list_and_ast_list_identical(sorted[2], ["x(X) :- y(X)."])

def test_transformation_with_choice_on_variables():
    prg = "a((1..15)). { b(X) :  } :- a(X)."
    t = transform.JustTheRulesTransformer()
    sorted = t.transform(prg)
    g = make_dependency_graph(sorted, t._head_signature2rule,t._body_signature2rule)
    assert len(g) == 2
    assert len(sorted) == 2

def test_transform_choice_in_beginning():
    queens = "{a}. b :- a. c :- b."
    sorted = transform.transform(queens)
    assert len(sorted) == 3
    assert is_str_list_and_ast_list_identical(sorted[0], ["{ a :  }."])
    assert is_str_list_and_ast_list_identical(sorted[1], ["b :- a."])
    assert is_str_list_and_ast_list_identical(sorted[2], ["c :- b."])

def test_group_based_on_heads():
    prg = "{a; b}. a :- b."
    transformed = transform.transform(prg)
    assert len(transformed) == 1

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
