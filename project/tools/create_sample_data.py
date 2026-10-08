"""
create_sample_data.py - (Re)creates the demo data in the data/ folder.

Run from the project folder:   python tools/create_sample_data.py

It uses the application's own classes, so the data always passes the same
validation rules as data typed in through the menus. Existing data files are
overwritten, so only run it when you want to reset the demo data.

NOTE: ISBNs below are sample values for demonstration.
"""

import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from auth import AuthManager                      # noqa: E402
from book_manager import BookManager              # noqa: E402
from circulation import Circulation               # noqa: E402
from member_manager import MemberManager          # noqa: E402
from storage import DataStore                     # noqa: E402

BOOKS = [
    ("Python Crash Course", "Eric Matthes", "978-1593279288", "Programming", 2019, 3),
    ("Think Python", "Allen Downey", "978-1491929568", "Programming", 2015, 2),
    ("Automate the Boring Stuff", "Al Sweigart", "978-1593275990", "Programming", 2015, 2),
    ("Clean Code", "Robert Martin", "978-0132350884", "Programming", 2008, 2),
    ("Introduction to Algorithms", "Thomas Cormen", "978-0262033848", "Computer Science", 2009, 2),
    ("Data Structures Using C", "Reema Thareja", "978-0198099307", "Computer Science", 2014, 3),
    ("Engineering Mathematics", "B S Grewal", "978-8174091955", "Mathematics", 2012, 4),
    ("Concepts of Physics", "H C Verma", "978-8177091878", "Physics", 2017, 3),
    ("A Brief History of Time", "Stephen Hawking", "978-0553380163", "Science", 1998, 2),
    ("Wings of Fire", "A P J Abdul Kalam", "978-8173711466", "Biography", 1999, 3),
    ("The Alchemist", "Paulo Coelho", "978-0062315007", "Fiction", 1988, 2),
    ("Malgudi Days", "R K Narayan", "978-0143039655", "Fiction", 1943, 1),
]

MEMBERS = [
    ("Aarav Sharma", "aarav.sharma@example.com", "9876543210"),
    ("Priya Verma", "priya.verma@example.com", "9123456780"),
    ("Rohan Gupta", "rohan.gupta@example.com", "9988776655"),
    ("Sneha Iyer", "sneha.iyer@example.com", "8899001122"),
    ("Karan Singh", "karan.singh@example.com", "7012345678"),
]


def main():
    data_dir = os.path.join(ROOT, "data")
    for name in ("books.json", "members.json", "transactions.json", "users.json"):
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            os.remove(path)

    store = DataStore(data_dir)
    AuthManager(data_dir)                          # creates users.json (admin)
    books, members, circ = BookManager(store), MemberManager(store), Circulation(store)

    for row in BOOKS:
        books.add_book(*row)
    for row in MEMBERS:
        members.add_member(*row)
    for member in store.members.values():          # fixed join date for the demo
        member.join_date = date(2026, 8, 1)
    store.save()

    # (member, book, issued on, returned on or None)
    loans = [
        ("M003", "B002", date(2026, 9, 1), date(2026, 9, 12)),    # on time
        ("M004", "B005", date(2026, 8, 20), date(2026, 9, 10)),   # 7 days late
        ("M002", "B004", date(2026, 9, 28), None),                # still issued
        ("M001", "B001", date(2026, 9, 10), None),                # OVERDUE
        ("M001", "B010", date(2026, 10, 1), None),                # still issued
    ]
    for member_id, book_id, issued, returned in loans:
        circ.issue_book(member_id, book_id, issue_date=issued)
        if returned:
            circ.return_book(member_id, book_id, return_date=returned)

    print(f"Sample data created: {len(store.books)} books, "
          f"{len(store.members)} members, {len(store.transactions)} transactions.")


if __name__ == "__main__":
    main()
