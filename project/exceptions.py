"""
exceptions.py - Custom exception classes for the Library Management System.

Module owner : Member 1
Concepts used: Classes, inheritance, exception handling

Having our own exception classes lets every module report problems in a
consistent way, and lets main.py catch them with a single `except LibraryError`.
"""


class LibraryError(Exception):
    """Base class for every error raised by this application."""


class ValidationError(LibraryError):
    """Raised when user input is not valid (empty, wrong format, out of range)."""


class NotFoundError(LibraryError):
    """Raised when a book / member / record does not exist."""


class OperationNotAllowedError(LibraryError):
    """Raised when a request is valid but breaks a library rule
    (e.g. issuing a book with no copies left, deleting an issued book)."""


class StorageError(LibraryError):
    """Raised when a data file cannot be read or written."""


class OperationCancelled(LibraryError):
    """Raised when the user types 'cancel' while an operation is in progress."""
