"""
storage.py - File handling: loading, saving and backing up the library data.

Module owner : Member 2
Concepts used: File handling (open/read/write), JSON, os & shutil modules,
               dictionaries, lists, classes, exception handling

All data lives in three JSON files inside the data/ folder:
    books.json         - list of books
    members.json       - list of members
    transactions.json  - list of issue/return records

DataStore reads them into memory when the program starts, keeps them in
dictionaries/lists while it runs, and writes them back after every change.
"""

import json
import os
import shutil
from datetime import datetime

from exceptions import NotFoundError, StorageError
from models import Book, Member, Transaction
from validators import validate_book_id, validate_member_id

DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def read_json(path, default):
    """Read a JSON file. If it does not exist yet, return `default`."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        raise StorageError(f"Data file '{os.path.basename(path)}' is corrupted "
                           f"(not valid JSON).")
    except OSError as error:
        raise StorageError(f"Cannot read '{os.path.basename(path)}': {error}")


def write_json(path, data):
    """Write data to a JSON file safely.

    We first write to a temporary file and then replace the real file, so a
    crash in the middle of writing cannot leave a half-written data file."""
    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        os.replace(temp_path, path)
    except OSError as error:
        raise StorageError(f"Cannot save '{os.path.basename(path)}': {error}")


class DataStore:
    """Holds all library data in memory and keeps it in sync with the files."""

    def __init__(self, data_dir=DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.books_file = os.path.join(data_dir, "books.json")
        self.members_file = os.path.join(data_dir, "members.json")
        self.transactions_file = os.path.join(data_dir, "transactions.json")

        self.books = {}             # book_id   -> Book
        self.members = {}           # member_id -> Member
        self.transactions = []      # list of Transaction
        self.load()

    # ----------------------------------------------------------- load / save
    def load(self):
        """Read the three data files into memory."""
        try:
            self.books = {item["book_id"]: Book.from_dict(item)
                          for item in read_json(self.books_file, [])}
            self.members = {item["member_id"]: Member.from_dict(item)
                            for item in read_json(self.members_file, [])}
            self.transactions = [Transaction.from_dict(item)
                                 for item in read_json(self.transactions_file, [])]
        except (KeyError, TypeError, ValueError):
            raise StorageError("A data file has a missing field or wrong format.")

    def save(self):
        """Write everything in memory back to the files."""
        write_json(self.books_file, [b.to_dict() for b in self.books.values()])
        write_json(self.members_file, [m.to_dict() for m in self.members.values()])
        write_json(self.transactions_file, [t.to_dict() for t in self.transactions])

    def backup(self):
        """Copy the data files into data/backup/<timestamp>/ and return that path."""
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.data_dir, "backup", stamp)
        try:
            os.makedirs(folder, exist_ok=True)
            for path in (self.books_file, self.members_file, self.transactions_file):
                if os.path.exists(path):
                    shutil.copy2(path, folder)
        except OSError as error:
            raise StorageError(f"Backup failed: {error}")
        return folder

    # -------------------------------------------------------------- lookups
    def get_book(self, book_id):
        """Return the Book with this ID or raise NotFoundError."""
        book_id = validate_book_id(book_id)
        if book_id not in self.books:
            raise NotFoundError(f"No book found with ID {book_id}.")
        return self.books[book_id]

    def get_member(self, member_id):
        """Return the Member with this ID or raise NotFoundError."""
        member_id = validate_member_id(member_id)
        if member_id not in self.members:
            raise NotFoundError(f"No member found with ID {member_id}.")
        return self.members[member_id]

    def open_loans_of_member(self, member_id):
        """Loans of this member that have not been returned yet."""
        return [t for t in self.transactions
                if t.member_id == member_id and t.is_open]

    def open_loans_of_book(self, book_id):
        """Loans of this book that have not been returned yet."""
        return [t for t in self.transactions
                if t.book_id == book_id and t.is_open]

    # ------------------------------------------------------- ID generation
    @staticmethod
    def _next_id(prefix, existing_ids, width):
        """Next free ID such as B013: take the biggest number so far and add 1."""
        numbers = [int(item[len(prefix):]) for item in existing_ids]
        next_number = max(numbers) + 1 if numbers else 1
        return f"{prefix}{next_number:0{width}d}"

    def next_book_id(self):
        return self._next_id("B", self.books.keys(), 3)

    def next_member_id(self):
        return self._next_id("M", self.members.keys(), 3)

    def next_transaction_id(self):
        return self._next_id("T", [t.txn_id for t in self.transactions], 4)
