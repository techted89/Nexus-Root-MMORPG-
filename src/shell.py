from .player import Player
from .nexus_script.lexer import Lexer
from .nexus_script.parser import Parser
from .nexus_script.evaluator import Evaluator

class NexusShell:
    def __init__(self):
        self.player = Player("Jules")
        self.evaluator = Evaluator(self.player)

    def execute(self, input_string, edit_content=None):
        if edit_content:
            self.evaluator._edit([input_string, edit_content])
            return

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
                if not line:
                    continue

                if line.startswith("edit "):
                    filename = line.split(" ")[1]
                    print(f"Editing {filename}. Type ':wq' to save and exit.")
                    buffer = []
                    while True:
                        editor_line = input()
                        if editor_line == ':wq':
                            break
                        buffer.append(editor_line)

                    content = "\n".join(buffer)
                    self.execute(filename, edit_content=content)

                else:
                    self.execute(line)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Nexus Root.")
                break
