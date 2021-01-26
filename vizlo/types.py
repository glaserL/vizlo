from typing import List

import clingo

RuleSet = List[str]
Program = List[RuleSet]
ASTRuleSet = List[clingo.ast.AST]
FlatASTProgram = ASTRuleSet
ASTProgram = List[ASTRuleSet]
