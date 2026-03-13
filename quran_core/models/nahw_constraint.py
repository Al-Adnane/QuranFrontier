"""Nahw Constraint Grammar - Arabic Syntax as Constraint Satisfaction.

This model treats Arabic grammatical analysis (i'rab) as a constraint 
satisfaction problem (CSP) and uses neural networks to learn and solve
grammatical constraints.

Architecture:
    Input: Tokenized Arabic sentence
    Constraint Learner: Neural network that learns case assignment rules
    CSP Solver: Backtracking search with constraint propagation
    Output: Grammatical analysis with case assignments and roles

Based on frontierqu.linguistic.nahw for constraint definitions.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import copy


class GrammaticalRole(Enum):
    """Arabic grammatical roles."""
    MUBTADA = auto()      # Subject (topic)
    KHABAR = auto()       # Predicate
    FAIL = auto()         # Agent (doer)
    MAFUL = auto()        # Object (patient)
    MUDAF = auto()        # Construct state (first)
    MUDAF_ILAYH = auto()  # Construct state (second)
    MAJRUR = auto()       # Prepositional object
    HAL = auto()          # Circumstantial
    TAMYIZ = auto()       # Specification
    NIDA = auto()         # Vocative
    NAIB_FAIL = auto()    # Passive agent
    ISM_INNA = auto()     # Inna subject
    KHABAR_INNA = auto()  # Inna predicate


class CaseRequirement(Enum):
    """Arabic case requirements."""
    MARFU = auto()    # Nominative (raf')
    MANSUB = auto()   # Accusative (nasb)
    MAJRUR = auto()   # Genitive (jarr)
    MAJZUM = auto()   # Jussive (jazm)


# Case assignment rules (from nahw.py)
CASE_ASSIGNMENTS: Dict[GrammaticalRole, CaseRequirement] = {
    GrammaticalRole.MUBTADA: CaseRequirement.MARFU,
    GrammaticalRole.KHABAR: CaseRequirement.MARFU,
    GrammaticalRole.FAIL: CaseRequirement.MARFU,
    GrammaticalRole.MAFUL: CaseRequirement.MANSUB,
    GrammaticalRole.HAL: CaseRequirement.MANSUB,
    GrammaticalRole.TAMYIZ: CaseRequirement.MANSUB,
    GrammaticalRole.NIDA: CaseRequirement.MANSUB,
    GrammaticalRole.MUDAF: CaseRequirement.MARFU,
    GrammaticalRole.MUDAF_ILAYH: CaseRequirement.MAJRUR,
    GrammaticalRole.MAJRUR: CaseRequirement.MAJRUR,
    GrammaticalRole.NAIB_FAIL: CaseRequirement.MARFU,
    GrammaticalRole.ISM_INNA: CaseRequirement.MANSUB,
    GrammaticalRole.KHABAR_INNA: CaseRequirement.MARFU,
}

# Particles that govern cases
NASB_PARTICLES = {"إن", "أن", "كأن", "لكن", "ليت", "لعل"}
JARR_PARTICLES = {"في", "من", "إلى", "على", "عن", "ب", "ل", "ك", "حتى", "مع"}
JAZM_PARTICLES = {"لم", "لما", "لا الناهية", "إن الشرطية"}


@dataclass
class Constraint:
    """Grammatical constraint."""
    word_index: int
    role: Optional[GrammaticalRole]
    required_case: Optional[CaseRequirement]
    possible_roles: List[GrammaticalRole] = field(default_factory=list)
    possible_cases: List[CaseRequirement] = field(default_factory=list)
    is_resolved: bool = False
    
    def __post_init__(self):
        if not self.possible_roles:
            self.possible_roles = list(GrammaticalRole)
        if not self.possible_cases:
            self.possible_cases = list(CaseRequirement)


@dataclass
class SyntacticAnalysis:
    """Result of syntactic analysis."""
    tokens: List[str]
    roles: List[Optional[GrammaticalRole]]
    cases: List[Optional[CaseRequirement]]
    constraints: List[Constraint]
    is_valid: bool
    confidence: float
    parse_tree: Optional[Dict] = None


class ConstraintLearner(nn.Module):
    """Neural network that learns grammatical constraints."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        hidden_dim: int = 512,
        num_roles: int = len(GrammaticalRole),
        num_cases: int = len(CaseRequirement)
    ):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # Bidirectional LSTM for context
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            bidirectional=True,
            batch_first=True,
            dropout=0.3
        )
        
        # Role prediction head
        self.role_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_roles)
        )
        
        # Case prediction head
        self.case_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_cases)
        )
        
        # Particle detection
        self.particle_vocab = set(NASB_PARTICLES) | set(JARR_PARTICLES) | set(JAZM_PARTICLES)
        self.particle_embed = nn.Embedding(len(self.particle_vocab) + 1, embed_dim)
        
    def forward(
        self,
        input_ids: torch.Tensor,
        particle_mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Predict grammatical roles and cases.
        
        Args:
            input_ids: Token ids [batch, seq_len]
            particle_mask: Mask for particles [batch, seq_len]
        Returns:
            role_logits: [batch, seq_len, num_roles]
            case_logits: [batch, seq_len, num_cases]
        """
        # Embedding
        h = self.embedding(input_ids)  # [batch, seq_len, embed_dim]
        
        # LSTM encoding
        lstm_out, _ = self.lstm(h)  # [batch, seq_len, hidden*2]
        
        # Predictions
        role_logits = self.role_head(lstm_out)
        case_logits = self.case_head(lstm_out)
        
        return role_logits, case_logits
    
    def predict_constraints(
        self,
        input_ids: torch.Tensor,
        token_strings: List[str]
    ) -> List[Constraint]:
        """Predict constraints for a sentence.
        
        Args:
            input_ids: Token ids [1, seq_len]
            token_strings: Original token strings
        Returns:
            List of constraints
        """
        self.eval()
        
        with torch.no_grad():
            role_logits, case_logits = self.forward(input_ids)
            
            role_probs = F.softmax(role_logits[0], dim=-1)
            case_probs = F.softmax(case_logits[0], dim=-1)
            
            constraints = []
            roles_list = list(GrammaticalRole)
            cases_list = list(CaseRequirement)
            
            for i, (token, rp, cp) in enumerate(zip(token_strings, role_probs, case_probs)):
                # Check for particles
                if token in JARR_PARTICLES:
                    # Next word should be majrur
                    constraints.append(Constraint(
                        word_index=i,
                        role=GrammaticalRole.MAJRUR,
                        required_case=CaseRequirement.MAJRUR,
                        possible_roles=[GrammaticalRole.MAJRUR],
                        possible_cases=[CaseRequirement.MAJRUR],
                        is_resolved=True
                    ))
                elif token in NASB_PARTICLES:
                    # Next word should be mansub (ism inna)
                    constraints.append(Constraint(
                        word_index=i,
                        role=GrammaticalRole.ISM_INNA,
                        required_case=CaseRequirement.MANSUB,
                        possible_roles=[GrammaticalRole.ISM_INNA],
                        possible_cases=[CaseRequirement.MANSUB],
                        is_resolved=True
                    ))
                else:
                    # Use neural predictions
                    top_roles = [(roles_list[j], rp[j].item()) for j in range(len(roles_list))]
                    top_cases = [(cases_list[j], cp[j].item()) for j in range(len(cases_list))]
                    top_roles.sort(key=lambda x: -x[1])
                    top_cases.sort(key=lambda x: -x[1])
                    
                    # Filter by confidence threshold
                    possible_roles = [r for r, p in top_roles if p > 0.1]
                    possible_cases = [c for c, p in top_cases if p > 0.1]
                    
                    best_role, best_role_prob = top_roles[0]
                    best_case, best_case_prob = top_cases[0]
                    
                    # Apply CASE_ASSIGNMENTS constraint
                    if best_role in CASE_ASSIGNMENTS:
                        expected_case = CASE_ASSIGNMENTS[best_role]
                        if expected_case not in possible_cases:
                            possible_cases.append(expected_case)
                    
                    constraints.append(Constraint(
                        word_index=i,
                        role=best_role if best_role_prob > 0.5 else None,
                        required_case=CASE_ASSIGNMENTS.get(best_role),
                        possible_roles=possible_roles,
                        possible_cases=possible_cases,
                        is_resolved=len(possible_roles) == 1 and len(possible_cases) == 1
                    ))
            
            return constraints


class CSPSolver:
    """Constraint satisfaction problem solver for grammar."""
    
    def __init__(self, constraints: List[Constraint]):
        self.constraints = copy.deepcopy(constraints)
        self.n = len(constraints)
        
    def apply_constraint_propagation(self) -> bool:
        """Apply constraint propagation to reduce domains.
        
        Returns:
            True if any domain was reduced
        """
        changed = False
        
        # Rule 1: If word i is mubtada, word i+1 is likely khabar
        for i in range(self.n - 1):
            if self.constraints[i].is_resolved:
                if self.constraints[i].role == GrammaticalRole.MUBTADA:
                    # Khabar must be marfu
                    if GrammaticalRole.KHABAR not in self.constraints[i+1].possible_roles:
                        self.constraints[i+1].possible_roles.append(GrammaticalRole.KHABAR)
                        changed = True
        
        # Rule 2: Maf'ul must follow fail (verb-agent-object order)
        for i in range(self.n):
            if self.constraints[i].role == GrammaticalRole.FAIL:
                # Look for maf'ul in remaining words
                for j in range(i + 1, self.n):
                    if GrammaticalRole.MAFUL in self.constraints[j].possible_roles:
                        # Maf'ul must be mansub
                        if CaseRequirement.MANSUB not in self.constraints[j].possible_cases:
                            self.constraints[j].possible_cases.append(CaseRequirement.MANSUB)
                            changed = True
                        break
        
        # Rule 3: Mudaf-Mudaf ilayh relationship
        for i in range(self.n - 1):
            if GrammaticalRole.MUDAF in self.constraints[i].possible_roles:
                if GrammaticalRole.MUDAF_ILAYH in self.constraints[i+1].possible_roles:
                    # Mudaf ilayh must be majrur
                    if CaseRequirement.MAJRUR not in self.constraints[i+1].possible_cases:
                        self.constraints[i+1].possible_cases.append(CaseRequirement.MAJRUR)
                        changed = True
        
        return changed
    
    def solve(self, max_iterations: int = 100) -> bool:
        """Solve the CSP using constraint propagation and backtracking.
        
        Returns:
            True if solution found
        """
        # First apply constraint propagation
        for _ in range(max_iterations):
            if not self.apply_constraint_propagation():
                break
        
        # Check if all resolved
        all_resolved = all(c.is_resolved for c in self.constraints)
        
        if all_resolved:
            return True
        
        # Backtracking for unresolved
        return self._backtrack(0)
    
    def _backtrack(self, index: int) -> bool:
        """Backtracking search."""
        if index >= self.n:
            return True
        
        constraint = self.constraints[index]
        
        if constraint.is_resolved:
            return self._backtrack(index + 1)
        
        # Try each possible role
        for role in constraint.possible_roles:
            for case in constraint.possible_cases:
                # Check consistency with CASE_ASSIGNMENTS
                if role in CASE_ASSIGNMENTS:
                    expected = CASE_ASSIGNMENTS[role]
                    if expected != case:
                        continue
                
                # Assign
                constraint.role = role
                constraint.required_case = case
                constraint.is_resolved = True
                
                # Recurse
                if self._backtrack(index + 1):
                    return True
                
                # Backtrack
                constraint.is_resolved = False
                constraint.role = None
                constraint.required_case = None
        
        return False
    
    def get_solution(self) -> SyntacticAnalysis:
        """Get the solution as syntactic analysis."""
        roles = [c.role for c in self.constraints]
        cases = [c.required_case for c in self.constraints]
        is_valid = all(r is not None and c is not None for r, c in zip(roles, cases))
        
        # Compute confidence
        confidences = []
        for c in self.constraints:
            if c.is_resolved:
                role_conf = 1.0 / len(c.possible_roles) if c.possible_roles else 1.0
                case_conf = 1.0 / len(c.possible_cases) if c.possible_cases else 1.0
                confidences.append((role_conf + case_conf) / 2)
            else:
                confidences.append(0.0)
        
        return SyntacticAnalysis(
            tokens=[],
            roles=roles,
            cases=cases,
            constraints=self.constraints,
            is_valid=is_valid,
            confidence=sum(confidences) / len(confidences) if confidences else 0.0
        )


class NahwConstraintGrammar(nn.Module):
    """Main Nahw Constraint Grammar model."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 256,
        hidden_dim: int = 512
    ):
        super().__init__()
        
        self.constraint_learner = ConstraintLearner(
            vocab_size, embed_dim, hidden_dim
        )
        self.vocab_size = vocab_size
        
    def analyze(
        self,
        tokens: List[str],
        token_ids: List[int]
    ) -> SyntacticAnalysis:
        """Analyze Arabic sentence syntax.
        
        Args:
            tokens: Token strings
            token_ids: Token ids
        Returns:
            SyntacticAnalysis with roles and cases
        """
        self.eval()
        
        input_ids = torch.tensor([token_ids], dtype=torch.long)
        
        # Predict constraints
        constraints = self.constraint_learner.predict_constraints(input_ids, tokens)
        
        # Solve CSP
        solver = CSPSolver(constraints)
        solver.solve()
        
        solution = solver.get_solution()
        solution.tokens = tokens
        
        # Build parse tree
        solution.parse_tree = self._build_parse_tree(tokens, solution.roles)
        
        return solution
    
    def _build_parse_tree(
        self,
        tokens: List[str],
        roles: List[Optional[GrammaticalRole]]
    ) -> Dict:
        """Build a simple parse tree from roles."""
        tree = {'type': 'sentence', 'children': []}
        
        current_phrase = None
        
        for i, (token, role) in enumerate(zip(tokens, roles)):
            if role is None:
                continue
            
            # Determine phrase type
            if role in [GrammaticalRole.MUBTADA, GrammaticalRole.KHABAR]:
                phrase_type = 'nominal_phrase'
            elif role in [GrammaticalRole.FAIL, GrammaticalRole.MAFUL]:
                phrase_type = 'verbal_phrase'
            elif role == GrammaticalRole.MAJRUR:
                phrase_type = 'prepositional_phrase'
            else:
                phrase_type = 'phrase'
            
            if current_phrase is None or current_phrase['type'] != phrase_type:
                current_phrase = {'type': phrase_type, 'children': []}
                tree['children'].append(current_phrase)
            
            current_phrase['children'].append({
                'token': token,
                'role': role.name,
                'index': i
            })
        
        return tree
    
    def check_grammaticality(
        self,
        tokens: List[str],
        token_ids: List[int]
    ) -> Tuple[bool, float, List[str]]:
        """Check if sentence is grammatically valid.
        
        Args:
            tokens: Token strings
            token_ids: Token ids
        Returns:
            is_valid, confidence, list of errors
        """
        analysis = self.analyze(tokens, token_ids)
        
        errors = []
        
        # Check for common errors
        for i, (role, case) in enumerate(zip(analysis.roles, analysis.cases)):
            if role is None:
                errors.append(f"Word {i} '{tokens[i]}': No role assigned")
            elif case is None:
                errors.append(f"Word {i} '{tokens[i]}': No case assigned")
            elif role in CASE_ASSIGNMENTS:
                expected = CASE_ASSIGNMENTS[role]
                if expected != case:
                    errors.append(
                        f"Word {i} '{tokens[i]}': {role.name} requires "
                        f"{expected.name}, got {case.name}"
                    )
        
        return analysis.is_valid, analysis.confidence, errors
    
    def forward(
        self,
        input_ids: torch.Tensor,
        role_labels: Optional[torch.Tensor] = None,
        case_labels: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """Forward pass with optional loss computation.
        
        Args:
            input_ids: Token ids [batch, seq_len]
            role_labels: Optional role labels [batch, seq_len]
            case_labels: Optional case labels [batch, seq_len]
        Returns:
            Dict with predictions and optional loss
        """
        role_logits, case_logits = self.constraint_learner(input_ids)
        
        result = {
            'role_logits': role_logits,
            'case_logits': case_logits
        }
        
        if role_labels is not None:
            result['role_loss'] = F.cross_entropy(
                role_logits.view(-1, role_logits.size(-1)),
                role_labels.view(-1),
                ignore_index=-100
            )
        
        if case_labels is not None:
            result['case_loss'] = F.cross_entropy(
                case_logits.view(-1, case_logits.size(-1)),
                case_labels.view(-1),
                ignore_index=-100
            )
        
        if 'role_loss' in result and 'case_loss' in result:
            result['total_loss'] = result['role_loss'] + result['case_loss']
        
        return result


def create_nahw_model(
    vocab_size: int = 30000,
    pretrained: bool = False
) -> NahwConstraintGrammar:
    """Create NahwConstraintGrammar model."""
    model = NahwConstraintGrammar(vocab_size=vocab_size)
    
    if pretrained:
        # Would load pretrained weights
        pass
    
    return model
