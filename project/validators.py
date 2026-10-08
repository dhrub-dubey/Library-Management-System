"""
validators.py - Input validation functions.

Module owner : Member 3
Concepts used: Functions, strings, conditionals, loops, regular expressions,
               exception handling (try/except, raise)

Every function takes the raw text typed by the user, checks it, and either
returns the CLEANED value or raises ValidationError with a helpful message.
The menu code in main.py catches that error and asks the user again.
"""

import re
from datetime import date

from exceptions import ValidationError


def validate_text(value, field="Value", max_len=100):
    """Non-empty text. Extra spaces are removed."""
    cleaned = " ".join(str(value).split())      # trims + collapses spaces
    if cleaned == "":
        raise ValidationError(f"{field} cannot be empty.")
    if len(cleaned) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} characters.")
    return cleaned


def validate_name(value, field="Name"):
    """A person's name: letters, spaces, dot, hyphen and apostrophe only."""
    cleaned = validate_text(value, field, 50)
    if len(cleaned) < 2:
        raise ValidationError(f"{field} must have at least 2 characters.")
    for character in cleaned:
        if not (character.isalpha() or character in " .'-"):
            raise ValidationError(
                f"{field} can contain only letters, spaces, '.', '-' and apostrophes.")
    return cleaned


def validate_int(value, field="Number", min_value=None, max_value=None):
    """Whole number, optionally inside a range."""
    try:
        number = int(str(value).strip())
    except ValueError:
        raise ValidationError(f"{field} must be a whole number.")
    if min_value is not None and number < min_value:
        raise ValidationError(f"{field} must be between {min_value} and {max_value}.")
    if max_value is not None and number > max_value:
        raise ValidationError(f"{field} must be between {min_value} and {max_value}.")
    return number


def validate_year(value):
    """Publication year between 1000 and the current year."""
    return validate_int(value, "Publication year", 1000, date.today().year)


def validate_copies(value):
    """Number of copies: 1 to 100."""
    return validate_int(value, "Number of copies", 1, 100)


def validate_isbn(value):
    """ISBN must be 10 or 13 digits. Hyphens and spaces are allowed
    while typing but are removed before storing."""
    digits = str(value).replace("-", "").replace(" ", "")
    if not digits.isdigit() or len(digits) not in (10, 13):
        raise ValidationError("ISBN must be 10 or 13 digits (hyphens allowed).")
    return digits


def validate_email(value):
    """Basic e-mail format check: name@domain.ext"""
    cleaned = str(value).strip().lower()
    if not re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", cleaned):
        raise ValidationError("Enter a valid e-mail address (e.g. name@example.com).")
    return cleaned


def validate_phone(value):
    """Indian mobile number: 10 digits starting with 6, 7, 8 or 9."""
    digits = str(value).replace(" ", "").replace("-", "")
    if not re.fullmatch(r"[6-9]\d{9}", digits):
        raise ValidationError("Phone must be a 10-digit mobile number starting with 6-9.")
    return digits


def validate_id(value, prefix, field="ID"):
    """Normalise IDs such as 'b1' -> 'B001' (prefix 'B') or 'm12' -> 'M012'.
    Transaction IDs ('T') use 4 digits."""
    cleaned = str(value).strip().upper()
    match = re.fullmatch(prefix + r"(\d+)", cleaned)
    if not match:
        raise ValidationError(f"{field} must look like {prefix}001.")
    width = 4 if prefix == "T" else 3
    return f"{prefix}{int(match.group(1)):0{width}d}"


def validate_book_id(value):
    return validate_id(value, "B", "Book ID")


def validate_member_id(value):
    return validate_id(value, "M", "Member ID")


def validate_choice(value, valid_options):
    """Menu choice must be one of the given options (list/tuple/set of str)."""
    cleaned = str(value).strip()
    if cleaned not in valid_options:
        raise ValidationError("Invalid choice. Please pick one of the listed options.")
    return cleaned


def validate_yes_no(value):
    """Returns True for yes, False for no."""
    cleaned = str(value).strip().lower()
    if cleaned in ("y", "yes"):
        return True
    if cleaned in ("n", "no"):
        return False
    raise ValidationError("Please type 'y' for yes or 'n' for no.")
