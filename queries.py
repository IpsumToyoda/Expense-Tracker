import psycopg2
from psycopg2.extras import RealDictCursor

from db import db_connection


def add_expense(title, amount, category=None, expense_date=None, notes=None):
    """Insert a new expense record into the database."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO expenses (title, amount, category, expense_date, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, title, amount, category, expense_date, notes, created_at;
                """,
                (title, amount, category, expense_date, notes),
            )
            expense = cur.fetchone()
        conn.commit()
    return expense


def get_categories():
    """Return a sorted list of distinct categories."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT category
                FROM expenses
                WHERE category IS NOT NULL AND category <> ''
                ORDER BY category;
                """
            )
            return [row["category"] for row in cur.fetchall()]


def get_expenses(
    limit=200,
    category=None,
    start_date=None,
    end_date=None,
    min_amount=None,
    max_amount=None,
):
    """Return recent expenses filtered by category, date range, and amount."""
    query_parts = [
        "SELECT id, title, amount, category, expense_date, notes, created_at",
        "FROM expenses",
    ]
    conditions = []
    params = []

    if category:
        conditions.append("category = %s")
        params.append(category)

    if start_date is not None:
        conditions.append("expense_date >= %s")
        params.append(start_date)

    if end_date is not None:
        conditions.append("expense_date <= %s")
        params.append(end_date)

    if min_amount is not None:
        conditions.append("amount >= %s")
        params.append(min_amount)

    if max_amount is not None:
        conditions.append("amount <= %s")
        params.append(max_amount)

    if conditions:
        query_parts.append("WHERE " + " AND ".join(conditions))

    query_parts.append("ORDER BY expense_date DESC, created_at DESC")
    query_parts.append("LIMIT %s")
    params.append(limit)

    final_query = "\n".join(query_parts) + ";"

    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(final_query, tuple(params))
            return cur.fetchall()


def get_expense_total(
    category=None,
    start_date=None,
    end_date=None,
    min_amount=None,
    max_amount=None,
):
    """Return the total expense amount for filtered records."""
    query_parts = ["SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"]
    conditions = []
    params = []

    if category:
        conditions.append("category = %s")
        params.append(category)

    if start_date is not None:
        conditions.append("expense_date >= %s")
        params.append(start_date)

    if end_date is not None:
        conditions.append("expense_date <= %s")
        params.append(end_date)

    if min_amount is not None:
        conditions.append("amount >= %s")
        params.append(min_amount)

    if max_amount is not None:
        conditions.append("amount <= %s")
        params.append(max_amount)

    if conditions:
        query_parts.append("WHERE " + " AND ".join(conditions))

    final_query = "\n".join(query_parts) + ";"

    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(final_query, tuple(params))
            result = cur.fetchone()
            return result["total"]


def delete_expense(expense_id):
    """Delete an expense record by its ID."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "DELETE FROM expenses WHERE id = %s;",
                (expense_id,),
            )
        conn.commit()


def get_expense_by_id(expense_id):
    """Return a single expense record by its ID."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, title, amount, category, expense_date, notes, created_at FROM expenses WHERE id = %s;",
                (expense_id,),
            )
            return cur.fetchone()


def update_expense(expense_id, title, amount, category=None, expense_date=None, notes=None):
    """Update an existing expense record."""
    with db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE expenses
                SET title = %s,
                    amount = %s,
                    category = %s,
                    expense_date = %s,
                    notes = %s
                WHERE id = %s;
                """,
                (title, amount, category, expense_date, notes, expense_id),
            )
        conn.commit()
