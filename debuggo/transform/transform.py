
from copy import copy

import clingo, heapq
from clingo import ast
from typing import List


class ASPTransformer():
    """
    Transforms a given ASP program into a reified version.
    """

    def __init__(self):
        raise NotImplementedError

    def transform(self, program):
        print("DEBUGGING MODE")
        return """
h(a,1,(b)) :- b, not a.
h(b,2,(c)) :- c, not b.
h(c,3,(d)) :- d, not c.
h(d,4,()) :- not d.
#external d.
#external c.
#external b.
#external a.
% Original program.
%a :- b.
%b :- c.
%c :- d.
%d.
"""

class IdentityTransformer(ASPTransformer):

    def __init__(self):
        pass

    def transform(self, program):
        return program

class HoldsTransformer(ASPTransformer):
    def __init__(self):
        pass

    def transform(self, program):
        transformed_lines = []
        i = 1
        atoms = set()
        with open("error.log","w") as log:
            for line in program.split("\n"):
                if line.strip().startswith("%"):
                    transformed_lines.append(line)
                elif ":-" in line:
                    split_rule = line.split(":-")
                    head = split_rule[0].strip()
                    literals = split_rule[1].split(",")
                    pos_literals = []
                    log.write(f"Found head: {head} :- {literals}\n")
                    for lit in literals:
                        if "not" not in lit:
                            pos_literals.append(lit.strip())
                        atoms.add(lit.replace("not","").strip())
                transformed_lines.append(f"h({head},{i},({','.join(pos_literals)})) :- {','.join(pos_literals)}, not {head}.")
            for atom in atoms:
                transformed_lines.append(f"#external: {atom}.")
    
        return "\n".join(transformed_lines)

class Visitor:
    def visit_children(self, x, *args, **kwargs):
        for key in x.child_keys:
            self.visit(getattr(x, key), *args, **kwargs)

    def visit_list(self, x, *args, **kwargs):
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_tuple(self, x, *args, **kwargs):
        print(f"Visting tuple {x}")
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_none(self, *args, **kwargs):
        pass

    def visit(self, x, *args, **kwargs):
        if isinstance(x, ast.AST):
            attr = "visit_" + str(x.type)
            print(f"{x} ({attr} (({hasattr(self, attr)})) {{{kwargs}}})")
            if hasattr(self, attr):
                return getattr(self, attr)(x, *args, **kwargs)
            return self.visit_children(x, *args, **kwargs)
        if isinstance(x, list):
            return self.visit_list(x, *args, **kwargs)
        if isinstance(x, tuple):
            return self.visit_tuple(x, *args, **kwargs)
        if x is None:
            return self.visit_none(x, *args, **kwargs)
        raise TypeError("unexpected type: {}".format(x))


class Transformer(Visitor):
    def visit_children(self, x, *args, **kwargs):
        copied = False
        for key in x.child_keys:
            y = getattr(x, key)
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                if not copied:
                    copied = True
                    x = copy(x)
                setattr(x, key, z)
        return x

    def _seq(self, i, z, x, args, kwargs):
        print("Visting Transformer swq")
        for y in x[:i]:
            yield y
        yield z
        for y in x[i+1:]:
            yield self.visit(y, *args, **kwargs)

    def visit_list(self, x, *args, **kwargs):
        print(f"Visting Transformer lst {x}")
        for i, y in enumerate(x):
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                return list(self._seq(i, z, x, args, kwargs))
        return x

    def visit_tuple(self, x, *args, **kwargs):
        print("Visting Transformer tup")
        for i, y in enumerate(x):
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                return tuple(self._seq(i, z, x, args, kwargs))
        return x



class HeadBodyTransformer(Transformer):
    def __init__(self):
        self._reified_program = []
        self._atoms_to_assign_as_external: List[clingo.ast.Function] = []

    def visit_Rule(self, rule):#(\label{prg:dl:transformer:rule:begin}#)
        head = rule.head
        body = rule.body
        print(f"Before:{head}:-{body} ({head.type}):-({[x.type for x in body] if isinstance(body, list) else body.type})")
        holds_func = clingo.ast.Function(head.location, clingo.ast.Symbol(head.location, clingo.Function("h")),[head], False)
        holds_atom = clingo.ast.SymbolicAtom(holds_func)
        holds_literal = clingo.ast.Literal(head.location, head.sign, holds_atom)
        #head = self.visit(head)
        print("####################")
        body = self.visit(body)
        print(self._atoms_to_assign_as_external)
        body_as_func_argument = copy(body)
        body_as_func_argument = [lit.atom.term for lit in body_as_func_argument]
        body_as_holds = clingo.ast.Function(head.location, "", body_as_func_argument, False)
        print(f"body_as_holds: {body_as_holds}")

        negated_head = clingo.ast.Literal(head.location, head.sign.Negation, head.atom)
        body.append(negated_head)
        
        #new_head = self.create_new_head(head)
        linenumber = clingo.ast.Symbol(head.location, clingo.Number(head.location["begin"]["line"]))
        head_as_term = head.atom.term
        print(head_as_term.type)
        self._atoms_to_assign_as_external.append(head_as_term.name)
        holds_func = clingo.ast.Function(head.location, "h", [head_as_term, linenumber, body_as_holds], False)
        holds_symbolicAtom = clingo.ast.SymbolicAtom(holds_func)
        holds_literal = clingo.ast.Literal(head.location,head.sign, holds_symbolicAtom)
        head = holds_literal
        print(holds_literal)
        print(self._atoms_to_assign_as_external)
        
        print("####################")
        #if len(body):
        #    body.extend(self.visit(body, neg=True))
        # body.append(ast.Literal(rule.location, "", body[0]))
        print(f"After:{head}:-{body} ({head.type}):-({[x.type for x in body] if isinstance(body, list) else body.type})")
        rule = ast.Rule(rule.location, head, body)
        print(f"Result:{rule} ({rule.type})")
        print(self._atoms_to_assign_as_external)
        return rule#(\label{prg:dl:transformer:rule:end}#)

    def create_new_head(self, head):
        print("====")
        head_as_func = head.atom.term
        holds_head_func = self.reify(head_as_func)
        holds_symbolicAtom = clingo.ast.SymbolicAtom(holds_head_func)
        holds_literal = clingo.ast.Literal(head.location,head.sign, holds_symbolicAtom)
        print(holds_head_func)
        print("====")
    
    def visit_Literal(self, literal, neg=False):
        print(f"Visting literal: {literal}")
        if neg:
            literal.sign = literal.sign.Negation
        else:
            literal.sign = literal.sign
        print(f"Returning literal: {literal}")
        literal.atom = self.visit(literal.atom)
        return literal

    def visit_SymbolicAtom(self, atom, neg=False):
        print(f"Visting symbolic atom: {atom}")
        print(f"atom.term: {atom.term} ({atom.term.type})")
        
        if neg:
            atom.term = self.visit(atom.term)
        else:
            atom.term = self.visit(atom.term)
        print(f"Returning symbolic atom: {atom}")
        return atom

    def reify(self, func):
        func_name_as_arg = clingo.ast.Symbol(func.location, clingo.Function(func.name))
        func.name = "h"
        func.arguments = [func_name_as_arg]
        return func

    def visit_Function(self, func, loc="body"):
        print(f"Visting function: {func}")
        print(f"{func.location} ({type(func.location)}))")
        print(f"{func.name} ({type(func.name)}))")
        print(f"{func.arguments} ({[x.type for x in func.arguments] if isinstance(func.arguments, list) else func.arguments.type}))")
        print(f"{func.external} ({type(func.external)}))")
        # if not len(func.arguments):
            # new_func = self.reify(func)
        # else:
        new_func = func
        print(f"Returning function: {new_func}")
        return new_func

    def visit_Symbol(self, symb):
        print(f"Visiting symbol {symb}")
        return symb


    def transform(self, program):
        prg = clingo.Control()
        print
        with prg.builder() as b:
            t = HeadBodyTransformer()
            clingo.parse_program(
                program,
                lambda stm: self.funcy(b, t, stm)) # stm mean line in code
        self._append_externals_to_program(self._reified_program, self._atoms_to_assign_as_external)
        return self._reified_program
    
    def _append_externals_to_program(self, program, externals):
        for external in externals:
            program.append(f"#external {external}.")
    
    def funcy(self, b, t, stm):
        print("One funcy call.")
        print(stm)
        result = t.visit(stm)
        if str(stm.type) == "Rule":
            self._atoms_to_assign_as_external.append(stm.head)
        print(f"Funcy result: {result}")
        b.add(result)
        self._reified_program.append(result)
        print("funcy call end.")

    def get_reified_program(self) -> clingo.ast.AST:
        return self._reified_program

    def get_reified_program_as_str(self) -> str:
        prg_as_str = "\n".join([str(x) for x in self._reified_program])
        print(prg_as_str)
        return prg_as_str