from .player import Player
from .nexus_script.lexer import Lexer
from .nexus_script.parser import Parser
from .nexus_script.evaluator import Evaluator

class NexusShell:
    def __init__(self):
        self.player = Player("Jules")
        self.evaluator = Evaluator()

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
        while True:
            try:
                line = input(f"{self.player.name}@nexus-root> ")
                if line:
                    self.execute(line)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Nexus Root.")
                break
