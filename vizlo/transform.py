from copy import copy

import clingo
import networkx as nx
from clingo import ast
from typing import List, Dict, Tuple

from vizlo.types import ASTRuleSet, ASTProgram, Program, RuleSet


def make_signature(function: clingo.ast.Function) -> Tuple[str, int]:
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
        self.rule2signatures = dict()

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
        if pos == "head":
            tmp = self._head_signature2rule.get(signature, list())
            tmp.append(rule)
            self._head_signature2rule[signature] = tmp
            tmp = self.rule2signatures.get(str(rule), [])
            tmp.append(signature)
            self.rule2signatures[str(rule)] = tmp
        if pos == "body":
            tmp = self._body_signature2rule.get(signature, list())
            tmp.append(rule)
            self._body_signature2rule[signature] = tmp

        return function

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
        deps = remove_loops(deps)
        self._deps = deps  # for debugging purposes
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
                          body_dependencies: Dict[Tuple[str, int], List[clingo.ast.AST]]) -> nx.DiGraph:
    """
    We draw a dependency graph based on which rule head contains which literals.
    That way we know, that in order to have a rule r with a body containg literal l, all rules that have l in their
    heads must come before r.
    :param rules: list of rules
    :param head_dependencies: Mapping from a signature to all rules containg them in the head
    :param body_dependencies: mapping from a signature to all rules containing them in the body
    :return:
    """
    g = nx.DiGraph()
    # Add independent rules
    for _, rules_with_head in head_dependencies.items():
        for x in rules_with_head:
            for y in rules_with_head:
                g.add_edge(frozenset([str(x)]), frozenset([str(y)]))
    # Add dependents
    for head_signature, rules_with_head in head_dependencies.items():
        dependent_rules = body_dependencies.get(head_signature, [])
        for parent_rule in rules_with_head:
            for dependent_rule in dependent_rules:
                g.add_edge(frozenset([str(parent_rule)]), frozenset([str(dependent_rule)]))
        if len(dependent_rules) == 0:
            for rule in rules_with_head:
                g.add_node(frozenset([str(rule)]))

    return g


def merge_nodes(nodes: frozenset) -> frozenset:
    old = set()
    for x in nodes:
        old.update(x)
    return frozenset(old)


def merge_cycles(g: nx.Graph) -> nx.Graph:
    mapping = {}
    for cycle in nx.algorithms.components.strongly_connected_components(g):
        print(f"Cycle: {cycle}")
        merge_node = merge_nodes(cycle)
        mapping.update({old_node: merge_node for old_node in cycle})
    print(mapping)
    return nx.relabel_nodes(g, mapping)


def remove_loops(g: nx.Graph) -> nx.Graph:
    remove_edges = []
    for edge in g.edges:
        u, v = edge
        if u == v:
            remove_edges.append(edge)

    for edge in remove_edges:
        g.remove_edge(*edge)
    return g


def add_to_list_if_is_not_program(rule: clingo.ast.AST, lst: List) -> None:
    if rule is not None and not rule.type == clingo.ast.ASTType.Program:
        lst.append(rule)


def parse_rule_set(rule_set: RuleSet) -> ASTRuleSet:
    ast_rule_set = []
    for rule in rule_set:
        clingo.parse_program(rule, lambda ast_rule: add_to_list_if_is_not_program(ast_rule, ast_rule_set))
    return ast_rule_set


def transform(program: str, sort: bool = True) -> ASTProgram:
    """
    Receives a logic program as a string and returns an ASTProgram. An ASTProgram consists of multiple
    RuleSets that each contain Rules that are interdependent of each.
    If they are sorted, the RuleSet at index i does only depend on RuleSets with index j>i.
    :param program: a logic program as a string
    :param sort: whether to sort by dependencies. This should always be true, vizlo does not guarantee correct results
    for unsorted programs.
    :return: a sorted (or unsorted) ASTProgram consisting of RuleSets consisting of Rules.
    """
    t = JustTheRulesTransformer()
    return t.transform(program, sort)
