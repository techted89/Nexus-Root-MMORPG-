import unittest

from src.nexus_script.lexer import Lexer
from src.nexus_script.parser import Parser
from src.nexus_script.ast import SetStatement, Identifier, StringLiteral

class TestParser(unittest.TestCase):
    def test_set_statement(self):
        input_string = 'set $ip = "127.0.0.1"'
        lexer = Lexer(input_string)
        parser = Parser(lexer)
        program = parser.parse_program()

        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, SetStatement)
        self.assertEqual(stmt.name.value, "$ip")
        self.assertEqual(stmt.value.value, "127.0.0.1")

if __name__ == '__main__':
    unittest.main()
