from .ast import (
    Program,
    SetStatement,
    ExpressionStatement,
    Identifier,
    StringLiteral,
    NumberLiteral,
)

class Evaluator:
    def __init__(self):
        self.environment = {}
        self.builtins = {
            "ls": self._ls,
            "cat": self._cat,
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
