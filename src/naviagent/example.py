"""Example module demonstrating Google style Python conventions."""


def greet(name: str) -> str:
    """Greet a person by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting message string.

    Examples:
        >>> greet("World")
        'Hello, World!'
    """
    return f"Hello, {name}!"


def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The sum of a and b.

    Examples:
        >>> calculate_sum(2, 3)
        5
    """
    return a + b


class Calculator:
    """A simple calculator class.

    This class demonstrates Google Python style conventions with proper
    docstrings and type hints.

    Attributes:
        result: The current result of calculations.
    """

    def __init__(self) -> None:
        """Initialize the calculator with result set to 0."""
        self.result: int = 0

    def add(self, value: int) -> int:
        """Add a value to the current result.

        Args:
            value: The value to add.

        Returns:
            The new result after addition.
        """
        self.result += value
        return self.result

    def subtract(self, value: int) -> int:
        """Subtract a value from the current result.

        Args:
            value: The value to subtract.

        Returns:
            The new result after subtraction.
        """
        self.result -= value
        return self.result

    def reset(self) -> None:
        """Reset the calculator result to 0."""
        self.result = 0
