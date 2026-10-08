"""
circulation.py - Issuing books, returning books, due dates and fines.

Module owner : Member 5
Concepts used: Classes, methods, constants, date arithmetic (timedelta),
               conditionals, loops, lists, exception handling

Library rules (constants below):
    * A member can hold at most 3 books at a time.
    * A book is lent for 14 days.
    * Late return costs Rs 2 per day after the due date.
"""

from datetime import date, timedelta

from exceptions import (NotFoundError, OperationNotAllowedError,
                        ValidationError)
from models import Transaction

MAX_BOOKS_PER_MEMBER = 3
LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 2            # rupees


def today():
    """Today's date. Kept in a function so it is easy to replace when testing."""
    return date.today()


def calculate_fine(due_date, return_date):
    """Fine in rupees = days late x FINE_PER_DAY (never negative)."""
    days_late = (return_date - due_date).days
    return max(0, days_late) * FINE_PER_DAY


class Circulation:
    def __init__(self, store):
        self.store = store

    # ---------------------------------------------------------------- issue
    def issue_book(self, member_id, book_id, issue_date=None):
        """Lend one copy of a book to a member. Returns the new Transaction."""
        member = self.store.get_member(member_id)
        book = self.store.get_book(book_id)
        issue_date = issue_date or today()

        if not book.is_available:
            raise OperationNotAllowedError(
                f"No copies of '{book.title}' are available right now.")

        current_loans = self.store.open_loans_of_member(member.member_id)
        if len(current_loans) >= MAX_BOOKS_PER_MEMBER:
            raise OperationNotAllowedError(
                f"{member.name} already has {MAX_BOOKS_PER_MEMBER} books issued "
                f"(limit reached).")
        for loan in current_loans:
            if loan.book_id == book.book_id:
                raise OperationNotAllowedError(
                    f"{member.name} already has a copy of '{book.title}'.")

        due_date = issue_date + timedelta(days=LOAN_PERIOD_DAYS)
        txn = Transaction(self.store.next_transaction_id(), book.book_id,
                          member.member_id, issue_date, due_date)
        self.store.transactions.append(txn)
        book.available_copies -= 1
        self.store.save()
        return txn

    # --------------------------------------------------------------- return
    def return_book(self, member_id, book_id, return_date=None):
        """Take a book back. Calculates the fine. Returns the closed Transaction."""
        member = self.store.get_member(member_id)
        book = self.store.get_book(book_id)
        return_date = return_date or today()

        # Find the open loan of this book for this member.
        loan = None
        for txn in self.store.open_loans_of_member(member.member_id):
            if txn.book_id == book.book_id:
                loan = txn
                break
        if loan is None:
            raise NotFoundError(
                f"{member.name} has not borrowed '{book.title}' (or already returned it).")

        if return_date < loan.issue_date:
            raise ValidationError("Return date cannot be before the issue date.")

        loan.return_date = return_date
        loan.fine = calculate_fine(loan.due_date, return_date)
        book.available_copies += 1
        self.store.save()
        return loan

    # -------------------------------------------------------------- queries
    def open_loans(self):
        """All loans that are still out, oldest first."""
        return [t for t in self.store.transactions if t.is_open]

    def overdue_loans(self, on_date=None):
        """Open loans whose due date is before `on_date` (default: today)."""
        on_date = on_date or today()
        return [t for t in self.open_loans() if t.due_date < on_date]

    def fine_so_far(self, loan, on_date=None):
        """Fine a still-open loan would cost if returned on `on_date`."""
        on_date = on_date or today()
        return calculate_fine(loan.due_date, on_date)
