class Node:
    pass

class Program(Node):
    def __init__(self):
        self.statements = []

class Statement(Node):
    pass

class Expression(Node):
    pass

class SetStatement(Statement):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class Identifier(Expression):
    def __init__(self, value):
        self.value = value

class StringLiteral(Expression):
    def __init__(self, value):
        self.value = value

class NumberLiteral(Expression):
    def __init__(self, value):
        self.value = value

class CallExpression(Expression):
    def __init__(self, function, arguments, flags):
        self.function = function
        self.arguments = arguments
        self.flags = flags

class NewExpression(Expression):
    def __init__(self, class_name, arguments):
        self.class_name = class_name
        self.arguments = arguments
