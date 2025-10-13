class Node:
    def to_string(self):
        return "Node"

class Program(Node):
    def __init__(self):
        self.statements = []
    def to_string(self):
        return "".join(s.to_string() for s in self.statements)

class Statement(Node):
    pass

class Expression(Node):
    pass

class SetStatement(Statement):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def to_string(self):
        return f"set {self.name.to_string()} = {self.value.to_string()};"

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression
    def to_string(self):
        return self.expression.to_string()

class Identifier(Expression):
    def __init__(self, value):
        self.value = value
    def to_string(self):
        return self.value

class StringLiteral(Expression):
    def __init__(self, value):
        self.value = value
    def to_string(self):
        return f'"{self.value}"'

class NumberLiteral(Expression):
    def __init__(self, value):
        self.value = value
    def to_string(self):
        return str(self.value)

class CallExpression(Expression):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments
    def to_string(self):
        args = ", ".join(arg.to_string() for arg in self.arguments)
        return f"{self.function.to_string()}({args})"

class NewExpression(Expression):
    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments
    def to_string(self):
        args = ", ".join(arg.to_string() for arg in self.arguments)
        return f"new {self.class_name}({args})"
