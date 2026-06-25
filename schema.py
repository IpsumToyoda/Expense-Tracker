from db import db_connection


def create_tables():
    """Create the expense schema if it does not already exist."""
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
                    category TEXT,
                    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
                """
            )
        conn.commit()
