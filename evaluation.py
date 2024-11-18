import re


class Node:
    def __init__(self, left=None, operator=None, right=None):
        self.left: Node | int | str = left
        self.operator: Node = operator
        self.right: Node = right

    def __repr__(self):
        if self.operator:
            return f"Node({self.left}, {self.operator}, {self.right})"
        return str(self.left)

    @staticmethod
    def is_node() -> bool:
        return True

    @staticmethod
    def is_number() -> bool:
        return False

    def __iter__(self):
        return iter([self.left, self.operator, self.right])

    def operate(self):
        match self.operator:
            case '+':
                return Number(self.left.left + self.right.left)
            case '-':
                return Number(self.left.left - self.right.left)
            case '*':
                return Number(self.left.left * self.right.left)
            case '/':
                return Number(self.left.left / self.right.left)

    def simplify(self):
        if self.is_number():
            return self

        if self.left is not None:
            self.left = self.left.simplify()

        if self.right is not None:
            self.right = self.right.simplify()

        if self.left.is_number() and self.right.is_number():
            return self.operate()

        return self


class Number(Node):
    def __init__(self, value):
        super().__init__(left=value)

    def __repr__(self):
        return f"Number({self.left})"

    def simplify(self):
        return self

    @staticmethod
    def is_number() -> bool:
        return True


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse_expression(self):
        try:
            node = self.parse_term()

            while self.peek() in ('+', '-'):
                operator = self.consume()
                right = self.parse_term()
                node = Node(node, operator, right)

            return node
        except Exception:
            return None

    def parse_term(self):
        node = self.parse_factor()

        while self.peek() in ('*', '/'):
            operator = self.consume()
            right = self.parse_factor()
            node = Node(node, operator, right)

        return node

    def parse_factor(self):
        token = self.peek()

        if re.match(r"\d+", token):
            self.consume()
            return Number(int(token))

        if token == '(':
            self.consume()
            node = self.parse_expression()
            self.consume()
            return node

        raise ValueError(f"Unknown token: {token}")

    @staticmethod
    def parse(expression):
        return Parser(tokenize(expression)).parse_expression()


def tokenize(expression):
    token_specification = [
        (r"\d+", "NUMBER"),
        (r"[+*/()\[\]\-\&]", "OP"),
        (r"\s+", None),
    ]
    tok_regex = '|'.join(f'(?P<{pair[1]}>{pair[0]})' for pair in token_specification if pair[1])
    tokens = [match.group(0) for match in re.finditer(tok_regex, expression)]
    return tokens
