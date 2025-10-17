"""Unit tests for the example module."""

from src.naviagent.example import Calculator, calculate_sum, greet


class TestGreet:
    """Test cases for the greet function."""

    def test_greet_simple(self):
        """Test greeting with a simple name."""
        result = greet("World")
        assert result == "Hello, World!"

    def test_greet_empty_string(self):
        """Test greeting with an empty string."""
        result = greet("")
        assert result == "Hello, !"

    def test_greet_special_characters(self):
        """Test greeting with special characters."""
        result = greet("Alice & Bob")
        assert result == "Hello, Alice & Bob!"


class TestCalculateSum:
    """Test cases for the calculate_sum function."""

    def test_calculate_sum_positive(self):
        """Test sum of two positive integers."""
        result = calculate_sum(2, 3)
        assert result == 5

    def test_calculate_sum_negative(self):
        """Test sum with negative integers."""
        result = calculate_sum(-5, 3)
        assert result == -2

    def test_calculate_sum_zero(self):
        """Test sum with zero."""
        result = calculate_sum(0, 0)
        assert result == 0


class TestCalculator:
    """Test cases for the Calculator class."""

    def test_calculator_initialization(self):
        """Test calculator initializes with result 0."""
        calc = Calculator()
        assert calc.result == 0

    def test_calculator_add(self):
        """Test adding values to calculator."""
        calc = Calculator()
        result = calc.add(5)
        assert result == 5
        assert calc.result == 5

    def test_calculator_subtract(self):
        """Test subtracting values from calculator."""
        calc = Calculator()
        calc.add(10)
        result = calc.subtract(3)
        assert result == 7
        assert calc.result == 7

    def test_calculator_reset(self):
        """Test resetting calculator."""
        calc = Calculator()
        calc.add(10)
        calc.reset()
        assert calc.result == 0

    def test_calculator_chaining(self):
        """Test chaining calculator operations."""
        calc = Calculator()
        calc.add(5)
        calc.add(3)
        calc.subtract(2)
        assert calc.result == 6
