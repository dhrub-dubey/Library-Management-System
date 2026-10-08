"""
auth.py - Librarian login (authentication).

Module owner : Member 2
Concepts used: Functions, classes, dictionaries, hashing (hashlib), file handling

Passwords are never stored as plain text. We store a random "salt" and the
SHA-256 hash of (salt + password). To check a login we hash the typed password
with the stored salt and compare the two hashes.

Default account created on first run:  username = admin   password = admin123
"""

import hashlib
import os
import secrets

from storage import read_json, write_json

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"


def hash_password(password, salt):
    """Return the SHA-256 hex digest of salt + password."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


class AuthManager:
    """Reads users.json and checks usernames/passwords."""

    def __init__(self, data_dir):
        self.users_file = os.path.join(data_dir, "users.json")
        self.users = read_json(self.users_file, {})
        if not self.users:                      # first run: create default admin
            self.add_user(DEFAULT_USERNAME, DEFAULT_PASSWORD, "Head Librarian")

    def add_user(self, username, password, full_name):
        salt = secrets.token_hex(8)
        self.users[username] = {
            "name": full_name,
            "salt": salt,
            "password_hash": hash_password(password, salt),
        }
        write_json(self.users_file, self.users)

    def verify(self, username, password):
        """Return the user's record if the login is correct, otherwise None."""
        user = self.users.get(username)
        if user is None:
            return None
        if hash_password(password, user["salt"]) == user["password_hash"]:
            return user
        return None
