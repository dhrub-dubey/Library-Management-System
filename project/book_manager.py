"""
book_manager.py - Add, view, search, update and delete books.

Module owner : Member 3
Concepts used: Classes, methods, lists, dictionaries, list comprehensions,
               string methods, conditionals, exception handling

BookManager works on the shared DataStore (see storage.py). Every method
validates its input first, then changes the data, then saves to disk.
"""

import validators as v
from exceptions import OperationNotAllowedError, ValidationError
from models import Book

SEARCH_FIELDS = ("title", "author", "isbn", "category", "all")


class BookManager:
    def __init__(self, store):
        self.store = store

    # ------------------------------------------------------------------ add
    def validate_new_isbn(self, value):
        """Validate the ISBN format AND make sure no other book uses it."""
        isbn = v.validate_isbn(value)
        for book in self.store.books.values():
            if book.isbn == isbn:
                raise ValidationError(
                    f"ISBN {isbn} already exists ({book.book_id}: {book.title}).")
        return isbn

    def add_book(self, title, author, isbn, category, year, copies):
        """Validate everything, create a Book, save it and return it."""
        title = v.validate_text(title, "Title", 100)
        author = v.validate_name(author, "Author")
        isbn = self.validate_new_isbn(isbn)
        category = v.validate_text(category, "Category", 30)
        year = v.validate_year(year)
        copies = v.validate_copies(copies)

        book = Book(self.store.next_book_id(), title, author, isbn,
                    category, year, copies)
        self.store.books[book.book_id] = book
        self.store.save()
        return book

    # ----------------------------------------------------------------- view
    def get_book(self, book_id):
        return self.store.get_book(book_id)

    def list_books(self):
        """All books, sorted by ID."""
        return sorted(self.store.books.values(), key=lambda b: b.book_id)

    # --------------------------------------------------------------- search
    def search_books(self, keyword, field="all"):
        """Case-insensitive 'contains' search. Returns a list of Books."""
        if field not in SEARCH_FIELDS:
            raise ValidationError("Unknown search field.")
        keyword = v.validate_text(keyword, "Search keyword", 50).lower()
        keyword_digits = keyword.replace("-", "")       # for ISBN searches

        results = []
        for book in self.list_books():
            matches = {
                "title": keyword in book.title.lower(),
                "author": keyword in book.author.lower(),
                "isbn": keyword_digits in book.isbn,
                "category": keyword in book.category.lower(),
            }
            if field == "all":
                found = any(matches.values())
            else:
                found = matches[field]
            if found:
                results.append(book)
        return results

    # --------------------------------------------------------------- update
    def update_book(self, book_id, title=None, author=None, category=None,
                    year=None, total_copies=None):
        """Change only the fields that are given (not None).

        All new values are validated BEFORE anything is changed, so a bad
        value cannot leave the book half-updated."""
        book = self.get_book(book_id)

        new_title = v.validate_text(title, "Title", 100) if title is not None else book.title
        new_author = v.validate_name(author, "Author") if author is not None else book.author
        new_category = v.validate_text(category, "Category", 30) if category is not None else book.category
        new_year = v.validate_year(year) if year is not None else book.year

        new_total = book.total_copies
        if total_copies is not None:
            new_total = v.validate_copies(total_copies)
            if new_total < book.issued_copies:
                raise OperationNotAllowedError(
                    f"Cannot reduce copies to {new_total}: "
                    f"{book.issued_copies} copies are currently issued.")

        issued = book.issued_copies
        book.title, book.author = new_title, new_author
        book.category, book.year = new_category, new_year
        book.total_copies = new_total
        book.available_copies = new_total - issued
        self.store.save()
        return book

    # --------------------------------------------------------------- delete
    def delete_book(self, book_id):
        """Remove a book. Not allowed while any copy is issued."""
        book = self.get_book(book_id)
        if book.issued_copies > 0:
            raise OperationNotAllowedError(
                f"Cannot delete '{book.title}': {book.issued_copies} copy(ies) "
                f"currently issued.")
        del self.store.books[book.book_id]
        self.store.save()
        return book
