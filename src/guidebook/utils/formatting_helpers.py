"""
Formatting helper functions for guidebook generation.

This module provides utility functions for formatting text, dates,
currencies, and other data in guidebook outputs.
"""

import html
import re
from datetime import datetime
from typing import Optional


def format_currency(
    amount: float,
    currency: str = "VND",
    locale: str = "vi",
) -> str:
    """
    Format a currency amount for display.

    Args:
        amount: The amount to format.
        currency: The currency code (default: VND).
        locale: The locale for formatting (default: vi).

    Returns:
        Formatted currency string.

    Examples:
        >>> format_currency(50000000)
        '50,000,000 VND'
        >>> format_currency(1500.50, currency="USD", locale="en")
        '$1,500.50'
    """
    if currency == "USD":
        if locale == "en":
            return f"${amount:,.2f}"
        return f"{amount:,.2f} USD"
    elif currency == "VND":
        # VND typically doesn't use decimal places
        return f"{int(amount):,} VND"
    else:
        return f"{amount:,.2f} {currency}"


def format_date(
    date_str: Optional[str],
    input_format: str = "%Y-%m-%d",
    output_format: str = "%d/%m/%Y",
    locale: str = "vi",
) -> str:
    """
    Format a date string for display.

    Args:
        date_str: The date string to format.
        input_format: The format of the input date string.
        output_format: The desired output format.
        locale: The locale for formatting.

    Returns:
        Formatted date string, or empty string if input is None/invalid.

    Examples:
        >>> format_date("2024-06-01")
        '01/06/2024'
    """
    if not date_str:
        return ""

    try:
        dt = datetime.strptime(date_str, input_format)
        return dt.strftime(output_format)
    except (ValueError, TypeError):
        return str(date_str) if date_str else ""


def format_time_range(start_time: str, end_time: Optional[str] = None) -> str:
    """
    Format a time range for display.

    Args:
        start_time: The start time (e.g., "08:00").
        end_time: The end time (optional).

    Returns:
        Formatted time range string.

    Examples:
        >>> format_time_range("08:00", "10:00")
        '08:00 - 10:00'
        >>> format_time_range("08:00")
        '08:00'
    """
    if end_time:
        return f"{start_time} - {end_time}"
    return start_time


def sanitize_text(text: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize text for safe output in HTML/PDF.

    Args:
        text: The text to sanitize.
        max_length: Optional maximum length to truncate to.

    Returns:
        Sanitized text string.
    """
    if not text:
        return ""

    # Escape HTML entities
    sanitized = html.escape(str(text))

    # Remove any control characters except newlines and tabs
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", sanitized)

    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[: max_length - 3] + "..."

    return sanitized


def format_list_items(items: list, bullet: str = "•") -> str:
    """
    Format a list of items with bullets.

    Args:
        items: List of items to format.
        bullet: The bullet character to use.

    Returns:
        Formatted list string with newlines.
    """
    if not items:
        return ""

    return "\n".join(f"{bullet} {item}" for item in items if item)


def calculate_total_days(start_date: str, end_date: str) -> int:
    """
    Calculate the number of days between two dates.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Number of days between dates, or 0 if invalid.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days + 1
    except (ValueError, TypeError):
        return 0


def get_activity_icon(activity_type: str) -> str:
    """
    Get an emoji icon for an activity type.

    Args:
        activity_type: The type of activity.

    Returns:
        Emoji string for the activity type.
    """
    icons = {
        "tham quan": "🏛️",
        "sightseeing": "🏛️",
        "ăn uống": "🍽️",
        "food": "🍽️",
        "dining": "🍽️",
        "mua sắm": "🛍️",
        "shopping": "🛍️",
        "di chuyển": "🚗",
        "transport": "🚗",
        "transportation": "🚗",
        "giải trí": "🎭",
        "entertainment": "🎭",
        "nghỉ ngơi": "😴",
        "rest": "😴",
        "check-in": "🏨",
        "check-out": "🏨",
        "flight": "✈️",
        "bay": "✈️",
    }

    activity_lower = activity_type.lower()
    for key, icon in icons.items():
        if key in activity_lower:
            return icon
    return "📌"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with suffix.

    Args:
        text: Text to truncate.
        max_length: Maximum length including suffix.
        suffix: Suffix to add when truncating.

    Returns:
        Truncated text.
    """
    if not text or len(text) <= max_length:
        return text or ""

    return text[: max_length - len(suffix)] + suffix
