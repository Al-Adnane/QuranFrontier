"""RQL Grammar definition using PLY (Python Lex-Yacc).

Defines lexical tokens and parsing rules for RQL query language.
Supports FIND, MATCH, WHERE, RETURN, and constraint operators.
"""

from typing import List, Dict, Any, Optional


class RQLGrammar:
    """RQL Grammar specification."""

    def __init__(self):
        """Initialize RQL grammar with tokens and rules."""
        self.tokens = self._define_tokens()
        self.rules = self._define_rules()

    def _define_tokens(self) -> List[str]:
        """Define RQL tokens."""
        return [
            # Keywords
            "FIND",
            "MATCH",
            "WHERE",
            "RETURN",
            "AND",
            "OR",
            "NOT",
            # Literals
            "IDENTIFIER",
            "NUMBER",
            "STRING",
            # Operators
            "LPAREN",
            "RPAREN",
            "LBRACE",
            "RBRACE",
            "LBRACKET",
            "RBRACKET",
            "COLON",
            "COMMA",
            "DOT",
            "EQUALS",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "NEQ",
            "ARROW",
            # Special
            "PIPE",
        ]

    def _define_rules(self) -> Dict[str, Any]:
        """Define parsing rules."""
        return {
            "query": [
                "find_query",
                "match_query",
            ],
            "find_query": [
                "FIND entity_type WHERE conditions opt_return",
            ],
            "match_query": [
                "MATCH pattern WHERE conditions opt_return",
            ],
            "entity_type": [
                "IDENTIFIER",
            ],
            "conditions": [
                "condition",
                "conditions AND condition",
                "conditions OR condition",
            ],
            "condition": [
                "constraint",
                "function_call",
            ],
            "constraint": [
                "IDENTIFIER EQUALS value",
                "IDENTIFIER GT value",
                "IDENTIFIER LT value",
                "IDENTIFIER GTE value",
                "IDENTIFIER LTE value",
                "IDENTIFIER NEQ value",
            ],
            "function_call": [
                "IDENTIFIER LPAREN arguments RPAREN",
            ],
            "arguments": [
                "argument",
                "arguments COMMA argument",
            ],
            "argument": [
                "IDENTIFIER COLON value",
                "value",
            ],
            "value": [
                "STRING",
                "NUMBER",
                "IDENTIFIER",
            ],
            "pattern": [
                "node_pattern",
                "pattern ARROW relationship_pattern ARROW node_pattern",
            ],
            "node_pattern": [
                "LPAREN IDENTIFIER COLON IDENTIFIER RPAREN",
            ],
            "relationship_pattern": [
                "LBRACKET IDENTIFIER COLON IDENTIFIER RBRACKET",
            ],
            "opt_return": [
                "",
                "RETURN return_fields",
            ],
            "return_fields": [
                "IDENTIFIER",
                "return_fields COMMA IDENTIFIER",
            ],
        }

    def get_reserved_words(self) -> Dict[str, str]:
        """Get reserved keywords."""
        return {
            "FIND": "FIND",
            "MATCH": "MATCH",
            "WHERE": "WHERE",
            "RETURN": "RETURN",
            "AND": "AND",
            "OR": "OR",
            "NOT": "NOT",
        }

    def get_operator_precedence(self) -> List[tuple]:
        """Get operator precedence (lowest to highest)."""
        return [
            ("left", "OR"),
            ("left", "AND"),
            ("left", "NOT"),
            ("left", "GT", "LT", "GTE", "LTE", "EQUALS", "NEQ"),
        ]
