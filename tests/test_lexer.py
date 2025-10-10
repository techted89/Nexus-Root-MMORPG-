import unittest

from src.nexus_script.lexer import Lexer, Token, TokenType

class TestLexer(unittest.TestCase):
    def test_next_token(self):
        input_string = 'set $ip = "127.0.0.1"'
        lexer = Lexer(input_string)

        expected_tokens = [
            Token(TokenType.SET, "set"),
            Token(TokenType.IDENTIFIER, "$ip"),
            Token(TokenType.EQUAL, "="),
            Token(TokenType.STRING, "127.0.0.1"),
            Token(TokenType.EOF, ""),
        ]

        for expected_token in expected_tokens:
            token = lexer.next_token()
            self.assertEqual(token.type, expected_token.type)
            self.assertEqual(token.literal, expected_token.literal)

if __name__ == '__main__':
    unittest.main()
