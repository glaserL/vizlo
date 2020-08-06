
from debuggo.transform import transform
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
