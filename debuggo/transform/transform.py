from copy import copy

import clingo, heapq
import networkx as nx
from clingo import ast
from typing import List, Dict, Tuple

RuleSet = List[str]
Program = List[RuleSet]
ASTRuleSet = List[clingo.ast.AST]
ASTProgram = List[ASTRuleSet]

def make_signature(function: clingo.ast.Function):
    return function.name, len(function.arguments)

class Visitor:
    def visit_children(self, x, *args, **kwargs):
        for key in x.child_keys:
            self.visit(getattr(x, key), *args, **kwargs)

    def visit_list(self, x, *args, **kwargs):
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_tuple(self, x, *args, **kwargs):
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_none(self, *args, **kwargs):
        pass

    def visit(self, x, *args, **kwargs):
        if isinstance(x, ast.AST):
            attr = "visit_" + str(x.type)
            # print(f"{x} ({attr} (({hasattr(self, attr)})) {{{kwargs}}})")
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
        for y in x[:i]:
            yield y
        yield z
        for y in x[i + 1:]:
            yield self.visit(y, *args, **kwargs)

    def visit_list(self, x, *args, **kwargs):
        for i, y in enumerate(x):
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                return list(self._seq(i, z, x, args, kwargs))
        return x

    def visit_tuple(self, x, *args, **kwargs):
        for i, y in enumerate(x):
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                return tuple(self._seq(i, z, x, args, kwargs))
        return x


class JustTheRulesTransformer(Transformer):

    def __init__(self):
        super(JustTheRulesTransformer, self).__init__()
        self._dependency_map = dict()
        self._head_signature2rule = dict()
        self._body_signature2rule = dict()

    def visit_Program(self, program):
        pass

    def visit_Rule(self, rule):
        head = rule.head
        self.visit(head, rule=rule, pos="head")
        self.visit(rule.body, rule=rule, pos="body")
        return rule

    def visit_Function(self, function, rule=None, pos=None):
        if rule is None:
            return rule
        if pos is None:
            return rule
        signature = make_signature(function)
        if pos=="head":
            tmp = self._head_signature2rule.get(signature, list())
            tmp.append(rule)
            self._head_signature2rule[signature] = tmp
        if pos=="body":
            tmp = self._body_signature2rule.get(signature, list())
            tmp.append(rule)
            self._body_signature2rule[signature] = tmp
            #
            #
            # hashable_rule = str(rule)
            # hashable_literal = str(literal)
            # tmp = self._dependency_map.get(hashable_literal, list())
            # tmp.append(rule)
            # self._dependency_map[hashable_literal] = tmp
            # tmp = self._dependency_map.get(hashable_rule, list())
            # tmp.append(literal)
            # self._dependency_map[hashable_rule] = tmp
        # self.visit(literal, rule)
        # return literal
        return function


    # def visit_Literal(self, literal, rule=None):
    #     if rule is not None:
    #         hashable_rule = str(rule)
    #         hashable_literal = str(literal)
    #         tmp = self._dependency_map.get(hashable_literal, list())
    #         tmp.append(rule)
    #         self._dependency_map[hashable_literal] = tmp
    #         # tmp = self._dependency_map.get(hashable_rule, list())
    #         # tmp.append(literal)
    #         # self._dependency_map[hashable_rule] = tmp
    #     return literal

    def _split_program_into_rules(self, program: str) -> ASTRuleSet:
        rules = []
        clingo.parse_program(
            program,
            lambda stm: add_to_list_if_is_not_program(self.visit(stm), rules))
        return rules

    def transform(self, program, sort=True) -> ASTProgram:
        rules = self._split_program_into_rules(program)
        if sort:
            rules = self.sort(rules)
        else:
            rules = [[rule] for rule in rules]
        return rules

    def sort_program_by_dependencies(self, parse: ASTRuleSet) -> Program:
        print(f"Parse: {parse} ({len(parse)})")
        deps = make_dependency_graph(parse, self._head_signature2rule, self._body_signature2rule)
        deps = merge_cycles(deps)
        deps = remove_eigenkanten(deps)
        program = list(nx.topological_sort(deps))
        return program

    def sort(self, program: ASTRuleSet) -> ASTProgram:
        sorted_program = self.sort_program_by_dependencies(program)
        rules = []
        for rule_set in sorted_program:
            rules.append(parse_rule_set(rule_set))
        return rules

def make_dependency_graph(rules: List[clingo.ast.Rule],
                          head_dependencies: Dict[Tuple[str, int], List[clingo.ast.AST]],
                          body_dependencies: Dict[Tuple[str, int], List[clingo.ast.AST]]):
    """We draw a dependency graph based on which rule head contains which literals.
    That way we know, that in order to have a rule r with a body containg literal l, all rules that have l in their
    heads must come before r.
    """
    g = nx.DiGraph()
    for head_signature, rules_with_head in head_dependencies.items():
        dependent_rules = body_dependencies.get(head_signature, [])
        for parent_rule in rules_with_head:
            for dependent_rule in dependent_rules:
                g.add_edge(frozenset([str(parent_rule)]), frozenset([str(dependent_rule)]))
        if len(dependent_rules) == 0:
            for rule in rules_with_head:
                g.add_node(frozenset([str(rule)]))
    # for rule in rules:
    #     body = rule.body
    #     rule_as_str = str(rule)
    #     if len(body) > 0:
    #         for e in body:
    #             deps = dependencies.get(str(e), set())
    #             for dep in deps:
    #                 g.add_edge(frozenset([str(dep)]), frozenset([rule_as_str]))
    #     else:
    #         g.add_node(frozenset([str(rule)]))
    return g
#
# def make_dependency_graph(rules: List[clingo.ast.Rule], dependencies: Dict[str, List[clingo.ast.AST]]):
#     """We draw a dependency graph based on which rule head contains which literals.
#     That way we know, that in order to have a rule r with a body containg literal l, all rules that have l in their
#     heads must come before r.
#     """
#     g = nx.DiGraph()
#     print(dependencies)
#     for rule in rules:
#         body = rule.body
#         rule_as_str = str(rule)
#         if len(body) > 0:
#             for e in body:
#                 deps = dependencies.get(str(e), set())
#                 for dep in deps:
#                     g.add_edge(frozenset([str(dep)]), frozenset([rule_as_str]))
#         else:
#             g.add_node(frozenset([str(rule)]))
#     return g


#
# def make_dependency_graph(rules: List[clingo.ast.Rule], dependencies: Dict[str, List[clingo.ast.AST]]):
#     g = nx.DiGraph()
#     for x in rules:
#         for y in rules:
#             x_head = x.head
#             y_body = y.body
#             if len(y_body) > 0:
#                 for y_lit in y_body:
#                     if y_lit == x_head:
#                         g.add_edge(frozenset([str(x)]), frozenset([str(y)]))
#             else:
#                 g.add_node(frozenset([str(x)]))
#     return g


def merge_nodes(nodes):
    old = set()
    for x in nodes:
        old.update(x)
    return frozenset(old)


def merge_cycles(g: nx.Graph) -> nx.Graph:
    mapping = {}
    for cycle in nx.algorithms.cycles.simple_cycles(g):
        merge_node = merge_nodes(cycle)
        mapping.update({old_node: merge_node for old_node in cycle})

    return nx.relabel_nodes(g, mapping)


def remove_eigenkanten(g):
    remove_edges = []
    for edge in g.edges:
        u, v = edge
        if u == v:
            remove_edges.append(edge)

    for edge in remove_edges:
        g.remove_edge(*edge)
    return g


def add_to_list_if_is_not_program(rule: clingo.ast.AST, lst: List):
    if rule is not None and not rule.type == clingo.ast.ASTType.Program:
        lst.append(rule)


def parse_rule_set(rule_set: RuleSet) -> ASTRuleSet:
    ast_rule_set = []
    for rule in rule_set:
        clingo.parse_program(rule, lambda ast_rule: add_to_list_if_is_not_program(ast_rule, ast_rule_set))
    return ast_rule_set


def transform(program: str, sort: bool = True):
    t = JustTheRulesTransformer()
    return t.transform(program, sort)


class DependentAtomsTransformer(Transformer):

    def __init__(self):
        self.dependency_map = {}

    #
    def visit_Rule(self, rule):  # (\label{prg:dl:transformer:rule:begin}#)
        head = rule.head
        body = rule.body
        self.visit(head, loc="head", rule=rule)
        self.visit(body, loc="body", rule=rule)
        return rule

    #
    # def visit_Literal(self, literal, rule=None, loc=None):
    #     if loc == "head":
    #         print(f"{literal} in {rule} ({loc})")
    #         strrule = str(rule)
    #         tmp = self.dependency_map.get(strrule, [])
    #         tmp.append(literal)
    #         self.dependency_map[strrule] = tmp
    #     print(self.dependency_map)
    #     return literal
    #
    # def visit_SymbolicAtom(self, atom, loc=None):
    #     return atom

    def visit_Function(self, func, rule=None, loc=None):
        if loc == "head":
            # print(f"{func} in {rule} ({loc})")
            strrule = str(rule)
            tmp = self.dependency_map.get(strrule, [])
            tmp.append(func)
            self.dependency_map[strrule] = tmp
        return func

    def make(self, program):
        clingo.parse_program(
            program,
            lambda stm: self.funcy(stm))  # stm mean line in code
        return self.dependency_map

    def funcy(self, stm):
        result = self.visit(stm)
