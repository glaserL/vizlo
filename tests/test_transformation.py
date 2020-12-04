from typing import List
from debuggo.transform import transform


def are_two_lists_identical(a, b):
    print(a)
    print(b)
    return len((set(a) ^ set(b))) == 0


def test_identity_transformer():
    it = transform.IdentityTransformer()
    with open("tests/program.lp", encoding="utf-8") as f:
        program = "".join(f.readlines())
        assert program == it.transform(program)
def test_abstract_transformer():
    error = None
    try:
        _ = transform.ASPTransformer()
    except NotImplementedError as e:
        error = e
    assert isinstance(error, NotImplementedError)
def test_holds_transformer():
    ht = transform.HoldsTransformer()
    with open("tests/program.lp", encoding="utf-8") as f:
        program = ht.transform("".join(f.readlines()))
    
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        gold_result = "".join(f.readlines())
    assert program == gold_result

def test_ast_transformer():
    at = transform.HeadBodyTransformer()
    with open("tests/program.lp", encoding="utf-8") as f:
        at.transform("".join(f.readlines()))
        program = at.get_reified_program_as_str()
    
    with open("tests/program_transformed_holds.lp", encoding="utf-8") as f:
        gold_result = "".join(f.readlines())
    assert are_two_lists_identical(program.split("\n"), gold_result.split("\n"))


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