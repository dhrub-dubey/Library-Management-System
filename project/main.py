"""
main.py - Entry point of the Library Management System (menus and user flow).

Module owner : Member 6
Concepts used: Functions, loops (while True), conditionals, dictionaries,
               exception handling (try/except), modules, f-strings

Run with:   python main.py

Flow:  Login -> Main menu -> (Books | Members | Issue/Return | Reports | Backup)
       -> Logout / Exit.  Type 'cancel' at any prompt to abort the operation.
"""

import getpass
import os

import display
import reports
import validators as v
from auth import AuthManager
from book_manager import BookManager
from circulation import (FINE_PER_DAY, LOAN_PERIOD_DAYS, MAX_BOOKS_PER_MEMBER,
                         Circulation, today)
from exceptions import (LibraryError, OperationCancelled, StorageError,
                        ValidationError)
from member_manager import MemberManager
from storage import DEFAULT_DATA_DIR, DataStore

MAX_LOGIN_ATTEMPTS = 3


# ------------------------------------------------------------ input helpers
def ask(prompt, validator, *args):
    """Keep asking until the validator accepts the answer.
    Typing 'cancel' aborts the whole operation."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            raise OperationCancelled()
        try:
            return validator(raw, *args)
        except ValidationError as err:
            display.error(str(err))


def ask_optional(prompt, validator, *args):
    """Like ask(), but pressing Enter returns None (meaning 'keep old value')."""
    while True:
        raw = input(prompt).strip()
        if raw.lower() == "cancel":
            raise OperationCancelled()
        if raw == "":
            return None
        try:
            return validator(raw, *args)
        except ValidationError as err:
            display.error(str(err))


def choose(options, prompt="Enter your choice: "):
    """Read a menu choice. Keeps asking until it is one of `options`."""
    while True:
        try:
            return v.validate_choice(input(prompt), options)
        except ValidationError as err:
            display.error(str(err))


def confirm(question):
    return ask(question + " (y/n): ", v.validate_yes_no)


def run_safely(action, *args):
    """Run one menu action; show friendly messages instead of crashing."""
    try:
        action(*args)
    except OperationCancelled:
        display.info("Operation cancelled.")
    except LibraryError as err:
        display.error(str(err))


# --------------------------------------------------------------------- login
def login(auth):
    display.section("Librarian Login")
    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        username = input("  Username: ").strip()
        password = getpass.getpass("  Password: ")
        user = auth.verify(username, password)
        if user is not None:
            display.success(f"Welcome, {user['name']}!")
            return user
        left = MAX_LOGIN_ATTEMPTS - attempt
        display.error(f"Invalid username or password. Attempts left: {left}")
    return None


# ------------------------------------------------------------- book actions
def add_book_action(books):
    display.section("Add New Book  (type 'cancel' to abort)")
    title = ask("  Title            : ", v.validate_text, "Title", 100)
    author = ask("  Author           : ", v.validate_name, "Author")
    isbn = ask("  ISBN (10/13 digits): ", books.validate_new_isbn)
    category = ask("  Category         : ", v.validate_text, "Category", 30)
    year = ask("  Publication year : ", v.validate_year)
    copies = ask("  Number of copies : ", v.validate_copies)
    book = books.add_book(title, author, isbn, category, year, copies)
    display.success(f"Book added with ID {book.book_id}: {book.title}")


def view_books_action(books):
    display.section("All Books")
    all_books = books.list_books()
    display.print_books(all_books)
    display.info(f"Total titles: {len(all_books)}")


def search_books_action(books):
    display.section("Search Books")
    print("  Search by:  1. Title   2. Author   3. ISBN   4. Category   5. Any field")
    field_map = {"1": "title", "2": "author", "3": "isbn",
                 "4": "category", "5": "all"}
    option = choose(list(field_map))
    keyword = ask("  Enter keyword: ", v.validate_text, "Search keyword", 50)
    results = books.search_books(keyword, field_map[option])
    display.print_books(results)
    display.info(f"{len(results)} result(s) found.")


def update_book_action(books):
    display.section("Update Book  (press Enter to keep the current value)")
    book = books.get_book(ask("  Book ID: ", v.validate_book_id))
    display.print_books([book])
    title = ask_optional("  New title            : ", v.validate_text, "Title", 100)
    author = ask_optional("  New author           : ", v.validate_name, "Author")
    category = ask_optional("  New category         : ", v.validate_text, "Category", 30)
    year = ask_optional("  New publication year : ", v.validate_year)
    copies = ask_optional("  New total copies     : ", v.validate_copies)
    books.update_book(book.book_id, title, author, category, year, copies)
    display.success("Book updated.")
    display.print_books([book])


def delete_book_action(books):
    display.section("Delete Book")
    book = books.get_book(ask("  Book ID: ", v.validate_book_id))
    display.print_books([book])
    if confirm("  Delete this book?"):
        books.delete_book(book.book_id)
        display.success("Book deleted.")
    else:
        display.info("Deletion cancelled.")


def book_menu(books):
    actions = {"1": add_book_action, "2": view_books_action,
               "3": search_books_action, "4": update_book_action,
               "5": delete_book_action}
    while True:
        display.section("BOOK MANAGEMENT")
        print("  1. Add book\n  2. View all books\n  3. Search books\n"
              "  4. Update book\n  5. Delete book\n  0. Back to main menu")
        choice = choose(["0"] + list(actions))
        if choice == "0":
            return
        run_safely(actions[choice], books)


# ----------------------------------------------------------- member actions
def add_member_action(members):
    display.section("Register New Member  (type 'cancel' to abort)")
    name = ask("  Full name : ", v.validate_name, "Name")
    email = ask("  E-mail    : ", members.validate_new_email)
    phone = ask("  Phone     : ", v.validate_phone)
    member = members.add_member(name, email, phone)
    display.success(f"Member registered with ID {member.member_id}: {member.name}")


def view_members_action(members):
    display.section("All Members")
    all_members = members.list_members()
    display.print_members(all_members)
    display.info(f"Total members: {len(all_members)}")


def search_members_action(members):
    display.section("Search Members")
    keyword = ask("  Name / ID / e-mail contains: ", v.validate_text,
                  "Search keyword", 50)
    results = members.search_members(keyword)
    display.print_members(results)
    display.info(f"{len(results)} result(s) found.")


def update_member_action(members):
    display.section("Update Member  (press Enter to keep the current value)")
    member = members.get_member(ask("  Member ID: ", v.validate_member_id))
    display.print_members([member])
    name = ask_optional("  New name   : ", v.validate_name, "Name")
    email = ask_optional("  New e-mail : ", members.validate_new_email,
                         member.member_id)
    phone = ask_optional("  New phone  : ", v.validate_phone)
    members.update_member(member.member_id, name, email, phone)
    display.success("Member updated.")
    display.print_members([member])


def delete_member_action(members):
    display.section("Delete Member")
    member = members.get_member(ask("  Member ID: ", v.validate_member_id))
    display.print_members([member])
    if confirm("  Delete this member?"):
        members.delete_member(member.member_id)
        display.success("Member deleted.")
    else:
        display.info("Deletion cancelled.")


def member_history_action(members, store):
    display.section("Member Borrowing History")
    member = members.get_member(ask("  Member ID: ", v.validate_member_id))
    display.info(f"History of {member.name}")
    display.print_loans(members.history_of(member.member_id), store, today())


def member_menu(members, store):
    while True:
        display.section("MEMBER MANAGEMENT")
        print("  1. Register member\n  2. View all members\n  3. Search members\n"
              "  4. Update member\n  5. Delete member\n  6. Borrowing history\n"
              "  0. Back to main menu")
        choice = choose(["0", "1", "2", "3", "4", "5", "6"])
        if choice == "0":
            return
        if choice == "6":
            run_safely(member_history_action, members, store)
        else:
            action = {"1": add_member_action, "2": view_members_action,
                      "3": search_members_action, "4": update_member_action,
                      "5": delete_member_action}[choice]
            run_safely(action, members)


# ----------------------------------------------------- issue / return actions
def issue_book_action(store, circulation):
    display.section(f"Issue Book  (max {MAX_BOOKS_PER_MEMBER} books, "
                    f"{LOAN_PERIOD_DAYS} days)")
    member = store.get_member(ask("  Member ID: ", v.validate_member_id))
    display.info(f"Member: {member.name}")
    book = store.get_book(ask("  Book ID  : ", v.validate_book_id))
    display.info(f"Book  : {book.title} ({book.available_copies} available)")
    txn = circulation.issue_book(member.member_id, book.book_id)
    display.success(f"Issued '{book.title}' to {member.name}. "
                    f"Transaction {txn.txn_id}.")
    display.info(f"Due date: {txn.due_date}")


def return_book_action(store, circulation):
    display.section("Return Book")
    member = store.get_member(ask("  Member ID: ", v.validate_member_id))
    loans = store.open_loans_of_member(member.member_id)
    if not loans:
        display.info(f"{member.name} has no books to return.")
        return
    display.info(f"Books currently held by {member.name}:")
    display.print_loans(loans, store, today())
    book = store.get_book(ask("  Book ID to return: ", v.validate_book_id))
    txn = circulation.return_book(member.member_id, book.book_id)
    display.success(f"'{book.title}' returned by {member.name}.")
    late = txn.days_overdue(txn.return_date)
    if late:
        display.info(f"Returned {late} day(s) late. Fine to collect: Rs {txn.fine} "
                     f"(Rs {FINE_PER_DAY}/day)")
    else:
        display.info("Returned on time. No fine.")


def view_issued_action(store, circulation):
    display.section("Currently Issued Books")
    loans = circulation.open_loans()
    display.print_loans(loans, store, today())
    display.info(f"{len(loans)} book(s) currently issued.")


def view_overdue_action(store, circulation):
    display.section("Overdue Books")
    loans = circulation.overdue_loans()
    display.print_loans(loans, store, today())
    display.info(f"{len(loans)} overdue loan(s) as of {today()}.")


def circulation_menu(store, circulation):
    actions = {"1": issue_book_action, "2": return_book_action,
               "3": view_issued_action, "4": view_overdue_action}
    while True:
        display.section("ISSUE / RETURN")
        print("  1. Issue a book\n  2. Return a book\n"
              "  3. View issued books\n  4. View overdue books\n"
              "  0. Back to main menu")
        choice = choose(["0"] + list(actions))
        if choice == "0":
            return
        run_safely(actions[choice], store, circulation)


# ----------------------------------------------------------------- reports
def report_menu(store):
    while True:
        display.section("REPORTS")
        print("  1. Library summary report\n  2. Most borrowed books\n"
              "  3. Export summary report to file\n  0. Back to main menu")
        choice = choose(["0", "1", "2", "3"])
        if choice == "0":
            return
        try:
            if choice == "1":
                print()
                print(reports.format_summary_report(store))
            elif choice == "2":
                display.section("Most Borrowed Books")
                ranking = reports.most_borrowed(store)
                for position, (title, count) in enumerate(ranking, start=1):
                    print(f"  {position}. {title} - {count} time(s)")
                if not ranking:
                    display.info("(no borrowing yet)")
            else:
                folder = os.path.join(store.data_dir, "..", "reports")
                path = reports.export_summary_report(store, os.path.normpath(folder))
                display.success(f"Report saved to: {os.path.relpath(path)}")
        except OSError as err:
            display.error(f"Could not write the report: {err}")


def backup_action(store):
    display.section("Backup Data")
    folder = store.backup()
    display.success(f"Data files copied to: {os.path.relpath(folder)}")


# -------------------------------------------------------------- main program
def main_menu(store):
    books = BookManager(store)
    members = MemberManager(store)
    circulation = Circulation(store)
    while True:
        display.section("MAIN MENU")
        print("  1. Book management\n  2. Member management\n"
              "  3. Issue / Return books\n  4. Reports\n"
              "  5. Backup data\n  0. Logout and exit")
        choice = choose(["0", "1", "2", "3", "4", "5"])
        if choice == "1":
            book_menu(books)
        elif choice == "2":
            member_menu(members, store)
        elif choice == "3":
            circulation_menu(store, circulation)
        elif choice == "4":
            report_menu(store)
        elif choice == "5":
            run_safely(backup_action, store)
        else:
            return


def run(data_dir=DEFAULT_DATA_DIR):
    """Start the application. Returns when the librarian logs out."""
    display.banner("LIBRARY MANAGEMENT SYSTEM")
    try:
        store = DataStore(data_dir)
        auth = AuthManager(data_dir)
    except StorageError as err:
        display.error(str(err))
        display.info("Fix or delete the damaged file in the data folder and try again.")
        return

    try:
        user = login(auth)
        if user is None:
            display.error("Too many failed attempts. Exiting.")
            return
        main_menu(store)
        display.info("You have been logged out. Goodbye!")
    except (KeyboardInterrupt, EOFError):
        print()
        display.info("Session ended. All changes were already saved.")


if __name__ == "__main__":
    run()
