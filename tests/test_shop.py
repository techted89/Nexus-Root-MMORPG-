import unittest
import time
from src.player import Player
from src.nexus_script.evaluator import Evaluator
from src.nexus_script.lexer import Lexer
from src.nexus_script.parser import Parser
from src.upgrade_data import UPGRADE_DATA

class TestShop(unittest.TestCase):
    def setUp(self):
        self.player = Player("TestPlayer")
        self.evaluator = Evaluator(self.player, {})

    def _execute(self, command):
        lexer = Lexer(command)
        parser = Parser(lexer)
        program = parser.parse_program()
        return self.evaluator.eval(program)

    def test_shop_display(self):
        output = self._execute("shop()")
        self.assertIn("--- Hardware Shop ---", output)
        self.assertIn("CPU (Current Tier: 1)", output)
        self.assertIn("RAM (Current Tier: 1)", output)

    def test_buy_success(self):
        self.player.vc_state.credits = 100
        output = self._execute('buy("cpu")')
        self.assertEqual(self.player.vc_state.cpu_tier, 2)
        self.assertEqual(self.player.vc_state.credits, 0)
        self.assertIn("Successfully purchased CPU Tier 2", output)

    def test_buy_insufficient_credits(self):
        self.player.vc_state.credits = 50
        output = self._execute('buy("cpu")')
        self.assertEqual(self.player.vc_state.cpu_tier, 1)
        self.assertEqual(self.player.vc_state.credits, 50)
        self.assertIn("insufficient credits", output)

    def test_buy_max_tier(self):
        self.player.vc_state.cpu_tier = 10
        output = self._execute('buy("cpu")')
        self.assertEqual(self.player.vc_state.cpu_tier, 10)
        self.assertIn("already at max tier", output)

    def test_buy_invalid_component(self):
        output = self._execute('buy("gpu")')
        self.assertIn("unknown component", output)

    def test_hashcrack_speed_increase(self):
        # Tier 1 CPU speed is 5 seconds
        start_time = time.time()
        self._execute("hashcrack()")
        end_time = time.time()
        self.assertGreaterEqual(end_time - start_time, 5)

        # Buy Tier 2 CPU
        self.player.vc_state.credits = 100
        self._execute('buy("cpu")')

        # Tier 2 CPU speed should be less than 5 seconds
        start_time = time.time()
        self._execute("hashcrack()")
        end_time = time.time()
        self.assertLess(end_time - start_time, 5)

if __name__ == '__main__':
    unittest.main()
