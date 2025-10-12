from .lexer import Lexer, Token, TokenType
from .ast import (
    Program,
    SetStatement,
    ExpressionStatement,
    Identifier,
    StringLiteral,
    NumberLiteral,
)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.errors = []
        self.current_token = None
        self.peek_token = None
        self.next_token()
        self.next_token()

        self.prefix_parse_fns = {
            TokenType.IDENTIFIER: self.parse_identifier,
            TokenType.STRING: self.parse_string_literal,
            TokenType.NUMBER: self.parse_number_literal,
        }

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self):
        program = Program()
        while self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()
        return program

    def parse_statement(self):
        if self.current_token.type == TokenType.SET:
            return self.parse_set_statement()
        else:
            return self.parse_expression_statement()

    def parse_set_statement(self):
        stmt = SetStatement(name=None, value=None)
        if not self.expect_peek(TokenType.IDENTIFIER):
            return None
        stmt.name = Identifier(value=self.current_token.literal)
        if not self.expect_peek(TokenType.EQUAL):
            return None
        self.next_token()
        stmt.value = self.parse_expression()
        return stmt

    def parse_expression_statement(self):
        stmt = ExpressionStatement(expression=self.parse_expression())
        return stmt

    def parse_expression(self):
        prefix = self.prefix_parse_fns.get(self.current_token.type)
        if prefix is None:
            return None
        return prefix()

    def parse_identifier(self):
        return Identifier(value=self.current_token.literal)

    def parse_string_literal(self):
        return StringLiteral(value=self.current_token.literal)

    def parse_number_literal(self):
        return NumberLiteral(value=float(self.current_token.literal))

    def expect_peek(self, token_type):
        if self.peek_token.type == token_type:
            self.next_token()
            return True
        else:
            self.peek_error(token_type)
            return False

    def peek_error(self, token_type):
        msg = f"expected next token to be {token_type}, got {self.peek_token.type} instead"
        self.errors.append(msg)
