import os
import time
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
from .objects import IP_Object

class Evaluator:
    def __init__(self, player):
        self.player = player
        self.environment = {}
        self.builtins = {
            "ls": self._ls,
            "cat": self._cat,
            "print": self._print,
            "edit": self._edit,
            "run": self._run,
            "hashcrack": self._hashcrack,
            "man": self._man,
        }
        self.virtual_fs = {
            "docs": {
                "tutorial.txt": "Welcome to Nexus Root!",
                "pivot_fragment.txt": "CMD_DECLARE: PIVOT"
            },
            "bin": {}
        }
        self.man_pages = {
            "ls": "NAME\n\tls - list contents of virtual directories\nSYNOPSIS\n\tls [path]",
            "cat": "NAME\n\tcat - print contents of a file\nSYNOPSIS\n\tcat [filepath]",
            "print": "NAME\n\tprint - display text or variable contents\nSYNOPSIS\n\tprint [message]",
            "edit": "NAME\n\tedit - create or edit a file\nSYNOPSIS\n\tedit [filename]",
            "run": "NAME\n\trun - execute a saved NexusScript module\nSYNOPSIS\n\trun [module_name]",
            "set": "NAME\n\tset - declare and assign a variable or object\nSYNOPSIS\n\tset $[variable] = [value]",
            "hashcrack": "NAME\n\thashcrack - crack a password hash\nSYNOPSIS\n\thashcrack [hash]",
            "pivot": "NAME\n\tpivot - use a compromised asset as a proxy\nSYNOPSIS\n\tpivot [compromised_ip] [command]",
        }


    def eval(self, node):
        if isinstance(node, Program):
            return self.eval_statements(node.statements)
        elif isinstance(node, ExpressionStatement):
            return self.eval(node.expression)
        elif isinstance(node, SetStatement):
            value = self.eval(node.value)
            self.environment[node.name.value] = value
            return value
        elif isinstance(node, Identifier):
            if node.value in self.builtins:
                if self.player.check_kmap(node.value) == "LOCKED":
                    return f"Command not found: {node.value}"
                return self.builtins[node.value]
            return self.environment.get(node.value, None)
        elif isinstance(node, StringLiteral):
            return node.value
        elif isinstance(node, NumberLiteral):
            return node.value
        elif isinstance(node, CallExpression):
            func = self.eval(node.function)
            if not callable(func):
                return f"Error: {node.function.value} is not a function"
            args = [self.eval(arg) for arg in node.arguments]
            return func(args)
        elif isinstance(node, NewExpression):
            if node.class_name == "IP":
                args = [self.eval(arg) for arg in node.arguments]
                return IP_Object(args)
        return None

    def eval_statements(self, statements):
        result = None
        for statement in statements:
            result = self.eval(statement)
        return result

    def _ls(self, args):
        path = args[0] if args else "."
        if path == ".":
            return "\n".join(self.virtual_fs.keys())

        parts = path.split('/')
        current = self.virtual_fs
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return f"ls: cannot access '{path}': No such file or directory"

        if isinstance(current, dict):
            return "\n".join(current.keys())
        else:
            return path


    def _cat(self, args):
        if not args:
            return "cat: missing operand"
        path = args[0]
        parts = path.split('/')
        current = self.virtual_fs
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return f"cat: cannot access '{path}': No such file or directory"

        if isinstance(current, str):
            discovery = self.player.scan_file_for_fragment(current)
            if discovery:
                print(discovery)
            return current
        else:
            return f"cat: {path}: Is a directory"


    def _print(self, args):
        print(*args)
        return None

    def _edit(self, args):
        if not args:
            return "edit: missing operand"
        filename = args[0]
        content = args[1]

        # For simplicity, saving in the root of the virtual fs
        self.virtual_fs[filename] = content
        return f"File '{filename}' saved."

    def _run(self, args):
        if not args:
            return "run: missing operand"
        filename = args[0]
        if filename not in self.virtual_fs:
            return f"run: cannot find script '{filename}'"

        script_content = self.virtual_fs[filename]

        from .lexer import Lexer
        from .parser import Parser

        lexer = Lexer(script_content)
        parser = Parser(lexer)
        program = parser.parse_program()

        if parser.errors:
            for error in parser.errors:
                print(error)
            return

        return self.eval(program)

    def _hashcrack(self, args):
        if not self.player.is_vip:
            print("Cracking hash (standard algorithm)...")
            time.sleep(5)
        else:
            print("Cracking hash (quantum core)...")
        return "password123"

    def _man(self, args):
        if not args:
            return "man: missing operand"
        command = args[0]
        if self.player.check_kmap(command) == "LOCKED":
            return f"man: command not found: {command}"

        return self.man_pages.get(command, f"No manual entry for {command}")
