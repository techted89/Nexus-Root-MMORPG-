from enum import Enum

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = '('
    RIGHT_PAREN = ')'
    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'
    DOT = '.'
    COMMA = ','
    EQUAL = '='
    # Literals
    IDENTIFIER = 'IDENTIFIER'
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    # Keywords
    SET = 'SET'
    NEW = 'NEW'
    FUNC = 'FUNC'
    IF = 'IF'
    FOR = 'FOR'
    IN = 'IN'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    PRINT = 'PRINT'
    RUN = 'RUN'
    HELP = 'HELP'
    LS = 'LS'
    CAT = 'CAT'
    PING = 'PING'
    SCAN = 'SCAN'
    USE = 'USE'
    EDIT = 'EDIT'
    EXIT = 'EXIT'
    STATUS = 'STATUS'

    EOF = 'EOF'
    ILLEGAL = 'ILLEGAL'

class Token:
    def __init__(self, type, literal):
        self.type = type
        self.literal = literal

    def __str__(self):
        return f"Token({self.type}, {self.literal})"

class Lexer:
    def __init__(self, input_string):
        self.input = input_string
        self.position = 0
        self.read_position = 0
        self.ch = ''
        self.keywords = {
            "set": TokenType.SET,
            "new": TokenType.NEW,
            "func": TokenType.FUNC,
            "if": TokenType.IF,
            "for": TokenType.FOR,
            "in": TokenType.IN,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "print": TokenType.PRINT,
            "run": TokenType.RUN,
            "help": TokenType.HELP,
            "ls": TokenType.LS,
            "cat": TokenType.CAT,
            "ping": TokenType.PING,
            "scan": TokenType.SCAN,
            "use": TokenType.USE,
            "edit": TokenType.EDIT,
            "exit": TokenType.EXIT,
            "status": TokenType.STATUS,
        }
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = ''
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def skip_whitespace(self):
        while self.ch.isspace():
            self.read_char()

    def next_token(self):
        self.skip_whitespace()

        token = None
        if self.ch == '(':
            token = Token(TokenType.LEFT_PAREN, self.ch)
        elif self.ch == ')':
            token = Token(TokenType.RIGHT_PAREN, self.ch)
        elif self.ch == '{':
            token = Token(TokenType.LEFT_BRACE, self.ch)
        elif self.ch == '}':
            token = Token(TokenType.RIGHT_BRACE, self.ch)
        elif self.ch == '.':
            token = Token(TokenType.DOT, self.ch)
        elif self.ch == ',':
            token = Token(TokenType.COMMA, self.ch)
        elif self.ch == '=':
            token = Token(TokenType.EQUAL, self.ch)
        elif self.ch == '"':
            literal = self.read_string()
            token = Token(TokenType.STRING, literal)
        elif self.ch == '':
            token = Token(TokenType.EOF, "")
        else:
            if self.ch.isalpha() or self.ch == '$':
                literal = self.read_identifier()
                token_type = self.keywords.get(literal, TokenType.IDENTIFIER)
                return Token(token_type, literal)
            elif self.ch.isdigit():
                literal = self.read_number()
                return Token(TokenType.NUMBER, literal)
            else:
                token = Token(TokenType.ILLEGAL, self.ch)

        self.read_char()
        return token

    def read_identifier(self):
        start_pos = self.position
        while self.ch.isalpha() or self.ch.isdigit() or self.ch == '_' or self.ch == '$':
            self.read_char()
        return self.input[start_pos:self.position]

    def read_number(self):
        start_pos = self.position
        while self.ch.isdigit() or self.ch == '.':
            self.read_char()
        return self.input[start_pos:self.position]

    def read_string(self):
        self.read_char() # Consume the opening quote
        start_pos = self.position
        while self.ch != '"' and self.ch != '':
            self.read_char()
        return self.input[start_pos:self.position]
