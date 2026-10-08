"""
reports.py - Summary reports and report export.

Module owner : Member 6
Concepts used: Functions, dictionaries (counting), sets, sorting with lambda,
               string formatting, file handling (writing a .txt report)
"""

import os
from datetime import datetime

from circulation import today as current_date


def build_summary(store, on_date=None):
    """Collect the headline numbers into a dictionary."""
    on_date = on_date or current_date()
    books = store.books.values()
    open_loans = [t for t in store.transactions if t.is_open]
    overdue = [t for t in open_loans if t.due_date < on_date]
    fines_collected = sum(t.fine for t in store.transactions if not t.is_open)

    return {
        "report_date": str(on_date),
        "total_titles": len(store.books),
        "total_copies": sum(b.total_copies for b in books),
        "available_copies": sum(b.available_copies for b in books),
        "issued_copies": sum(b.issued_copies for b in books),
        "total_members": len(store.members),
        "members_with_loans": len({t.member_id for t in open_loans}),   # a set
        "total_transactions": len(store.transactions),
        "overdue_loans": len(overdue),
        "fines_collected": fines_collected,
    }


def category_breakdown(store):
    """Returns a list of (category, number of titles, number of copies)."""
    counts = {}                     # category -> [titles, copies]
    for book in store.books.values():
        entry = counts.setdefault(book.category, [0, 0])
        entry[0] += 1
        entry[1] += book.total_copies
    return sorted(((name, t, c) for name, (t, c) in counts.items()),
                  key=lambda row: row[0])


def most_borrowed(store, top_n=5):
    """Returns the top_n books as a list of (title, times borrowed)."""
    times = {}                      # book_id -> count
    for txn in store.transactions:
        times[txn.book_id] = times.get(txn.book_id, 0) + 1
    ranked = sorted(times.items(), key=lambda pair: pair[1], reverse=True)
    result = []
    for book_id, count in ranked[:top_n]:
        book = store.books.get(book_id)
        title = book.title if book else f"{book_id} (deleted)"
        result.append((title, count))
    return result


def format_summary_report(store, on_date=None):
    """Build the full text of the summary report (used for screen and file)."""
    s = build_summary(store, on_date)
    lines = [
        "LIBRARY SUMMARY REPORT",
        f"Date: {s['report_date']}",
        "-" * 50,
        f"Total book titles        : {s['total_titles']}",
        f"Total copies             : {s['total_copies']}",
        f"Copies available         : {s['available_copies']}",
        f"Copies issued            : {s['issued_copies']}",
        f"Registered members       : {s['total_members']}",
        f"Members holding books    : {s['members_with_loans']}",
        f"Total transactions       : {s['total_transactions']}",
        f"Overdue loans            : {s['overdue_loans']}",
        f"Fines collected (Rs)     : {s['fines_collected']}",
        "-" * 50,
        "Category-wise stock:",
    ]
    for name, titles, copies in category_breakdown(store):
        lines.append(f"  {name:<16} {titles} title(s), {copies} copies")
    lines.append("-" * 50)
    lines.append("Most borrowed books:")
    ranking = most_borrowed(store)
    if not ranking:
        lines.append("  (no borrowing yet)")
    for position, (title, count) in enumerate(ranking, start=1):
        lines.append(f"  {position}. {title} - {count} time(s)")
    return "\n".join(lines)


def export_summary_report(store, folder, on_date=None):
    """Save the summary report as a text file in `folder`; return its path."""
    os.makedirs(folder, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"summary_report_{stamp}.txt")
    with open(path, "w", encoding="utf-8") as file:
        file.write(format_summary_report(store, on_date) + "\n")
    return path
