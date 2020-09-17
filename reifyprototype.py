#script (python)

import clingo
import clingo.ast

class Transformer:
    def visit_children(self, x, *args, **kwargs):
        for key in x.child_keys:
            setattr(x, key, self.visit(getattr(x, key), *args, **kwargs))
        return x

    def visit(self, x, *args, **kwargs):
        if isinstance(x, clingo.ast.AST):
            
            attr = "visit_" + str(x.type)
            if hasattr(self, attr):
                return getattr(self, attr)(x, *args, **kwargs) # This calls the function in the TermTransformer
            else:
                return self.visit_children(x, *args, **kwargs)
        elif isinstance(x, list):
            return [self.visit(y, *args, **kwargs) for y in x]
        elif x is None:
            return x
        else:
            raise TypeError("unexpected type")

class TermTransformer(Transformer):

    
    def visit_Function(self, term):
        line = term.location["begin"]["line"]
        print(line)
        term.arguments.append(clingo.ast.Symbol(term.location, line))
        
        return term

    def visit_Symbol(self, term):
        # this function is not necessary if gringo's parser is used
        # but this case could occur in a valid AST
        fun = term.symbol
        assert(fun.type == clingo.SymbolType.Function)
        # term.symbol = clingo.Function(fun.name, fun.arguments + [self.parameter], fun.positive)
        return term

# y) class HeadBodyTransformer(Transformer):
# def
# def
# visit_Rule(self, rule):
# head = rule.head
# body = rule.body
# head = self.visit(head, loc="head")
# body = self.visit(body, loc="body")
# return ast.Rule(rule.location, head, body)
# h(a,1,(b)) :- b, not a. <- a :- b.
    def visit_Rule(self, rule):
        print(f"Visiting Rule: {rule}")
        # clingo.ast.Literal(location, sign, atom)
        print(rule)
        print(rule.head)
        # clingo.ast.Function(location, name, arguments, external)
        new_head = clingo.ast.Function(rule.location, "h", "a", False)
        new_head = clingo.ast.Literal(rule.location, "", new_head)
        # new_head = self.visit(rule.head)
        print(f"Created head: {new_head}")
        new_body = clingo.ast.Literal(rule.head.location, "", rule.head)
        new_body = rule.body
        new_body = self.visit(new_body)
        print(f"Created body: {new_body}")
        
        # holds_head = clingo.Function("h", [rule.head, rule.location["begin"]["line"], clingo.Function("", rule.body)])
        
        
        new_rule = clingo.ast.Rule(rule.location, new_head, new_body)
        print(f"Created rule: {new_rule}")
        return new_rule
        
    def visit_ShowSignature(self, sig):
        sig.arity += 1
        return sig

    def visit_ProjectSignature(self, sig):
        sig.arity += 1
        return sig

def main(prg):
    with prg.builder() as b:
        t = TermTransformer()
        clingo.parse_program(
            open("tests/program.lp").read(),
            lambda stm: b.add(
                t.visit(stm)
                )) # stm mean line in code
    prg.ground([("base", [])])
    prg.solve()



#end.