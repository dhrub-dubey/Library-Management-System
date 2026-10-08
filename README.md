# Library Management System

A menu-driven, console-based **Library Management System** written in pure Python.
It lets a librarian manage books and members, issue and return books, calculate
late fines, and generate reports. All data is stored in JSON files, so nothing
needs to be installed.

> Project for the **Python Programming Laboratory – WCA (Group-Based Project)**,
> B.Tech 3rd Semester.

---

## 1. Objectives

* Apply Python programming concepts to solve a real-world problem.
* Replace manual register-based record keeping with a simple, reliable program.
* Demonstrate structured coding: functions, modules, classes, file handling,
  validation and exception handling.

## 2. Main Features

| Area | Features |
| --- | --- |
| Login | Librarian login with hashed password (3 attempts), logout / exit |
| Books | Add, view all, search (title / author / ISBN / category / any), update, delete |
| Members | Register, view all, search, update, delete, borrowing history |
| Circulation | Issue book (3-book limit, 14-day loan), return book, automatic fine (Rs 2/day), list of issued books, list of overdue books |
| Reports | Summary report, category-wise stock, most borrowed books, export report to a `.txt` file |
| Data | Automatic saving to JSON after every change, one-click backup of data files |
| Safety | Input validation on every field, friendly error messages, no crash on bad input or corrupted data file, type `cancel` to abort any operation |

## 3. Technologies Used

* **Python 3.8 or newer** (developed and tested on Python 3.12)
* Standard library only: `json`, `os`, `shutil`, `datetime`, `hashlib`, `secrets`, `getpass`, `re`, `tempfile`

## 4. Required Libraries

**None** to run the application (standard library only).


## 5. Installation / Setup

1. Install Python 3.8+ from <https://www.python.org/downloads/> (tick *“Add Python to PATH”* on Windows).
2. Copy the project folder `Library_Management_System`.
3. Open a terminal (Command Prompt, PowerShell or Terminal) **inside /project folder** by doing **cd project** from root.

The folder already contains demo data in `data/`, so the program is ready to use.

## 6. How to Run

```
python main.py
```

(on some systems: `python3 main.py`)

**Default login:** username `admin`, password `admin123`

To run the automated tests:

```
python run_tests.py
```

To reset the demo data:

```
python tools/create_sample_data.py
```

## 7. Basic Usage

1. Log in with the username and password above.
2. Choose a menu number and press Enter:

```
MAIN MENU
  1. Book management
  2. Member management
  3. Issue / Return books
  4. Reports
  5. Backup data
  0. Logout and exit
```

3. Follow the prompts. Type `cancel` at any prompt to abort the current operation.
4. In update screens, press **Enter** to keep the existing value.
5. Choose `0` to go back, and `0` from the main menu to log out.

**Library Rules:** 
1. A member can hold at most **3** books
2. Loan period is **14 days** 
3. Fine is **Rs 2 per day** after the due date 
4. A book that is issued cannot be deleted 
5. A member holding books cannot be deleted

## 8. Project Structure

```
Library_Management_System/project
├── auth.py              Librarian login with hashed password
├── book_manager.py      Book operations
├── circulation.py       Issue / return / fine / overdue logic
├── display.py           Console tables and messages
├── exceptions.py        Custom exception classes
├── main.py              Menus and user flow (entry point)
├── member_manager.py    Member operations
├── models.py            Book, Member, Transaction classes (OOP)
├── reports.py           Summary reports and export
├── run_tests.py         42 automated test cases
├── storage.py           DataStore - loading, saving and backup of JSON files
├── validators.py        Input validation functions
├── data/
│   ├── books.json
│   ├── members.json
│   ├── transactions.json
│   └── users.json
├── docs/
│   └── test_results.json 
├── screenshots/
│   ├── 01_login_and_logout.png
│   ├── 02_view_books.png
│   ├── 03_add_book_validation.png
│   ├── 04_search_books.png
│   ├── 05_update_book.png
│   ├── 06_delete_book.png
│   ├── 07_add_member.png
│   ├── 08_member_history.png
│   ├── 09_issue_book.png
│   ├── 10_issue_limit_duplicate.png
│   ├── 11_issue_no_copies.png
│   ├── 12_overdue_books.png
│   ├── 13_return_with_fine.png
│   ├── 14_summary_report.png
│   ├── 15_export_and_backup.png
│   └── 16_invalid_menu_and_cancel.png
└── tools/
    └── create_sample_data.py
```

## 9. Group Members and Individual Contribution

> We divided the project into separate modules so that each group member could contribute to a specific area of the Library Management System. 
> The contributions covered data modelling, storage, authentication, book and member management, circulation, reports, testing, and documentation.

| Student | Roll No. | Assigned Module / Responsibility | Files |
| --- | --- | --- | --- |
| Member 1 – *Uzma Jabbar* | *33* | Data models and custom exceptions (OOP) | `models.py`, `exceptions.py` |
| Member 2 – *Mesba Mollah* | *43* | File handling, data storage, backup, login | `storage.py`, `auth.py`, `data/` |
| Member 3 – *Fazal Rahman* | *56* | Book management and input validation | `book_manager.py`, `validators.py` |
| Member 4 – *Rupsa Chatterjee* | *57* | Member management and console display | `member_manager.py`, `display.py` |
| Member 5 – *Mujtaba Mia* | *54* | Issue / return, due dates, fines, overdue| `circulation.py` |
| Member 6 – *Dhrub Dubey* | *46* | Menus / user flow, reports, testing, documentation | `main.py`, `reports.py`, `run_tests.py`, `README.md` |

Each source file also names its owner in the docstring at the top.

## 10. Known Limitations

* Single librarian account type; no separate student login.
* ISBN is checked for length/digits only (no check-digit validation; ISBN-10 ending in `X` is not accepted).
* Console only (no graphical interface); one user at a time.
* Fine is recorded at return time; there is no separate fine-payment tracking.
