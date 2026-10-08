"""
models.py - Data classes (Object-Oriented Programming) for the system.

Module owner : Member 1
Concepts used: Classes, objects, constructors, methods, @classmethod,
               @property, dictionaries, date handling

Three classes are defined:
    Book        - one title in the library (with number of copies)
    Member      - one registered library member
    Transaction - one issue/return record (a "loan")

Every class can convert itself to a dictionary (to_dict) so it can be saved
as JSON, and can be rebuilt from a dictionary (from_dict) when loading.
"""

from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


def parse_date(text):
    """Convert a 'YYYY-MM-DD' string into a date object."""
    return datetime.strptime(text, DATE_FORMAT).date()


def format_date(day):
    """Convert a date object into a 'YYYY-MM-DD' string."""
    return day.strftime(DATE_FORMAT)


class Book:
    """A book title and how many copies of it the library owns."""

    def __init__(self, book_id, title, author, isbn, category, year,
                 total_copies, available_copies=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.year = year
        self.total_copies = total_copies
        # When a book is first added, every copy is available.
        if available_copies is None:
            available_copies = total_copies
        self.available_copies = available_copies

    @property
    def is_available(self):
        """True if at least one copy can be issued."""
        return self.available_copies > 0

    @property
    def issued_copies(self):
        """Number of copies currently lent out."""
        return self.total_copies - self.available_copies

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "year": self.year,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["book_id"], data["title"], data["author"],
                   data["isbn"], data["category"], data["year"],
                   data["total_copies"], data["available_copies"])

    def __str__(self):
        return (f"{self.book_id} | {self.title} by {self.author} "
                f"({self.available_copies}/{self.total_copies} available)")


class Member:
    """A registered library member."""

    def __init__(self, member_id, name, email, phone, join_date):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.join_date = join_date          # a date object

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "join_date": format_date(self.join_date),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["member_id"], data["name"], data["email"],
                   data["phone"], parse_date(data["join_date"]))

    def __str__(self):
        return f"{self.member_id} | {self.name} ({self.email})"


class Transaction:
    """One loan record: a member borrowing one copy of a book."""

    def __init__(self, txn_id, book_id, member_id, issue_date, due_date,
                 return_date=None, fine=0):
        self.txn_id = txn_id
        self.book_id = book_id
        self.member_id = member_id
        self.issue_date = issue_date        # date
        self.due_date = due_date            # date
        self.return_date = return_date      # date, or None while still issued
        self.fine = fine                    # whole rupees

    @property
    def is_open(self):
        """True while the book has not been returned yet."""
        return self.return_date is None

    def days_overdue(self, today):
        """How many days past the due date (0 if not late).

        For an open loan we compare with `today`; for a returned loan we
        compare with the day it was actually returned."""
        end_day = today if self.is_open else self.return_date
        late_days = (end_day - self.due_date).days
        return max(0, late_days)

    def to_dict(self):
        return {
            "txn_id": self.txn_id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "issue_date": format_date(self.issue_date),
            "due_date": format_date(self.due_date),
            "return_date": format_date(self.return_date) if self.return_date else None,
            "fine": self.fine,
        }

    @classmethod
    def from_dict(cls, data):
        return_text = data["return_date"]
        return cls(data["txn_id"], data["book_id"], data["member_id"],
                   parse_date(data["issue_date"]), parse_date(data["due_date"]),
                   parse_date(return_text) if return_text else None,
                   data["fine"])
