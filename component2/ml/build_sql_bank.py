"""Build the non-executed SQL bank (`component2/models/coding_bank_sql.json`).

SQL is graded **without executing anything**: the product has no database engine
at grading time, so a SQL coding question is text-graded exactly like the
non-executed coding formats in ``coding_bank_nonexecuted.json``.  This script is
the SQL sibling of ``build_nonexecuted_bank.py`` and follows its conventions
(docstring style, validation pass, ``--validate`` flag, per-format report).

Two formats:

* ``Predict Output`` -- a self-contained snippet (``CREATE TABLE`` + ``INSERT``
  rows + the query under test).  The answer key is authored *and then proven*:
  the build opens an in-memory ``sqlite3`` database, runs the whole snippet and
  refuses to ship unless the stated answer matches the engine's own rendering.
* ``Find the Bug`` -- one line of a SQL query is wrong; the candidate picks the
  replacement line.  Every distractor is wrong for a reason we can name.

Answer keys
-----------
Predict Output keys are the SQL result rendered as a single canonical string:
one value per column joined with ``" | "`` and (only when an ``ORDER BY`` forces
the order) multiple rows joined with ``" \\n "``.  ``NULL`` is the literal text
``NULL`` and numbers are exactly as SQLite renders them (``3``, not ``3.0``).

How the Find-the-Bug intended results were determined
-----------------------------------------------------
A Find-the-Bug question is only a *query* (no data shown).  To prove its key, the
builder keeps a hidden ``setup`` (``CREATE TABLE`` + ``INSERT``) and a stated
intended result for the corrected query.  For each question the build:

1. substitutes the correct option for the marked line and runs
   ``setup`` + corrected query in ``sqlite3``; the result must equal the stated
   intended result, else the build fails;
2. runs the *unfixed* query and requires that it errors or returns something
   different (otherwise there is no bug);
3. runs each distractor substituted for the marked line and requires that it
   either errors or returns something different from the intended result, so a
   distractor can never be silently correct for this data.

The hidden ``setup`` is verification-only and is stripped from the shipped JSON;
the shipped ``code`` for Find the Bug is just the query with a
``-- the marked line is wrong: <line>`` comment above the offending line.

Usage (from ``component2/``):
    python ml/build_sql_bank.py
    python ml/build_sql_bank.py --out models/coding_bank_sql.json
    python ml/build_sql_bank.py --validate          # validate the file only
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

_MODELS = Path(__file__).resolve().parents[1] / "models"

LANGUAGE = "SQL"
CATEGORY = "SQL Queries"              # must contain "SQL" for the sql profile gate
FORMATS = ("Predict Output", "Find the Bug")
DIFFICULTIES = ("Easy", "Medium", "Hard")
# The product's "sql" profile matches a question when category/topic/question_text
# contains one of these (see services/ml_engine.py).  category always matches via
# "SQL"; the question text is also required to carry one of them.
PROFILE_KEYWORDS = ("sql", "query", "database", "schema", "index", "join", "select")
PREDICT_MARKER = "-- predict the output of this query"
BUG_MARKER = "-- the marked line is wrong"
TIME_LIMIT = 300


# ---------------------------------------------------------------------------
# Authored Predict Output questions
#   (topic, difficulty, setup, query, expected)
# ``setup`` is the CREATE TABLE / INSERT block; ``query`` is the statement under
# test (shown last, after PREDICT_MARKER).  ``expected`` is the canonical result.
# ---------------------------------------------------------------------------
PREDICT_OUTPUT: list[tuple[str, str, str, str, str]] = [
    # ------------------------- basic SELECT / WHERE -------------------------
    (
        "basic SELECT and WHERE", "Easy",
        """CREATE TABLE employees (id INTEGER, name TEXT, salary INTEGER);
INSERT INTO employees VALUES (1, 'Alice', 5000);
INSERT INTO employees VALUES (2, 'Bob', 3000);
INSERT INTO employees VALUES (3, 'Carol', 7000);""",
        "SELECT name FROM employees WHERE salary > 4000 ORDER BY name;",
        "Alice \n Carol",
    ),
    (
        "AND / OR precedence", "Medium",
        """CREATE TABLE flags (id INTEGER, a INTEGER, b INTEGER);
INSERT INTO flags VALUES (1, 1, 0);
INSERT INTO flags VALUES (2, 0, 1);
INSERT INTO flags VALUES (3, 1, 1);""",
        "SELECT COUNT(*) FROM flags WHERE a = 1 OR b = 1 AND id = 1;",
        "2",
    ),
    # ------------------------- ORDER BY / LIMIT -----------------------------
    (
        "ORDER BY with LIMIT", "Easy",
        """CREATE TABLE products (id INTEGER, name TEXT, price INTEGER);
INSERT INTO products VALUES (1, 'Pen', 10);
INSERT INTO products VALUES (2, 'Book', 50);
INSERT INTO products VALUES (3, 'Bag', 30);
INSERT INTO products VALUES (4, 'Cup', 20);""",
        "SELECT name FROM products ORDER BY price DESC LIMIT 1;",
        "Book",
    ),
    (
        "GROUP BY with ORDER BY", "Medium",
        """CREATE TABLE staff (dept TEXT, salary INTEGER);
INSERT INTO staff VALUES ('Eng', 1000);
INSERT INTO staff VALUES ('Eng', 2000);
INSERT INTO staff VALUES ('Sales', 500);
INSERT INTO staff VALUES ('Eng', 3000);""",
        "SELECT dept, COUNT(*) FROM staff GROUP BY dept ORDER BY dept;",
        "Eng | 3 \n Sales | 1",
    ),
    # ------------------------------- DISTINCT -------------------------------
    (
        "DISTINCT count", "Easy",
        """CREATE TABLE visits (user_id INTEGER);
INSERT INTO visits VALUES (1);
INSERT INTO visits VALUES (1);
INSERT INTO visits VALUES (2);
INSERT INTO visits VALUES (3);
INSERT INTO visits VALUES (3);
INSERT INTO visits VALUES (3);""",
        "SELECT COUNT(DISTINCT user_id) FROM visits;",
        "3",
    ),
    # --------------------------- aggregates / GROUP BY ----------------------
    (
        "aggregate functions", "Easy",
        """CREATE TABLE sales (amount INTEGER);
INSERT INTO sales VALUES (100);
INSERT INTO sales VALUES (200);
INSERT INTO sales VALUES (300);""",
        "SELECT SUM(amount), COUNT(amount) FROM sales;",
        "600 | 3",
    ),
    (
        "HAVING filter on groups", "Medium",
        """CREATE TABLE staff2 (dept TEXT, salary INTEGER);
INSERT INTO staff2 VALUES ('Eng', 6000);
INSERT INTO staff2 VALUES ('Eng', 5000);
INSERT INTO staff2 VALUES ('Sales', 1000);
INSERT INTO staff2 VALUES ('Sales', 2000);""",
        "SELECT dept, SUM(salary) AS total FROM staff2 GROUP BY dept HAVING SUM(salary) > 5000 ORDER BY dept;",
        "Eng | 11000",
    ),
    (
        "COUNT(*) versus COUNT(column)", "Hard",
        """CREATE TABLE notes (id INTEGER, note TEXT);
INSERT INTO notes VALUES (1, 'a');
INSERT INTO notes VALUES (2, NULL);
INSERT INTO notes VALUES (3, 'b');""",
        "SELECT COUNT(*), COUNT(note) FROM notes;",
        "3 | 2",
    ),
    (
        "AVG returns a decimal", "Medium",
        """CREATE TABLE scores2 (score INTEGER);
INSERT INTO scores2 VALUES (10);
INSERT INTO scores2 VALUES (20);""",
        "SELECT AVG(score) FROM scores2;",
        "15.0",
    ),
    (
        "MIN and MAX on text", "Easy",
        """CREATE TABLE words (word TEXT);
INSERT INTO words VALUES ('banana');
INSERT INTO words VALUES ('apple');
INSERT INTO words VALUES ('cherry');""",
        "SELECT MIN(word), MAX(word) FROM words;",
        "apple | cherry",
    ),
    # --------------------------------- joins --------------------------------
    (
        "INNER JOIN with WHERE", "Medium",
        """CREATE TABLE customers (id INTEGER, name TEXT);
INSERT INTO customers VALUES (1, 'Alice');
INSERT INTO customers VALUES (2, 'Bob');
INSERT INTO customers VALUES (3, 'Carol');
CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount INTEGER);
INSERT INTO orders VALUES (10, 1, 150);
INSERT INTO orders VALUES (11, 2, 50);
INSERT INTO orders VALUES (12, 1, 200);""",
        "SELECT DISTINCT c.name FROM customers c JOIN orders o ON o.customer_id = c.id WHERE o.amount > 100 ORDER BY c.name;",
        "Alice",
    ),
    (
        "LEFT JOIN finding unmatched rows", "Hard",
        """CREATE TABLE customers2 (id INTEGER, name TEXT);
INSERT INTO customers2 VALUES (1, 'Alice');
INSERT INTO customers2 VALUES (2, 'Bob');
INSERT INTO customers2 VALUES (3, 'Carol');
CREATE TABLE orders2 (id INTEGER, customer_id INTEGER);
INSERT INTO orders2 VALUES (10, 1);
INSERT INTO orders2 VALUES (11, 1);
INSERT INTO orders2 VALUES (12, 2);""",
        "SELECT COUNT(*) FROM customers2 c LEFT JOIN orders2 o ON o.customer_id = c.id WHERE o.id IS NULL;",
        "1",
    ),
    # ------------------------------- subqueries -----------------------------
    (
        "subquery with IN", "Medium",
        """CREATE TABLE emp (id INTEGER, name TEXT, dept_id INTEGER);
INSERT INTO emp VALUES (1, 'Alice', 1);
INSERT INTO emp VALUES (2, 'Bob', 2);
INSERT INTO emp VALUES (3, 'Carol', 1);
CREATE TABLE dept (id INTEGER, dname TEXT);
INSERT INTO dept VALUES (1, 'Eng');
INSERT INTO dept VALUES (2, 'Sales');""",
        "SELECT name FROM emp WHERE dept_id IN (SELECT id FROM dept WHERE dname = 'Eng') ORDER BY name;",
        "Alice \n Carol",
    ),
    (
        "scalar subquery", "Medium",
        """CREATE TABLE emp2 (id INTEGER, name TEXT, salary INTEGER);
INSERT INTO emp2 VALUES (1, 'Alice', 5000);
INSERT INTO emp2 VALUES (2, 'Bob', 9000);
INSERT INTO emp2 VALUES (3, 'Carol', 9000);""",
        "SELECT name FROM emp2 WHERE salary = (SELECT MAX(salary) FROM emp2) ORDER BY name;",
        "Bob \n Carol",
    ),
    (
        "second highest with a subquery", "Hard",
        """CREATE TABLE emp4 (id INTEGER, name TEXT, salary INTEGER);
INSERT INTO emp4 VALUES (1, 'Alice', 5000);
INSERT INTO emp4 VALUES (2, 'Bob', 9000);
INSERT INTO emp4 VALUES (3, 'Carol', 7000);""",
        "SELECT MAX(salary) FROM emp4 WHERE salary < (SELECT MAX(salary) FROM emp4);",
        "7000",
    ),
    # ---------------------------------- CASE --------------------------------
    (
        "CASE expression", "Medium",
        """CREATE TABLE emp3 (id INTEGER, name TEXT, salary INTEGER);
INSERT INTO emp3 VALUES (1, 'Alice', 5000);
INSERT INTO emp3 VALUES (2, 'Bob', 3000);""",
        "SELECT name, CASE WHEN salary >= 5000 THEN 'High' ELSE 'Low' END AS band FROM emp3 ORDER BY name;",
        "Alice | High \n Bob | Low",
    ),
    # -------------------------------- functions -----------------------------
    (
        "string functions", "Easy",
        """CREATE TABLE users (id INTEGER, name TEXT);
INSERT INTO users VALUES (1, 'Alice');
INSERT INTO users VALUES (2, 'Bob');""",
        "SELECT UPPER(name) || ' has ' || LENGTH(name) || ' letters' FROM users WHERE id = 1;",
        "ALICE has 5 letters",
    ),
    (
        "numeric functions", "Medium",
        """CREATE TABLE nums (x INTEGER);
INSERT INTO nums VALUES (10);
INSERT INTO nums VALUES (20);
INSERT INTO nums VALUES (30);""",
        "SELECT ABS(-7) + ROUND(AVG(x)) FROM nums;",
        "27.0",
    ),
    (
        "integer division and modulo", "Medium",
        """CREATE TABLE dummy (x INTEGER);
INSERT INTO dummy VALUES (1);""",
        "SELECT 5 / 2 AS a, 5.0 / 2 AS b, 5 % 2 AS c FROM dummy;",
        "2 | 2.5 | 1",
    ),
    # ------------------------------ NULL handling ---------------------------
    (
        "COALESCE replacing NULL", "Medium",
        """CREATE TABLE acct (id INTEGER, balance INTEGER);
INSERT INTO acct VALUES (1, 100);
INSERT INTO acct VALUES (2, NULL);""",
        "SELECT COALESCE(balance, 0) FROM acct WHERE id = 2;",
        "0",
    ),
    (
        "NOT IN with a NULL", "Hard",
        """CREATE TABLE a (id INTEGER);
INSERT INTO a VALUES (1);
INSERT INTO a VALUES (2);
INSERT INTO a VALUES (3);
CREATE TABLE b (id INTEGER);
INSERT INTO b VALUES (1);
INSERT INTO b VALUES (NULL);""",
        "SELECT COUNT(*) FROM a WHERE id NOT IN (SELECT id FROM b);",
        "0",
    ),
    # --------------------------------- predicates ---------------------------
    (
        "BETWEEN is inclusive", "Easy",
        """CREATE TABLE items (id INTEGER, price INTEGER);
INSERT INTO items VALUES (1, 5);
INSERT INTO items VALUES (2, 10);
INSERT INTO items VALUES (3, 15);
INSERT INTO items VALUES (4, 20);
INSERT INTO items VALUES (5, 25);""",
        "SELECT COUNT(*) FROM items WHERE price BETWEEN 10 AND 20;",
        "3",
    ),
    (
        "LIKE prefix match", "Easy",
        """CREATE TABLE people2 (id INTEGER, name TEXT);
INSERT INTO people2 VALUES (1, 'Ann');
INSERT INTO people2 VALUES (2, 'Ada');
INSERT INTO people2 VALUES (3, 'Bob');
INSERT INTO people2 VALUES (4, 'Amy');""",
        "SELECT COUNT(*) FROM people2 WHERE name LIKE 'A%';",
        "3",
    ),
    # ------------------------------ set operators ---------------------------
    (
        "UNION removes duplicates", "Medium",
        """CREATE TABLE t1 (c INTEGER);
INSERT INTO t1 VALUES (1);
INSERT INTO t1 VALUES (2);
INSERT INTO t1 VALUES (2);
CREATE TABLE t2 (c INTEGER);
INSERT INTO t2 VALUES (2);
INSERT INTO t2 VALUES (3);""",
        "SELECT COUNT(*) FROM (SELECT c FROM t1 UNION SELECT c FROM t2) AS u;",
        "3",
    ),
    (
        "UNION ALL keeps duplicates", "Medium",
        """CREATE TABLE t1 (c INTEGER);
INSERT INTO t1 VALUES (1);
INSERT INTO t1 VALUES (2);
INSERT INTO t1 VALUES (2);
CREATE TABLE t2 (c INTEGER);
INSERT INTO t2 VALUES (2);
INSERT INTO t2 VALUES (3);""",
        "SELECT COUNT(*) FROM (SELECT c FROM t1 UNION ALL SELECT c FROM t2) AS u;",
        "5",
    ),
    (
        "EXCEPT", "Hard",
        """CREATE TABLE t3 (c INTEGER);
INSERT INTO t3 VALUES (1);
INSERT INTO t3 VALUES (2);
INSERT INTO t3 VALUES (3);
CREATE TABLE t4 (c INTEGER);
INSERT INTO t4 VALUES (2);
INSERT INTO t4 VALUES (3);
INSERT INTO t4 VALUES (4);""",
        "SELECT COUNT(*) FROM (SELECT c FROM t3 EXCEPT SELECT c FROM t4) AS r;",
        "1",
    ),
    (
        "INTERSECT", "Hard",
        """CREATE TABLE t5 (c INTEGER);
INSERT INTO t5 VALUES (1);
INSERT INTO t5 VALUES (2);
INSERT INTO t5 VALUES (3);
CREATE TABLE t6 (c INTEGER);
INSERT INTO t6 VALUES (2);
INSERT INTO t6 VALUES (3);
INSERT INTO t6 VALUES (4);""",
        "SELECT COUNT(*) FROM (SELECT c FROM t5 INTERSECT SELECT c FROM t6) AS r;",
        "2",
    ),
]


# ---------------------------------------------------------------------------
# Authored Find the Bug questions
#   (topic, difficulty, intent, setup, query, broken_line, correct_line,
#    [distractor_line, ...], expected_with_correct)
# ``setup`` and ``expected_with_correct`` are verification-only and are not
# shipped; the shipped ``code`` is ``query`` with a marker comment above
# ``broken_line``.
# ---------------------------------------------------------------------------
FIND_THE_BUG: list[tuple[str, str, str, str, str, str, str, list[str], str]] = [
    (
        "GROUP BY / HAVING", "Medium",
        "Return the number of employees in each department that has more than one employee",
        """CREATE TABLE employees (department TEXT, salary INTEGER);
INSERT INTO employees VALUES ('Eng', 5000);
INSERT INTO employees VALUES ('Eng', 3000);
INSERT INTO employees VALUES ('Sales', 7000);""",
        """SELECT department, COUNT(*) AS n
FROM employees
GROUP BY department
WHERE COUNT(*) > 1
ORDER BY department;""",
        "WHERE COUNT(*) > 1",
        "HAVING COUNT(*) > 1",
        ["WHERE COUNT(*) > 1", "HAVING COUNT(*) = 1", "HAVING SUM(salary) > 1000"],
        "Eng | 2",
    ),
    (
        "comparison operator", "Easy",
        "Return the number of orders that are not paid",
        """CREATE TABLE orders (id INTEGER, status TEXT);
INSERT INTO orders VALUES (1, 'paid');
INSERT INTO orders VALUES (2, 'pending');
INSERT INTO orders VALUES (3, 'paid');
INSERT INTO orders VALUES (4, 'cancelled');
INSERT INTO orders VALUES (5, 'pending');""",
        """SELECT COUNT(*) AS n
FROM orders
WHERE status = 'paid';""",
        "WHERE status = 'paid'",
        "WHERE status <> 'paid'",
        ["WHERE status = 'paid'", "WHERE status = 'cancelled'", "WHERE status IS NULL"],
        "3",
    ),
    (
        "LEFT JOIN", "Medium",
        "Return each customer name and their order count, including customers with no orders",
        """CREATE TABLE customers (id INTEGER, name TEXT);
INSERT INTO customers VALUES (1, 'Alice');
INSERT INTO customers VALUES (2, 'Bob');
INSERT INTO customers VALUES (3, 'Carol');
CREATE TABLE orders (id INTEGER, customer_id INTEGER);
INSERT INTO orders VALUES (1, 1);
INSERT INTO orders VALUES (2, 1);
INSERT INTO orders VALUES (3, 2);""",
        """SELECT c.name, COUNT(o.id) AS n
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.name
ORDER BY c.name;""",
        "JOIN orders o ON o.customer_id = c.id",
        "LEFT JOIN orders o ON o.customer_id = c.id",
        [
            "INNER JOIN orders o ON o.customer_id = c.id",
            "JOIN orders o ON o.id = c.id",
            "JOIN orders o ON o.customer_id = c.id AND o.id > 1",
        ],
        "Alice | 2 \n Bob | 1 \n Carol | 0",
    ),
    (
        "DISTINCT", "Easy",
        "Return each department name exactly once",
        """CREATE TABLE employees (department TEXT);
INSERT INTO employees VALUES ('Eng');
INSERT INTO employees VALUES ('Eng');
INSERT INTO employees VALUES ('Sales');
INSERT INTO employees VALUES ('Sales');
INSERT INTO employees VALUES ('Sales');""",
        """SELECT department
FROM employees
ORDER BY department;""",
        "SELECT department",
        "SELECT DISTINCT department",
        ["SELECT department", "SELECT COUNT(department)", "SELECT UNIQUE department"],
        "Eng \n Sales",
    ),
    (
        "aggregate choice", "Medium",
        "Return the average score for each student",
        """CREATE TABLE scores (student TEXT, score INTEGER);
INSERT INTO scores VALUES ('Alice', 10);
INSERT INTO scores VALUES ('Alice', 20);
INSERT INTO scores VALUES ('Bob', 30);""",
        """SELECT student, SUM(score) AS avg_score
FROM scores
GROUP BY student
ORDER BY student;""",
        "SELECT student, SUM(score) AS avg_score",
        "SELECT student, AVG(score) AS avg_score",
        [
            "SELECT student, SUM(score) AS avg_score",
            "SELECT student, COUNT(score) AS avg_score",
            "SELECT student, MIN(score) AS avg_score",
        ],
        "Alice | 15.0 \n Bob | 30.0",
    ),
    (
        "AND / OR precedence", "Hard",
        "Return employees with a salary above 5000 who work in department 'Eng' or 'Sales'",
        """CREATE TABLE employees (id INTEGER, name TEXT, department TEXT, salary INTEGER);
INSERT INTO employees VALUES (1, 'Alice', 'Eng', 6000);
INSERT INTO employees VALUES (2, 'Bob', 'Eng', 4000);
INSERT INTO employees VALUES (3, 'Carol', 'Sales', 3000);
INSERT INTO employees VALUES (4, 'Dave', 'Sales', 8000);
INSERT INTO employees VALUES (5, 'Eve', 'Eng', 5000);""",
        """SELECT name
FROM employees
WHERE salary > 5000 AND department = 'Eng' OR department = 'Sales'
ORDER BY name;""",
        "WHERE salary > 5000 AND department = 'Eng' OR department = 'Sales'",
        "WHERE salary > 5000 AND (department = 'Eng' OR department = 'Sales')",
        [
            "WHERE salary > 5000 AND department = 'Eng' OR department = 'Sales'",
            "WHERE salary >= 5000 AND (department = 'Eng' OR department = 'Sales')",
            "WHERE salary > 5000 AND department IN ('Eng')",
        ],
        "Alice \n Dave",
    ),
    (
        "NULL comparison", "Medium",
        "Return the names of employees whose manager is not set",
        """CREATE TABLE employees (id INTEGER, name TEXT, manager_id INTEGER);
INSERT INTO employees VALUES (1, 'Alice', NULL);
INSERT INTO employees VALUES (2, 'Bob', 1);
INSERT INTO employees VALUES (3, 'Carol', NULL);""",
        """SELECT name
FROM employees
WHERE manager_id = NULL
ORDER BY name;""",
        "WHERE manager_id = NULL",
        "WHERE manager_id IS NULL",
        [
            "WHERE manager_id = NULL",
            "WHERE manager_id IS NOT NULL",
            "WHERE manager_id <> NULL",
            "WHERE manager_id = 0",
        ],
        "Alice \n Carol",
    ),
    (
        "BETWEEN off-by-one", "Medium",
        "Return products whose price is from 10 to 20 inclusive",
        """CREATE TABLE products (name TEXT, price INTEGER);
INSERT INTO products VALUES ('A', 10);
INSERT INTO products VALUES ('B', 15);
INSERT INTO products VALUES ('C', 20);""",
        """SELECT name
FROM products
WHERE price BETWEEN 11 AND 20
ORDER BY name;""",
        "WHERE price BETWEEN 11 AND 20",
        "WHERE price BETWEEN 10 AND 20",
        [
            "WHERE price BETWEEN 11 AND 20",
            "WHERE price BETWEEN 10 AND 19",
            "WHERE price > 10 AND price < 20",
            "WHERE price BETWEEN 20 AND 10",
        ],
        "A \n B \n C",
    ),
    (
        "LIMIT off-by-one", "Medium",
        "Return the names of the two highest-paid employees",
        """CREATE TABLE employees (name TEXT, salary INTEGER);
INSERT INTO employees VALUES ('Alice', 9000);
INSERT INTO employees VALUES ('Bob', 8000);
INSERT INTO employees VALUES ('Carol', 7000);
INSERT INTO employees VALUES ('Dave', 6000);""",
        """SELECT name
FROM employees
ORDER BY salary DESC
LIMIT 3;""",
        "LIMIT 3;",
        "LIMIT 2;",
        ["LIMIT 3;", "LIMIT 1;", "LIMIT 4;", "LIMIT 0;"],
        "Alice \n Bob",
    ),
    (
        "wrong join column", "Medium",
        "Return each customer name with the amount of their order",
        """CREATE TABLE customers (id INTEGER, name TEXT);
INSERT INTO customers VALUES (1, 'Alice');
INSERT INTO customers VALUES (2, 'Bob');
CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount INTEGER);
INSERT INTO orders VALUES (100, 1, 50);
INSERT INTO orders VALUES (101, 2, 70);""",
        """SELECT c.name, o.amount
FROM customers c
JOIN orders o ON o.id = c.id
ORDER BY c.name;""",
        "JOIN orders o ON o.id = c.id",
        "JOIN orders o ON o.customer_id = c.id",
        [
            "JOIN orders o ON o.id = c.id",
            "JOIN orders o ON o.customer_id = o.id",
            "JOIN orders o ON c.id = o.amount",
            "JOIN orders o ON o.customer_id = c.id AND o.amount > 60",
        ],
        "Alice | 50 \n Bob | 70",
    ),
    (
        "HAVING versus WHERE", "Hard",
        "Return departments whose total salary is above 10000",
        """CREATE TABLE employees (department TEXT, salary INTEGER);
INSERT INTO employees VALUES ('Eng', 6000);
INSERT INTO employees VALUES ('Eng', 5000);
INSERT INTO employees VALUES ('Sales', 3000);
INSERT INTO employees VALUES ('Sales', 7000);""",
        """SELECT department, SUM(salary) AS total
FROM employees
GROUP BY department
WHERE SUM(salary) > 10000
ORDER BY department;""",
        "WHERE SUM(salary) > 10000",
        "HAVING SUM(salary) > 10000",
        [
            "WHERE SUM(salary) > 10000",
            "HAVING SUM(salary) >= 10000",
            "HAVING COUNT(*) > 10000",
            "HAVING SUM(salary) > 1000",
        ],
        "Eng | 11000",
    ),
    (
        "COUNT(DISTINCT ...)", "Hard",
        "Return the number of distinct customers who placed an order",
        """CREATE TABLE orders (customer_id INTEGER);
INSERT INTO orders VALUES (1);
INSERT INTO orders VALUES (1);
INSERT INTO orders VALUES (2);
INSERT INTO orders VALUES (3);
INSERT INTO orders VALUES (3);""",
        """SELECT COUNT(customer_id) AS customers
FROM orders;""",
        "SELECT COUNT(customer_id) AS customers",
        "SELECT COUNT(DISTINCT customer_id) AS customers",
        [
            "SELECT COUNT(customer_id) AS customers",
            "SELECT COUNT(*) AS customers",
            "SELECT COUNT(customer_id) + 1 AS customers",
            "SELECT SUM(customer_id) AS customers",
        ],
        "3",
    ),
    (
        "LIKE pattern", "Easy",
        "Return the names that start with the letter A",
        """CREATE TABLE people (name TEXT);
INSERT INTO people VALUES ('Ann');
INSERT INTO people VALUES ('Ada');
INSERT INTO people VALUES ('Bob');""",
        """SELECT name
FROM people
WHERE name LIKE '%A'
ORDER BY name;""",
        "WHERE name LIKE '%A'",
        "WHERE name LIKE 'A%'",
        [
            "WHERE name LIKE '%A'",
            "WHERE name LIKE 'B%'",
            "WHERE name = 'Ann'",
        ],
        "Ada \n Ann",
    ),
]


# ---------------------------------------------------------------------------
# Rendering / execution
# ---------------------------------------------------------------------------
def render_rows(rows: list[tuple]) -> str:
    """Canonical rendering: values joined by ``" | "``, rows by ``" \\n "``."""
    if not rows:
        return "(no rows)"
    rendered = []
    for row in rows:
        rendered.append(" | ".join("NULL" if v is None else str(v) for v in row))
    return " \n ".join(rendered)


def execute_sql(setup: str, query: str) -> tuple[str | None, str | None]:
    """Run ``query`` against a fresh in-memory database seeded by ``setup``.

    Returns ``(rendered_result, None)`` on success or ``(None, error)`` when
    SQLite rejects the statement.
    """
    conn = sqlite3.connect(":memory:")
    try:
        if setup and setup.strip():
            conn.executescript(setup)
        cur = conn.execute(query)
        return render_rows(cur.fetchall()), None
    except sqlite3.Error as exc:  # includes syntax errors and constraint issues
        return None, str(exc)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def _predict_code(setup: str, query: str) -> str:
    return f"{setup.rstrip()}\n\n{PREDICT_MARKER}\n{query}\n"


def split_predict_code(code: str) -> tuple[str, str]:
    """Split a shipped Predict Output snippet into (setup, query)."""
    marker = f"\n{PREDICT_MARKER}\n"
    idx = code.index(marker)
    setup = code[:idx]
    query = code[idx + len(marker):].strip()
    return setup, query


def _display_query(query: str, broken_line: str) -> tuple[str, int]:
    """Insert the marker comment above the broken line; return (code, line_no)."""
    lines = query.split("\n")
    needle = broken_line.strip()
    matches = [i for i, ln in enumerate(lines) if needle in ln.strip()]
    if len(matches) != 1:
        raise ValueError(f"broken line {broken_line!r} matched {len(matches)} lines")
    idx = matches[0]
    raw = lines[idx]
    indent = raw[: len(raw) - len(raw.lstrip())]
    marker = f"{indent}{BUG_MARKER}: {raw.strip()}"
    lines.insert(idx, marker)
    return "\n".join(lines), idx + 2  # 1-based line number of the broken line


def _place_options(correct: str, distractors: list[str], idx: int) -> tuple[list[str], int]:
    """Deterministically place the correct option so it spreads across indices."""
    if correct in distractors:
        raise ValueError("the correct option is duplicated among the distractors")
    if len(set(distractors)) != len(distractors):
        raise ValueError("duplicate distractor")
    n = len(distractors) + 1
    target = (idx * 3 + 1) % n
    rest = list(distractors)
    ordered = rest[:target] + [correct] + rest[target:]
    return ordered, target


def verify_predict(setup: str, query: str, expected: str) -> None:
    got, err = execute_sql(setup, query)
    if err is not None:
        raise ValueError(f"Predict Output query failed to run: {err}")
    if got != expected:
        raise ValueError(f"Predict Output key mismatch: stated {expected!r}, sqlite gave {got!r}")


def verify_find_the_bug(
    setup: str,
    query: str,
    broken_line: str,
    correct: str,
    distractors: list[str],
    expected: str,
) -> None:
    """Prove the correct option works and every other option is genuinely wrong."""
    if query.count(broken_line) != 1:
        raise ValueError(f"broken line must occur exactly once: {broken_line!r}")

    fixed = query.replace(broken_line, correct)
    got, err = execute_sql(setup, fixed)
    if err is not None:
        raise ValueError(f"correct option does not run: {err}")
    if got != expected:
        raise ValueError(f"intended result mismatch: stated {expected!r}, sqlite gave {got!r}")

    bad, berr = execute_sql(setup, query)
    if berr is None and bad == expected:
        raise ValueError("the unfixed query already produces the intended result; not a bug")

    for distractor in distractors:
        if distractor == correct:
            raise ValueError("distractor equals the correct option")
        dgot, derr = execute_sql(setup, query.replace(broken_line, distractor))
        if derr is None and dgot == expected:
            raise ValueError(f"distractor is silently correct: {distractor!r}")


def build_predict_output() -> list[dict]:
    out: list[dict] = []
    for topic, difficulty, setup, query, expected in PREDICT_OUTPUT:
        verify_predict(setup, query, expected)
        out.append(
            {
                "id": None,
                "question_type": "Coding",
                "format": "Predict Output",
                "language": LANGUAGE,
                "difficulty": difficulty,
                "category": CATEGORY,
                "topic": topic,
                "question_text": (
                    "What does this SQL query return? Give one value per column, "
                    "joined with ' | '."
                ),
                "code": _predict_code(setup, query),
                "accepted_answers": [expected],
                "time_limit": TIME_LIMIT,
                "_setup": setup,
                "_query": query,
            }
        )
    return out


def build_find_the_bug() -> list[dict]:
    out: list[dict] = []
    for idx, (
        topic, difficulty, intent, setup, query, broken, correct, distractors, expected
    ) in enumerate(FIND_THE_BUG):
        verify_find_the_bug(setup, query, broken, correct, distractors, expected)
        code, line_no = _display_query(query, broken)
        options, correct_index = _place_options(correct, distractors, idx)
        out.append(
            {
                "id": None,
                "question_type": "Coding",
                "format": "Find the Bug",
                "language": LANGUAGE,
                "difficulty": difficulty,
                "category": CATEGORY,
                "topic": topic,
                "question_text": (
                    f"{intent}. The SQL query below is wrong: line {line_no} does not "
                    "work. Which line should replace it to fix it?"
                ),
                "code": code,
                "options": [{"index": i, "text": t} for i, t in enumerate(options)],
                "correct_answer_index": correct_index,
                "time_limit": TIME_LIMIT,
                "_setup": setup,
                "_query": query,
                "_broken": broken,
                "_correct": correct,
                "_distractors": distractors,
                "_expected": expected,
            }
        )
    return out


def assign_ids(questions: list[dict]) -> None:
    for i, q in enumerate(questions, start=1):
        q["id"] = f"NEX_SQL_{i:03d}"


def build_all() -> list[dict]:
    questions = build_predict_output() + build_find_the_bug()
    assign_ids(questions)
    return questions


# ---------------------------------------------------------------------------
# Verification of a shipped JSON file
# ---------------------------------------------------------------------------
def _authored_find_specs() -> dict[str, tuple]:
    """Find-the-Bug specs keyed by the id ``build_all`` would assign them."""
    base = len(PREDICT_OUTPUT)
    return {f"NEX_SQL_{base + i + 1:03d}": spec for i, spec in enumerate(FIND_THE_BUG)}


def verify_authored(questions: list[dict]) -> list[str]:
    """Re-run every answer key by execution; return error strings."""
    errors: list[str] = []
    specs = _authored_find_specs()
    for q in questions:
        qid = q.get("id", "?")
        try:
            if q.get("format") == "Predict Output":
                setup, query = split_predict_code(q["code"])
                verify_predict(setup, query, q["accepted_answers"][0])
            elif q.get("format") == "Find the Bug":
                spec = specs.get(qid)
                if spec is None:
                    errors.append(f"{qid}: no authored Find-the-Bug spec to verify against")
                    continue
                (topic, difficulty, intent, setup, query,
                 broken, correct, distractors, expected) = spec
                verify_find_the_bug(setup, query, broken, correct, distractors, expected)
                shipped = q["options"][q["correct_answer_index"]]["text"]
                if shipped != correct:
                    errors.append(
                        f"{qid}: shipped correct option {shipped!r} != authored {correct!r}"
                    )
                if {o["text"] for o in q["options"]} != {correct, *distractors}:
                    errors.append(f"{qid}: shipped options do not match the authored set")
        except (ValueError, KeyError, IndexError) as exc:
            errors.append(f"{qid}: verification failed: {exc}")
    return errors


# ---------------------------------------------------------------------------
# Contract validation
# ---------------------------------------------------------------------------
def validate(questions: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for q in questions:
        qid = q.get("id", "<missing id>")

        def bad(msg: str, qid=qid) -> None:
            errors.append(f"{qid}: {msg}")

        if not qid or qid in seen_ids:
            bad("duplicate or missing id")
        seen_ids.add(qid)
        if qid != f"NEX_SQL_{len(seen_ids):03d}":
            bad("id is not sequential / zero-padded")
        if q.get("question_type") != "Coding":
            bad("question_type must be Coding")
        fmt = q.get("format")
        if fmt not in FORMATS:
            bad(f"bad format {fmt!r}")
        if q.get("language") != LANGUAGE:
            bad(f"language must be {LANGUAGE!r}")
        if q.get("difficulty") not in DIFFICULTIES:
            bad(f"bad difficulty {q.get('difficulty')!r}")
        if q.get("category") != CATEGORY:
            bad(f"category must be {CATEGORY!r}")
        if "sql" not in str(q.get("category", "")).lower():
            bad("category must contain the substring 'sql'")
        for field in ("question_text", "code", "topic"):
            if not str(q.get(field) or "").strip():
                bad(f"empty {field}")
        if q.get("time_limit") != TIME_LIMIT:
            bad("time_limit must be 300")
        if not any(k in str(q.get("question_text", "")).lower() for k in PROFILE_KEYWORDS):
            bad("question_text lacks an sql-profile keyword")

        if fmt == "Predict Output":
            answers = q.get("accepted_answers") or []
            if len(answers) != 1 or not str(answers[0]).strip():
                bad("Predict Output needs exactly one non-empty answer")
            if "options" in q:
                bad("Predict Output must not carry options")
            if q.get("code", "").count(PREDICT_MARKER) != 1:
                bad("Predict Output needs exactly one predict marker")
        elif fmt == "Find the Bug":
            options = q.get("options") or []
            if len(options) < 3:
                bad("Find the Bug needs >= 3 options")
            if [o.get("index") for o in options] != list(range(len(options))):
                bad("option indices must be 0..n-1 in order")
            texts = [o.get("text", "") for o in options]
            if len(set(texts)) != len(texts):
                bad("duplicate option text")
            cai = q.get("correct_answer_index")
            if not isinstance(cai, int) or not (0 <= cai < len(options)):
                bad("correct_answer_index out of range")
            if "accepted_answers" in q:
                bad("Find the Bug must not carry accepted_answers")
            if q.get("code", "").count(BUG_MARKER) != 1:
                bad("Find the Bug needs exactly one marked-line comment")
    return errors


# ---------------------------------------------------------------------------
# Reporting / CLI
# ---------------------------------------------------------------------------
def print_report(questions: list[dict]) -> None:
    print("\nper-format counts")
    for fmt in FORMATS:
        print(f"  {fmt:<16} {sum(1 for q in questions if q['format'] == fmt)}")
    print(f"  {'TOTAL':<16} {len(questions)}")

    print("\nper-difficulty counts")
    for diff in DIFFICULTIES:
        print(f"  {diff:<16} {sum(1 for q in questions if q['difficulty'] == diff)}")

    print("\nper-format x per-difficulty")
    header = "difficulty".ljust(12) + "".join(f.ljust(16) for f in FORMATS) + "total"
    print(header)
    for diff in DIFFICULTIES:
        row = [
            str(sum(1 for q in questions if q["difficulty"] == diff and q["format"] == f)).ljust(16)
            for f in FORMATS
        ]
        total = sum(1 for q in questions if q["difficulty"] == diff)
        print(diff.ljust(12) + "".join(row) + str(total))


def _report_validation(errors: list[str], data: list[dict]) -> None:
    if errors:
        print(f"validation FAILED with {len(errors)} error(s):", file=sys.stderr)
        for err in errors[:40]:
            print(f"  - {err}", file=sys.stderr)
    else:
        fmt_counts = {f: sum(1 for q in data if q.get("format") == f) for f in FORMATS}
        print(f"validation passed for {len(data)} questions: {fmt_counts}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(_MODELS / "coding_bank_sql.json"))
    ap.add_argument("--validate", action="store_true",
                    help="validate the file at --out and exit")
    args = ap.parse_args()

    if args.validate:
        data = json.loads(Path(args.out).read_text(encoding="utf-8"))
        errors = validate(data) + verify_authored(data)
        _report_validation(errors, data)
        return 1 if errors else 0

    questions = build_all()
    errors = validate(questions) + verify_authored(questions)
    if errors:
        print(f"validation FAILED with {len(errors)} error(s):", file=sys.stderr)
        for err in errors[:40]:
            print(f"  - {err}", file=sys.stderr)
        return 1

    payload = [{k: v for k, v in q.items() if not k.startswith("_")} for q in questions]
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"validation passed for {len(questions)} questions "
          "(all Predict Output keys and Find-the-Bug keys verified in sqlite3)")
    print_report(questions)
    print(f"\nwrote {len(payload)} questions -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
