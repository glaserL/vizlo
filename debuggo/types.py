from typing import List
from .solve.solver import SolverState

SolvingHistory = List[SolverState]
RuleSet = List[str]
Program = List[RuleSet]