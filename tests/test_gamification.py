import unittest
from src.player import Player
from src.nexus_script.evaluator import Evaluator
from src.nexus_script.lexer import Lexer
from src.nexus_script.parser import Parser
from src.nexus_script.themes import THEMES

class TestGamification(unittest.TestCase):
    def setUp(self):
        self.player = Player("TestPlayer")
        self.evaluator = Evaluator(self.player, THEMES)

    def _execute(self, command):
        lexer = Lexer(command)
        parser = Parser(lexer)
        program = parser.parse_program()
        print(f"AST for '{command}': {program.to_string()}")
        return self.evaluator.eval(program)

    def test_set_theme(self):
        self._execute('set-theme("cyberpunk")')
        self.assertEqual(self.player.vc_state.theme, "cyberpunk")

    def test_set_prompt(self):
        self._execute('set-prompt("hacker> ")')
        self.assertEqual(self.player.vc_state.prompt_format, "hacker> ")

    def test_mine_hash(self):
        self._execute("mine-hash(1)")
        self.assertIsNotNone(self.player.vc_state.passive_mining_end_time)

if __name__ == '__main__':
    unittest.main()
