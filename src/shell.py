from .player import Player
from .nexus_script.lexer import Lexer
from .nexus_script.parser import Parser
from .nexus_script.evaluator import Evaluator
from .themes import THEMES
from datetime import datetime

class NexusShell:
    def __init__(self):
        self.player = Player("Jules")
        self.evaluator = Evaluator(self.player, THEMES)

    def _check_passive_mining(self):
        if self.player.vc_state.passive_mining_end_time and datetime.now() >= self.player.vc_state.passive_mining_end_time:
            self.player.vc_state.credits += 100 # Award 100 credits for completion
            self.player.vc_state.passive_mining_end_time = None
            print("\n[Passive hash mining complete. 100 credits awarded.]")

    def execute(self, input_string):
        lexer = Lexer(input_string)
        parser = Parser(lexer)
        program = parser.parse_program()

        if parser.errors:
            for error in parser.errors:
                print(error)
            return

        result = self.evaluator.eval(program)
        if result is not None:
            print(result)

    def main_loop(self):
        self._check_passive_mining() # Check on startup
        while True:
            try:
                self._check_passive_mining() # Check before each command
                theme = THEMES.get(self.player.vc_state.theme, THEMES["default"])
                prompt = theme["prompt"] + self.player.vc_state.prompt_format.format(user=self.player.name) + theme["reset"]
                line = input(prompt)
                if line:
                    self.execute(line)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Nexus Root.")
                break
