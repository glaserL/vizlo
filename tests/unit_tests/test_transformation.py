from typing import List
from debuggo.transform import transform


def are_two_lists_identical(a, b):
    print(a)
    print(b)
    return len((set(a) ^ set(b))) == 0


def test_abstract_transformer():
    error = None
    try:
        _ = transform.ASPTransformer()
    except NotImplementedError as e:
        error = e
    assert isinstance(error, NotImplementedError)


def test_recursive_parsing_with_annotation():
    prg = """
    #program recursive.
    a :- b.
    b :- a, not b.
    #program recursive.
    """
    transformer = transform.JustTheRulesTransformer()
    parsed_program = transformer.transform(prg)
    print(parsed_program)
    assert len(parsed_program) == 1
