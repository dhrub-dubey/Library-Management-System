"""
run_tests.py - Runs the test cases described in Chapter 5 of the report.

Module owner : Member 6 (all members contributed test cases for their modules)
Concepts used: Functions, lists, dictionaries, exception handling, file handling

Run with:   python run_tests.py

Every test uses a fresh temporary copy of a small data set, so your real data
in the data/ folder is never touched. Each test performs an action (valid or
invalid input), records what REALLY happened ("Actual Output"), and compares
it with what we expected. Results are printed and saved to docs/test_results.json.
"""

import json
import os
import shutil
import tempfile
from datetime import date

import validators as v
from auth import AuthManager
from book_manager import BookManager
from circulation import Circulation
from exceptions import LibraryError
from member_manager import MemberManager
from reports import build_summary, export_summary_report
from storage import DataStore

BASE_DAY = date(2026, 10, 1)


class World:
    """A small, fresh library used by one test."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="lms_test_")
        self.store = DataStore(self.dir)
        self.books = BookManager(self.store)
        self.members = MemberManager(self.store)
        self.circ = Circulation(self.store)
        self.auth = AuthManager(self.dir)
        for row in [("Python Crash Course", "Eric Matthes", "9781593279288", "Programming", 2019, 3),
                    ("Clean Code", "Robert Martin", "9780132350884", "Programming", 2008, 1),
                    ("Think Python", "Allen Downey", "9781491929568", "Programming", 2015, 2),
                    ("Wings of Fire", "A P J Abdul Kalam", "9788173711466", "Biography", 1999, 2)]:
            self.books.add_book(*row)
        for row in [("Aarav Sharma", "aarav@example.com", "9876543210"),
                    ("Priya Verma", "priya@example.com", "9123456780"),
                    ("Rohan Gupta", "rohan@example.com", "9988776655")]:
            self.members.add_member(*row)

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def attempt(function, *args, **kwargs):
    """Run function; return its result text, or 'Error: <message>' if the
    application raised one of its own errors."""
    try:
        return str(function(*args, **kwargs))
    except LibraryError as err:
        return f"Error: {err}"


# ----------------------------------------------------------------- test cases
# Each test: function(world) -> actual output text.
def tc_login_ok(w):
    user = w.auth.verify("admin", "admin123")
    return f"Login successful: {user['name']}" if user else "Login failed"

def tc_login_wrong_password(w):
    return "Login failed" if w.auth.verify("admin", "wrong") is None else "Login successful"

def tc_login_unknown_user(w):
    return "Login failed" if w.auth.verify("ghost", "admin123") is None else "Login successful"

def tc_add_book_valid(w):
    book = w.books.add_book("Learning Python", "Mark Lutz", "9781449355739", "Programming", 2013, 2)
    return f"Book added with ID {book.book_id}; copies {book.available_copies}/{book.total_copies}"

def tc_add_book_empty_title(w):
    return attempt(w.books.add_book, "   ", "Mark Lutz", "9781449355739", "Programming", 2013, 2)

def tc_add_book_bad_isbn(w):
    return attempt(w.books.add_book, "Learning Python", "Mark Lutz", "12345", "Programming", 2013, 2)

def tc_add_book_duplicate_isbn(w):
    return attempt(w.books.add_book, "Another Title", "Some Author", "978-1-59327-928-8", "Programming", 2020, 1)

def tc_add_book_text_copies(w):
    return attempt(w.books.add_book, "Learning Python", "Mark Lutz", "9781449355739", "Programming", 2013, "abc")

def tc_add_book_future_year(w):
    return attempt(w.books.add_book, "Learning Python", "Mark Lutz", "9781449355739", "Programming", 3000, 2)

def tc_search_title(w):
    found = w.books.search_books("python", "title")
    return f"{len(found)} result(s): " + ", ".join(b.title for b in found)

def tc_search_no_match(w):
    return f"{len(w.books.search_books('zzzz', 'author'))} result(s)"

def tc_update_copies(w):
    book = w.books.update_book("B001", total_copies=5)
    return f"Copies now {book.available_copies}/{book.total_copies}"

def tc_update_copies_below_issued(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)
    w.circ.issue_book("M002", "B001", BASE_DAY)
    return attempt(w.books.update_book, "B001", total_copies=1)

def tc_delete_book_free(w):
    book = w.books.delete_book("B004")
    return f"Deleted '{book.title}'; books left: {len(w.store.books)}"

def tc_delete_book_issued(w):
    w.circ.issue_book("M001", "B004", BASE_DAY)
    return attempt(w.books.delete_book, "B004")

def tc_unknown_book(w):
    return attempt(w.books.get_book, "B999")

def tc_add_member_valid(w):
    member = w.members.add_member("Sneha Iyer", "sneha@example.com", "8899001122")
    return f"Member registered with ID {member.member_id}"

def tc_add_member_bad_email(w):
    return attempt(w.members.add_member, "Sneha Iyer", "sneha.example.com", "8899001122")

def tc_add_member_bad_phone(w):
    return attempt(w.members.add_member, "Sneha Iyer", "sneha@example.com", "12345")

def tc_add_member_duplicate_email(w):
    return attempt(w.members.add_member, "Another Person", "AARAV@example.com", "8899001122")

def tc_add_member_digit_name(w):
    return attempt(w.members.add_member, "R0han", "r0han@example.com", "8899001122")

def tc_update_member_phone(w):
    member = w.members.update_member("M002", phone="7012345678")
    return f"Phone updated to {member.phone}"

def tc_delete_member_with_loan(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)
    return attempt(w.members.delete_member, "M001")

def tc_delete_member_free(w):
    member = w.members.delete_member("M003")
    return f"Deleted {member.name}; members left: {len(w.store.members)}"

def tc_issue_valid(w):
    txn = w.circ.issue_book("M001", "B001", BASE_DAY)
    book = w.store.books["B001"]
    return f"Issued {txn.txn_id}; due {txn.due_date}; copies left {book.available_copies}"

def tc_issue_no_copies(w):
    w.circ.issue_book("M001", "B002", BASE_DAY)         # Clean Code has only 1 copy
    return attempt(w.circ.issue_book, "M002", "B002", BASE_DAY)

def tc_issue_limit(w):
    for book_id in ("B001", "B002", "B003"):
        w.circ.issue_book("M001", book_id, BASE_DAY)
    return attempt(w.circ.issue_book, "M001", "B004", BASE_DAY)

def tc_issue_same_twice(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)
    return attempt(w.circ.issue_book, "M001", "B001", BASE_DAY)

def tc_issue_unknown_member(w):
    return attempt(w.circ.issue_book, "M999", "B001", BASE_DAY)

def tc_return_on_time(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)
    txn = w.circ.return_book("M001", "B001", date(2026, 10, 10))
    return f"Fine Rs {txn.fine}; copies available {w.store.books['B001'].available_copies}/3"

def tc_return_late(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)         # due 15 Oct
    txn = w.circ.return_book("M001", "B001", date(2026, 10, 20))
    return f"Returned {txn.days_overdue(txn.return_date)} days late; Fine Rs {txn.fine}"

def tc_return_not_issued(w):
    return attempt(w.circ.return_book, "M002", "B001", BASE_DAY)

def tc_return_before_issue(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)
    return attempt(w.circ.return_book, "M001", "B001", date(2026, 9, 1))

def tc_overdue_list(w):
    w.circ.issue_book("M001", "B001", date(2026, 9, 1))
    w.circ.issue_book("M002", "B003", date(2026, 10, 1))
    late = w.circ.overdue_loans(date(2026, 10, 4))
    return f"{len(late)} overdue loan(s): " + ", ".join(t.txn_id for t in late)

def tc_summary(w):
    w.circ.issue_book("M001", "B001", BASE_DAY)
    s = build_summary(w.store, BASE_DAY)
    return (f"Titles {s['total_titles']}, copies {s['total_copies']}, "
            f"available {s['available_copies']}, issued {s['issued_copies']}, members {s['total_members']}")

def tc_export_report(w):
    path = export_summary_report(w.store, os.path.join(w.dir, "reports"), BASE_DAY)
    size = os.path.getsize(path)
    return f"File created: {os.path.basename(path)} ({'non-empty' if size > 0 else 'empty'})"

def tc_persistence(w):
    w.books.add_book("Learning Python", "Mark Lutz", "9781449355739", "Programming", 2013, 2)
    w.circ.issue_book("M001", "B001", BASE_DAY)
    fresh = DataStore(w.dir)                            # re-read the files from disk
    return (f"After reload: {len(fresh.books)} books, {len(fresh.members)} members, "
            f"{len(fresh.transactions)} transaction(s)")

def tc_corrupted_file(w):
    with open(os.path.join(w.dir, "books.json"), "w", encoding="utf-8") as file:
        file.write("{ this is not valid json")
    return attempt(DataStore, w.dir)

def tc_missing_files(w):
    empty_dir = os.path.join(w.dir, "empty_library")
    store = DataStore(empty_dir)
    AuthManager(empty_dir)
    return (f"Started with {len(store.books)} books, {len(store.members)} members; "
            f"default login created: {os.path.exists(os.path.join(empty_dir, 'users.json'))}")

def tc_backup(w):
    folder = w.store.backup()
    return f"Backup created with files: {sorted(os.listdir(folder))}"

def tc_invalid_menu_choice(w):
    return attempt(v.validate_choice, "9", ["0", "1", "2"])

def tc_id_normalise(w):
    return f"'b1' becomes '{v.validate_book_id('b1')}'"


# (ID, module, input/action, expected output, text that must appear in actual, function)
TEST_CASES = [
    ("TC01", "Login", "Login with username admin, password admin123",
     "Login successful", "Login successful", tc_login_ok),
    ("TC02", "Login", "Login with admin and a wrong password",
     "Login rejected", "Login failed", tc_login_wrong_password),
    ("TC03", "Login", "Login with a username that does not exist",
     "Login rejected", "Login failed", tc_login_unknown_user),
    ("TC04", "Books", "Add a book with all valid details",
     "Book added with a new ID (B005)", "Book added with ID B005", tc_add_book_valid),
    ("TC05", "Books", "Add a book with a blank title",
     "Error: Title cannot be empty", "Title cannot be empty", tc_add_book_empty_title),
    ("TC06", "Books", "Add a book with ISBN '12345'",
     "Error: ISBN must be 10 or 13 digits", "ISBN must be 10 or 13 digits", tc_add_book_bad_isbn),
    ("TC07", "Books", "Add a book using an ISBN that already exists",
     "Error: ISBN already exists", "already exists", tc_add_book_duplicate_isbn),
    ("TC08", "Books", "Enter 'abc' as number of copies",
     "Error: copies must be a whole number", "must be a whole number", tc_add_book_text_copies),
    ("TC09", "Books", "Enter 3000 as publication year",
     "Error: year must be in the allowed range", "must be between", tc_add_book_future_year),
    ("TC10", "Books", "Search books by title with keyword 'python'",
     "Books whose title contains 'python' are listed", "2 result(s)", tc_search_title),
    ("TC11", "Books", "Search by author with keyword 'zzzz'",
     "0 results", "0 result(s)", tc_search_no_match),
    ("TC12", "Books", "Update total copies of B001 from 3 to 5",
     "Copies become 5/5", "5/5", tc_update_copies),
    ("TC13", "Books", "Reduce copies of B001 to 1 while 2 copies are issued",
     "Error: cannot reduce below issued copies", "Cannot reduce copies", tc_update_copies_below_issued),
    ("TC14", "Books", "Delete book B004 (no copies issued)",
     "Book deleted", "Deleted 'Wings of Fire'", tc_delete_book_free),
    ("TC15", "Books", "Delete book B004 while a copy is issued",
     "Error: cannot delete issued book", "Cannot delete", tc_delete_book_issued),
    ("TC16", "Books", "View book with ID B999 (does not exist)",
     "Error: no book found", "No book found", tc_unknown_book),
    ("TC17", "Members", "Register a member with valid details",
     "Member registered with ID M004", "M004", tc_add_member_valid),
    ("TC18", "Members", "Register with e-mail 'sneha.example.com' (no @)",
     "Error: invalid e-mail", "valid e-mail", tc_add_member_bad_email),
    ("TC19", "Members", "Register with phone '12345'",
     "Error: invalid phone", "10-digit", tc_add_member_bad_phone),
    ("TC20", "Members", "Register with an e-mail already in use",
     "Error: e-mail already registered", "already registered", tc_add_member_duplicate_email),
    ("TC21", "Members", "Register with name 'R0han' (contains a digit)",
     "Error: name must contain letters only", "only letters", tc_add_member_digit_name),
    ("TC22", "Members", "Update phone of M002 to 7012345678",
     "Phone updated", "7012345678", tc_update_member_phone),
    ("TC23", "Members", "Delete member M001 who has an issued book",
     "Error: cannot delete member", "Cannot delete", tc_delete_member_with_loan),
    ("TC24", "Members", "Delete member M003 with no issued books",
     "Member deleted", "Deleted Rohan Gupta", tc_delete_member_free),
    ("TC25", "Issue/Return", "Issue B001 to M001",
     "Book issued, due date = issue date + 14 days, copies reduce by 1",
     "due 2026-10-15; copies left 2", tc_issue_valid),
    ("TC26", "Issue/Return", "Issue B002 (only 1 copy, already issued) to another member",
     "Error: no copies available", "No copies", tc_issue_no_copies),
    ("TC27", "Issue/Return", "Issue a 4th book to a member who already holds 3",
     "Error: limit reached", "limit reached", tc_issue_limit),
    ("TC28", "Issue/Return", "Issue the same book twice to the same member",
     "Error: member already has a copy", "already has a copy", tc_issue_same_twice),
    ("TC29", "Issue/Return", "Issue a book to member M999 (does not exist)",
     "Error: no member found", "No member found", tc_issue_unknown_member),
    ("TC30", "Issue/Return", "Return a book before the due date",
     "Fine Rs 0, copy becomes available again", "Fine Rs 0; copies available 3/3", tc_return_on_time),
    ("TC31", "Issue/Return", "Return a book 5 days after the due date",
     "5 days late, Fine Rs 10", "Fine Rs 10", tc_return_late),
    ("TC32", "Issue/Return", "Return a book the member never borrowed",
     "Error: member has not borrowed this book", "has not borrowed", tc_return_not_issued),
    ("TC33", "Issue/Return", "Return with a date earlier than the issue date",
     "Error: return date before issue date", "before the issue date", tc_return_before_issue),
    ("TC34", "Issue/Return", "View overdue list (one overdue, one on time)",
     "Only the overdue loan (T0001) is listed", "1 overdue loan(s): T0001", tc_overdue_list),
    ("TC35", "Reports", "Generate summary report after issuing one book",
     "Titles 4, copies 8, available 7, issued 1, members 3",
     "Titles 4, copies 8, available 7, issued 1, members 3", tc_summary),
    ("TC36", "Reports", "Export the summary report to a file",
     "A non-empty .txt report file is created", "non-empty", tc_export_report),
    ("TC37", "Storage", "Add data, then reload the data files from disk",
     "Data is still present (5 books, 3 members, 1 transaction)",
     "5 books, 3 members, 1 transaction(s)", tc_persistence),
    ("TC38", "Storage", "Start the program with a corrupted books.json",
     "Error: data file is corrupted (program does not crash)", "corrupted", tc_corrupted_file),
    ("TC39", "Storage", "Start the program with no data files at all",
     "Starts with empty data and creates the default login", "0 books, 0 members; default login created: True",
     tc_missing_files),
    ("TC40", "Storage", "Create a backup of the data files",
     "Backup folder with the three data files", "books.json", tc_backup),
    ("TC41", "Validation", "Type menu option '9' when only 0-2 are valid",
     "Error: invalid choice", "Invalid choice", tc_invalid_menu_choice),
    ("TC42", "Validation", "Type book ID 'b1' (lower case, no zeros)",
     "Accepted and normalised to B001", "B001", tc_id_normalise),
]


def run_all():
    results = []
    for tc_id, module, action, expected, must_contain, function in TEST_CASES:
        world = World()
        try:
            actual = function(world)
        except Exception as err:                    # an unexpected crash = failed test
            actual = f"CRASH: {type(err).__name__}: {err}"
        finally:
            world.cleanup()
        status = "PASS" if must_contain in actual else "FAIL"
        results.append({"id": tc_id, "module": module, "action": action,
                        "expected": expected, "actual": actual, "status": status})
    return results


def main():
    results = run_all()
    for r in results:
        print(f"{r['id']} [{r['status']}] {r['action']}\n        -> {r['actual']}")
    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n{passed} of {len(results)} test cases passed.")

    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "test_results.json"), "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
