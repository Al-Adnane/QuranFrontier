"""RQL Parser - Converts RQL text to Abstract Syntax Tree.

Implements recursive descent parser for RQL query language.
Handles FIND, MATCH, WHERE, RETURN, and constraint expressions.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Condition:
    """Represents a query condition."""

    operator: str  # e.g., "=", ">", "<", "AND", "OR"
    left: Any
    right: Any = None

    def __hash__(self):
        return hash((self.operator, id(self.left), id(self.right)))

    def __eq__(self, other):
        if not isinstance(other, Condition):
            return False
        return (
            self.operator == other.operator
            and self.left == other.left
            and self.right == other.right
        )


@dataclass
class FunctionCall:
    """Represents a function call in query."""

    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, FunctionCall):
            return False
        return self.name == other.name and self.arguments == other.arguments


@dataclass
class QueryAST:
    """Abstract Syntax Tree for RQL query."""

    operation: str  # "FIND", "MATCH"
    entity_type: Optional[str] = None
    pattern: Optional[str] = None
    conditions: List[Any] = field(default_factory=list)
    return_fields: List[str] = field(default_factory=list)


class RQLParser:
    """RQL Query Parser - converts text to AST."""

    def __init__(self):
        """Initialize parser."""
        self.tokens = []
        self.pos = 0
        self.query_text = ""

    def parse(self, query: str) -> QueryAST:
        """Parse RQL query string to AST.

        Args:
            query: RQL query string

        Returns:
            QueryAST: Parsed abstract syntax tree

        Raises:
            SyntaxError: If query is malformed
        """
        self.query_text = query
        self.tokens = self._tokenize(query)
        self.pos = 0

        if not self.tokens:
            raise SyntaxError("Empty query")

        return self._parse_query()

    def _tokenize(self, query: str) -> List[Tuple[str, str]]:
        """Tokenize RQL query.

        Args:
            query: Query string

        Returns:
            List of (token_type, token_value) tuples
        """
        # Token patterns
        token_patterns = [
            ("FIND", r"\bFIND\b"),
            ("MATCH", r"\bMATCH\b"),
            ("WHERE", r"\bWHERE\b"),
            ("RETURN", r"\bRETURN\b"),
            ("AND", r"\bAND\b"),
            ("OR", r"\bOR\b"),
            ("NOT", r"\bNOT\b"),
            ("STRING", r"'[^']*'|\"[^\"]*\""),
            ("NUMBER", r"-?\d+(\.\d+)?"),
            ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("LBRACE", r"\{"),
            ("RBRACE", r"\}"),
            ("LBRACKET", r"\["),
            ("RBRACKET", r"\]"),
            ("ARROW", r"->"),
            ("GTE", r">="),
            ("LTE", r"<="),
            ("NEQ", r"!=|<>"),
            ("GT", r">"),
            ("LT", r"<"),
            ("EQUALS", r"="),
            ("COLON", r":"),
            ("COMMA", r","),
            ("DOT", r"\."),
            ("PIPE", r"\|"),
            ("WHITESPACE", r"\s+"),
        ]

        # Compile patterns
        token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_patterns)
        tokens = []

        for match in re.finditer(token_regex, query):
            token_type = match.lastgroup
            token_value = match.group()

            if token_type == "WHITESPACE":
                continue

            tokens.append((token_type, token_value))

        return tokens

    def _current_token(self) -> Optional[Tuple[str, str]]:
        """Get current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _peek_token(self, offset: int = 1) -> Optional[Tuple[str, str]]:
        """Peek ahead at token."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _consume(self, expected_type: Optional[str] = None) -> Tuple[str, str]:
        """Consume current token.

        Args:
            expected_type: Expected token type (optional validation)

        Returns:
            Token tuple

        Raises:
            SyntaxError: If token type doesn't match
        """
        token = self._current_token()
        if token is None:
            raise SyntaxError(f"Unexpected end of query, expected {expected_type}")

        token_type, token_value = token
        if expected_type and token_type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, got {token_type} ({token_value})"
            )

        self.pos += 1
        return token

    def _parse_query(self) -> QueryAST:
        """Parse top-level query."""
        token = self._current_token()
        if not token:
            raise SyntaxError("Empty query")

        token_type, _ = token

        if token_type == "FIND":
            return self._parse_find_query()
        elif token_type == "MATCH":
            return self._parse_match_query()
        else:
            raise SyntaxError(f"Expected FIND or MATCH, got {token_type}")

    def _parse_find_query(self) -> QueryAST:
        """Parse FIND query."""
        self._consume("FIND")

        # Parse entity type
        entity_token = self._consume("IDENTIFIER")
        entity_type = entity_token[1]

        # Parse WHERE clause
        conditions = []
        if self._current_token() and self._current_token()[0] == "WHERE":
            self._consume("WHERE")
            conditions = self._parse_conditions()

        # Parse RETURN clause
        return_fields = []
        if self._current_token() and self._current_token()[0] == "RETURN":
            self._consume("RETURN")
            return_fields = self._parse_return_fields()

        return QueryAST(
            operation="FIND",
            entity_type=entity_type,
            conditions=conditions,
            return_fields=return_fields,
        )

    def _parse_match_query(self) -> QueryAST:
        """Parse MATCH query."""
        self._consume("MATCH")

        # Parse pattern
        pattern = self._parse_pattern()

        # Parse WHERE clause
        conditions = []
        if self._current_token() and self._current_token()[0] == "WHERE":
            self._consume("WHERE")
            conditions = self._parse_conditions()

        # Parse RETURN clause
        return_fields = []
        if self._current_token() and self._current_token()[0] == "RETURN":
            self._consume("RETURN")
            return_fields = self._parse_return_fields()

        return QueryAST(
            operation="MATCH",
            pattern=pattern,
            conditions=conditions,
            return_fields=return_fields,
        )

    def _parse_conditions(self) -> List[Any]:
        """Parse WHERE conditions with AND/OR logic."""
        conditions = []
        conditions.append(self._parse_condition())

        while self._current_token() and self._current_token()[0] in ("AND", "OR"):
            op_token = self._consume()
            op = op_token[1]
            right_cond = self._parse_condition()
            conditions.append(Condition(operator=op, left=conditions[-1], right=right_cond))

        return conditions

    def _parse_condition(self) -> Any:
        """Parse single condition."""
        token = self._current_token()
        if not token:
            raise SyntaxError("Expected condition")

        token_type, token_value = token

        if token_type == "IDENTIFIER":
            # Look ahead to determine if function or constraint
            peek = self._peek_token()
            if peek and peek[0] == "LPAREN":
                return self._parse_function_call()
            elif peek and peek[0] == "DOT":
                # Dotted attribute access (e.g., v.surah)
                return self._parse_constraint()
            else:
                return self._parse_constraint()
        else:
            raise SyntaxError(f"Expected constraint or function, got {token_type}")

    def _parse_constraint(self) -> Condition:
        """Parse comparison constraint."""
        left_token = self._consume("IDENTIFIER")
        left = left_token[1]

        # Handle dotted attribute access (e.g., v.surah)
        if self._current_token() and self._current_token()[0] == "DOT":
            self._consume("DOT")
            attr_token = self._consume("IDENTIFIER")
            left = f"{left}.{attr_token[1]}"

        op_token = self._current_token()
        if not op_token or op_token[0] not in ("EQUALS", "GT", "LT", "GTE", "LTE", "NEQ"):
            raise SyntaxError(f"Expected comparison operator, got {op_token}")

        op = self._consume()[1]
        right = self._parse_value()

        return Condition(operator=op, left=left, right=right)

    def _parse_function_call(self) -> FunctionCall:
        """Parse function call like naskh(abrogates: '2:180')."""
        func_name = self._consume("IDENTIFIER")[1]
        self._consume("LPAREN")

        arguments = {}
        while self._current_token() and self._current_token()[0] != "RPAREN":
            arg_name = self._consume("IDENTIFIER")[1]
            self._consume("COLON")
            arg_value = self._parse_value()
            arguments[arg_name] = arg_value

            if self._current_token() and self._current_token()[0] == "COMMA":
                self._consume("COMMA")

        self._consume("RPAREN")

        return FunctionCall(name=func_name, arguments=arguments)

    def _parse_value(self) -> Any:
        """Parse value (string, number, or identifier)."""
        token = self._current_token()
        if not token:
            raise SyntaxError("Expected value")

        token_type, token_value = token

        if token_type == "STRING":
            self._consume("STRING")
            # Remove quotes
            return token_value[1:-1]
        elif token_type == "NUMBER":
            self._consume("NUMBER")
            # Try to parse as int, fallback to float
            try:
                return int(token_value)
            except ValueError:
                return float(token_value)
        elif token_type == "IDENTIFIER":
            self._consume("IDENTIFIER")
            return token_value
        else:
            raise SyntaxError(f"Expected value, got {token_type}")

    def _parse_pattern(self) -> str:
        """Parse graph pattern like (v:Verse)-[r:ABROGATES]->(v2:Verse)."""
        pattern_parts = []

        while self._current_token() and self._current_token()[0] != "WHERE":
            token_type, token_value = self._current_token()

            if token_type in ("LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "ARROW", "COLON"):
                pattern_parts.append(token_value)
                self._consume(token_type)
            elif token_type == "IDENTIFIER":
                pattern_parts.append(token_value)
                self._consume("IDENTIFIER")
            else:
                break

        return "".join(pattern_parts)

    def _parse_return_fields(self) -> List[str]:
        """Parse RETURN field list."""
        fields = []

        # Parse first field
        field_name = self._consume("IDENTIFIER")[1]
        if self._current_token() and self._current_token()[0] == "DOT":
            self._consume("DOT")
            field_name += "." + self._consume("IDENTIFIER")[1]
        fields.append(field_name)

        # Parse remaining fields
        while self._current_token() and self._current_token()[0] == "COMMA":
            self._consume("COMMA")
            field_name = self._consume("IDENTIFIER")[1]
            if self._current_token() and self._current_token()[0] == "DOT":
                self._consume("DOT")
                field_name += "." + self._consume("IDENTIFIER")[1]
            fields.append(field_name)

        return fields
