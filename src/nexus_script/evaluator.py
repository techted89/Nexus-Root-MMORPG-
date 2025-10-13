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
from datetime import datetime, timedelta

class Evaluator:
    def __init__(self, player, themes):
        self.player = player
        self.themes = themes
        self.environment = {}
        self.builtins = {
            "ls": self._ls,
            "cat": self._cat,
            "set-theme": self._set_theme,
            "set-prompt": self._set_prompt,
            "mine-hash": self._mine_hash,
            "status": self._status,
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
            # Simplified for now
            return None
        return None

    def eval_statements(self, statements):
        result = None
        for statement in statements:
            result = self.eval(statement)
        return result

    def _ls(self, args):
        # TODO: Implement ls
        pass

    def _cat(self, args):
        # TODO: Implement cat
        pass

    def _set_theme(self, args):
        if not args:
            return "set-theme: missing operand"
        theme_name = args[0]
        if theme_name not in self.themes:
            return f"set-theme: unknown theme '{theme_name}'"
        self.player.vc_state.theme = theme_name
        return f"Theme set to '{theme_name}'."

    def _set_prompt(self, args):
        if not args:
            return "set-prompt: missing operand"
        self.player.vc_state.prompt_format = args[0]
        return "Prompt format updated."

    def _mine_hash(self, args):
        if not args:
            return "mine-hash: missing operand"
        try:
            duration_hours = int(args[0])
            self.player.vc_state.passive_mining_end_time = datetime.now() + timedelta(hours=duration_hours)
            return f"Passive hash mining started for {duration_hours} hours."
        except (ValueError, IndexError):
            return "mine-hash: invalid duration"

    def _status(self, args):
        if self.player.vc_state.passive_mining_end_time:
            if datetime.now() < self.player.vc_state.passive_mining_end_time:
                remaining = self.player.vc_state.passive_mining_end_time - datetime.now()
                return f"Passive mining in progress. Time remaining: {remaining}"
            else:
                return "Passive mining complete. Run 'status' again to collect."
        return "No passive mining in progress."
