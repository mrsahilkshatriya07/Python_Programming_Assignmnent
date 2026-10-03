"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 3
Topic: Recursive Expression Engine with Memoization
CO Mapping: CO-1, CO-2
Bloom Level: L6 (Create)

Description:
    Evaluates recursive arithmetic expressions containing integers, variables, +, -, *, 
    and nested parentheses with precedence rules.
    1. Lexical Tokenization & Recursive Descent Parsing (Shunting-Yard / AST-like Parsing).
    2. Cycle Detection: Uses an active call stack tracking set (`visiting`).
    3. Memoization Cache: Caches evaluated variable results to avoid recomputation.
    4. Input Validation: Reports 'CYCLE' for cyclic dependencies and 'INVALID' for syntax/semantic errors.
"""

import sys

# Increase recursion depth for deep expression trees
sys.setrecursionlimit(300000)


def tokenize(expr_str: str) -> list[str]:
    """
    Converts a raw string expression into a list of structural tokens.
    Handles spaces, numbers, operators, parentheses, and variable identifiers.
    """
    tokens = []
    i = 0
    n = len(expr_str)

    while i < n:
        ch = expr_str[i]

        if ch.isspace():
            i += 1
            continue

        if ch in "+-*()=":
            tokens.append(ch)
            i += 1
        elif ch.isdigit():
            start = i
            while i < n and expr_str[i].isdigit():
                i += 1
            tokens.append(expr_str[start:i])
        elif ch.isalpha() or ch == '_':
            start = i
            while i < n and (expr_str[i].isalnum() or expr_str[i] == '_'):
                i += 1
            tokens.append(expr_str[start:i])
        else:
            # Unrecognized character -> invalid syntax
            raise ValueError("Invalid character encountered")

    return tokens


class Evaluator:
    def __init__(self, var_env: dict[str, list[str]]):
        self.var_env = var_env
        self.memo = {}        # Memoization cache: var_name -> evaluated int value
        self.visiting = set() # Active call stack set for cycle detection

    def evaluate_expr(self, tokens: list[str]) -> int:
        """
        Parses and evaluates a token list using standard operator precedence rules:
        Parentheses () > Multiplication * > Addition/Subtraction +,-
        """
        # Parsing using Shunting-Yard Algorithm adapted for immediate evaluation
        output_stack = []
        op_stack = []

        prec = {'+': 1, '-': 1, '*': 2}

        def apply_op():
            if len(output_stack) < 2 or not op_stack:
                raise ValueError("Syntax Error: Insufficient operands")
            b = output_stack.pop()
            a = output_stack.pop()
            op = op_stack.pop()

            if op == '+':
                output_stack.append(a + b)
            elif op == '-':
                output_stack.append(a - b)
            elif op == '*':
                output_stack.append(a * b)

        i = 0
        n = len(tokens)
        expect_operand = True  # Tracks syntax structure

        while i < n:
            token = tokens[i]

            if token.isdigit():
                if not expect_operand:
                    raise ValueError("Syntax Error: Unexpected number")
                output_stack.append(int(token))
                expect_operand = False

            elif token.isalpha() or token == '_' or (token[0].isalpha() if token else False):
                if not expect_operand:
                    raise ValueError("Syntax Error: Unexpected variable")
                # Evaluate variable
                val = self.evaluate_var(token)
                output_stack.append(val)
                expect_operand = False

            elif token == '(':
                if not expect_operand:
                    raise ValueError("Syntax Error: Unexpected '('")
                op_stack.append('(')
                expect_operand = True

            elif token == ')':
                if expect_operand:
                    raise ValueError("Syntax Error: Unexpected ')'")
                while op_stack and op_stack[-1] != '(':
                    apply_op()
                if not op_stack or op_stack[-1] != '(':
                    raise ValueError("Syntax Error: Unmatched ')'")
                op_stack.pop()  # Pop '('
                expect_operand = False

            elif token in prec:
                if expect_operand:
                    raise ValueError(f"Syntax Error: Unexpected operator '{token}'")
                while op_stack and op_stack[-1] != '(' and prec[op_stack[-1]] >= prec[token]:
                    apply_op()
                op_stack.append(token)
                expect_operand = True

            else:
                raise ValueError(f"Syntax Error: Invalid token '{token}'")

            i += 1

        if expect_operand:
            raise ValueError("Syntax Error: Expression ended abruptly")

        while op_stack:
            if op_stack[-1] == '(':
                raise ValueError("Syntax Error: Unmatched '('")
            apply_op()

        if len(output_stack) != 1:
            raise ValueError("Syntax Error: Expression evaluation failed")

        return output_stack[0]

    def evaluate_var(self, var_name: str) -> int:
        """Evaluates a variable reference with cycle detection and memoization."""
        # 1. Return cached result if already computed
        if var_name in self.memo:
            return self.memo[var_name]

        # 2. Check for active dependency cycles
        if var_name in self.visiting:
            raise RecursionError("CYCLE")

        # 3. Check if variable exists in environment
        if var_name not in self.var_env:
            raise ValueError(f"Undefined variable: {var_name}")

        # 4. Evaluate with stack tracking
        self.visiting.add(var_name)
        val = self.evaluate_expr(self.var_env[var_name])
        self.visiting.remove(var_name)

        # 5. Memoize result
        self.memo[var_name] = val
        return val


def process_expressions(input_lines: list[str]) -> str:
    """Parses input lines, builds environment, and computes target expression result."""
    if not input_lines:
        return "INVALID"

    try:
        num_vars = int(input_lines[0].strip())
    except ValueError:
        return "INVALID"

    if len(input_lines) < num_vars + 2:
        return "INVALID"

    var_env = {}

    # Parse Variable Definitions
    for idx in range(1, num_vars + 1):
        line = input_lines[idx].strip()
        if not line:
            return "INVALID"

        if '=' not in line:
            return "INVALID"

        parts = line.split('=', 1)
        var_name = parts[0].strip()
        expr_str = parts[1].strip()

        # Validate Variable Identifier Name
        if not var_name or not (var_name.isalnum() or var_name.startswith('_')):
            return "INVALID"

        try:
            tokens = tokenize(expr_str)
            if not tokens:
                return "INVALID"
            var_env[var_name] = tokens
        except Exception:
            return "INVALID"

    # Target Expression
    target_expr_str = input_lines[num_vars + 1].strip()
    try:
        target_tokens = tokenize(target_expr_str)
        if not target_tokens:
            return "INVALID"
    except Exception:
        return "INVALID"

    evaluator = Evaluator(var_env)

    # Evaluate
    try:
        result = evaluator.evaluate_expr(target_tokens)
        return str(result)
    except RecursionError as re:
        if str(re) == "CYCLE":
            return "CYCLE"
        return "INVALID"
    except Exception:
        return "INVALID"


def main():
    """Main execution entry point reading input streams."""
    lines = sys.stdin.read().splitlines()
    if not lines:
        return

    result = process_expressions(lines)
    print(result)


if __name__ == "__main__":
    main()
