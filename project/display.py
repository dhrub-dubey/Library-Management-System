"""
display.py - Helpers that print headings and neat tables on the console.

Module owner : Member 4
Concepts used: Functions, strings (ljust, center, f-strings), loops, lists

Only plain ASCII characters are printed so the program works on every
terminal (including Windows Command Prompt).
"""

from circulation import FINE_PER_DAY

LINE_WIDTH = 98


def banner(title):
    print("=" * LINE_WIDTH)
    print(title.center(LINE_WIDTH))
    print("=" * LINE_WIDTH)


def section(title):
    print()
    print(f"--- {title} " + "-" * max(0, LINE_WIDTH - len(title) - 5))


def info(message):
    print(f"  {message}")


def success(message):
    print(f"  [OK] {message}")


def error(message):
    print(f"  [ERROR] {message}")


def truncate(text, width):
    """Shorten long text with '...' so tables stay aligned."""
    text = str(text)
    return text if len(text) <= width else text[:width - 3] + "..."


def print_table(headers, rows, widths):
    """Print a table. `rows` is a list of lists; `widths` gives column widths."""
    if not rows:
        print("  (no records)")
        return
    head = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(head)
    print("  ".join("-" * w for w in widths))
    for row in rows:
        cells = [truncate(cell, w).ljust(w) for cell, w in zip(row, widths)]
        print("  ".join(cells))


def print_books(books):
    rows = [[b.book_id, b.title, b.author, b.category, b.year,
             f"{b.available_copies}/{b.total_copies}"] for b in books]
    print_table(["ID", "Title", "Author", "Category", "Year", "Avail"],
                rows, [5, 30, 22, 16, 4, 6])


def print_members(members):
    rows = [[m.member_id, m.name, m.email, m.phone, str(m.join_date)]
            for m in members]
    print_table(["ID", "Name", "E-mail", "Phone", "Joined"],
                rows, [5, 22, 30, 10, 10])


def print_loans(loans, store, today):
    """Table of loan records with status and fine."""
    rows = []
    for t in loans:
        member = store.members.get(t.member_id)
        book = store.books.get(t.book_id)
        member_text = f"{t.member_id} {member.name}" if member else t.member_id
        book_text = book.title if book else t.book_id
        late = t.days_overdue(today)
        if t.is_open:
            status = f"OVERDUE {late}d" if late else "Issued"
            fine = f"Rs {late * FINE_PER_DAY}" if late else "-"
        else:
            status = "Returned"
            fine = f"Rs {t.fine}" if t.fine else "-"
        rows.append([t.txn_id, member_text, book_text, str(t.issue_date),
                     str(t.due_date), status, fine])
    print_table(["Txn", "Member", "Book", "Issued", "Due", "Status", "Fine"],
                rows, [5, 18, 22, 10, 10, 11, 6])
