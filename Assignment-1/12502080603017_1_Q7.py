"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 7
Topic: Interactive Formula Validator with Custom Exceptions
CO Mapping: CO-1, CO-2
Bloom Level: L5 (Evaluate)

Description:
    Interactive formula evaluator and validator supporting arithmetic operations
    (+, -, *, /, %) and variable assignments (var = value).
    Custom Exceptions Raised:
    1. FormulaFormatError: Invalid syntax or missing tokens.
    2. UnknownVariableError: Reference to an unassigned variable identifier.
    3. UnsupportedOperatorError: Operator is not in (+, -, *, /, %).
    4. DivisionByZeroError: Division or modulo by zero.
"""

import sys


class FormulaError(Exception):
    """Base exception class for formula validation errors."""
    pass


class FormulaFormatError(FormulaError):
    """Raised when formula string violates token or assignment structure."""
    pass


class UnknownVariableError(FormulaError):
    """Raised when an uninitialized variable identifier is referenced."""
    pass


class UnsupportedOperatorError(FormulaError):
    """Raised when an operator is not supported by the evaluator."""
    pass


class DivisionByZeroError(FormulaError):
    """Raised when an operation attempts division or modulo by zero."""
    pass


class FormulaEvaluator:
    """
    Evaluates arithmetic expressions and manages environment variables.
    """
    SUPPORTED_OPERATORS = {'+', '-', '*', '/', '%'}

    def __init__(self):
        self.variables: dict[str, float] = {}

    def _resolve_operand(self, token: str) -> float:
        """
        Resolves a token into a float value or raises an appropriate exception.
        """
        # Attempt to parse directly as a number
        try:
            return float(token)
        except ValueError:
            pass

        # Validate variable identifier naming rule
        if token.isidentifier():
            if token in self.variables:
                return self.variables[token]
            raise UnknownVariableError(f"Unknown variable '{token}'")

        raise FormulaFormatError(f"Invalid operand token '{token}'")

    def evaluate_line(self, line: str):
        """
        Processes a single input line for assignment or expression evaluation.
        
        Returns:
            float/int result if valid expression, or None if assignment line.
        """
        tokens = line.strip().split()

        # Handle Variable Assignment: var_name = value / expression
        if '=' in tokens:
            if len(tokens) == 3 and tokens[1] == '=':
                var_name = tokens[0]
                val_token = tokens[2]

                if not var_name.isidentifier():
                    raise FormulaFormatError(f"Invalid variable identifier '{var_name}'")

                val = self._resolve_operand(val_token)
                self.variables[var_name] = val
                return None
            else:
                raise FormulaFormatError("Invalid assignment format. Expected 'var = value'")

        # Handle standard formula evaluation: operand1 operator operand2
        if len(tokens) != 3:
            raise FormulaFormatError("Invalid formula format. Expected 'operand1 operator operand2'")

        operand1_str, operator, operand2_str = tokens

        val1 = self._resolve_operand(operand1_str)
        val2 = self._resolve_operand(operand2_str)

        if operator not in self.SUPPORTED_OPERATORS:
            raise UnsupportedOperatorError(f"Unsupported operator '{operator}'")

        if operator in ('/', '%') and val2 == 0:
            raise DivisionByZeroError("Division or modulo by zero")

        # Perform computation
        if operator == '+':
            res = val1 + val2
        elif operator == '-':
            res = val1 - val2
        elif operator == '*':
            res = val1 * val2
        elif operator == '/':
            res = val1 / val2
        elif operator == '%':
            res = val1 % val2

        # Convert float to int if value is integral
        if isinstance(res, float) and res.is_integer():
            return int(res)
        return res


def main():
    """Main execution loop for processing interactive formulas or stream inputs."""
    evaluator = FormulaEvaluator()

    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        if cleaned_line.lower() == "quit":
            break

        try:
            result = evaluator.evaluate_line(cleaned_line)
            if result is not None:
                print(result)

        except FormulaError as e:
            # Print the custom exception class name
            print(e.__class__.__name__)


if __name__ == "__main__":
    main()
