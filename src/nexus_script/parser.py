from .lexer import Lexer, Token, TokenType
from .ast import (
    Program,
    SetStatement,
    ExpressionStatement,
    Identifier,
    StringLiteral,
    NumberLiteral,
    CallExpression,
    NewExpression,
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
            TokenType.NEW: self.parse_new_expression,
        }
        self.infix_parse_fns = {
            TokenType.LEFT_PAREN: self.parse_call_expression,
        }
        self.precedences = {
            TokenType.LEFT_PAREN: 1
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

    def parse_expression(self, precedence=0):
        prefix = self.prefix_parse_fns.get(self.current_token.type)
        if prefix is None:
            return None

        left_exp = prefix()

        while self.peek_token.type != TokenType.EOF and precedence < self.peek_precedence():
            infix = self.infix_parse_fns.get(self.peek_token.type)
            if infix is None:
                return left_exp
            self.next_token()
            left_exp = infix(left_exp)

        return left_exp

    def parse_identifier(self):
        return Identifier(value=self.current_token.literal)

    def parse_string_literal(self):
        return StringLiteral(value=self.current_token.literal)

    def parse_number_literal(self):
        return NumberLiteral(value=float(self.current_token.literal))

    def parse_new_expression(self):
        self.next_token() # consume 'new'
        class_name = self.current_token.literal
        self.next_token() # consume class name
        arguments = self.parse_expression_list(TokenType.RIGHT_PAREN)
        return NewExpression(class_name=class_name, arguments=arguments)

    def parse_call_expression(self, function):
        arguments, flags = self.parse_expression_list(TokenType.RIGHT_PAREN)
        return CallExpression(function=function, arguments=arguments, flags=flags)

    def parse_expression_list(self, end_token):
        args = []
        flags = []
        if self.peek_token.type == end_token:
            self.next_token()
            return args, flags

        self.next_token()
        if self.current_token.type == TokenType.FLAG:
            flags.append(self.current_token.literal)
        else:
            args.append(self.parse_expression())

        while self.peek_token.type == TokenType.COMMA:
            self.next_token()
            self.next_token()
            if self.current_token.type == TokenType.FLAG:
                flags.append(self.current_token.literal)
            else:
                args.append(self.parse_expression())

        if not self.expect_peek(end_token):
            return None

        return args, flags


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

    def peek_precedence(self):
        return self.precedences.get(self.peek_token.type, 0)

    def current_precedence(self):
        return self.precedences.get(self.current_token.type, 0)
