import sqlite3
from flask import g

DATABASE = "expense_tracker.db"


def get_db():
    """Return a SQLite connection with row_factory and foreign keys enabled."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables using CREATE TABLE IF NOT EXISTS."""
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_expenses_user_date
            ON expenses(user_id, date);
        """
    )
    db.commit()


def seed_db():
    """Insert sample data for development."""
    db = get_db()

    # Only seed if the tables are empty.
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return

    from werkzeug.security import generate_password_hash

    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Nitish Kumar", "nitish@example.com", generate_password_hash("password123")),
    )
    db.commit()

    user_id = db.execute("SELECT id FROM users WHERE email = ?", ("nitish@example.com",)).fetchone()["id"]

    sample_expenses = [
        ("Bills", 4500.00, "2026-03-05", "Electricity bill"),
        ("Food", 3200.00, "2026-03-10", "Groceries"),
        ("Health", 2050.00, "2026-03-12", "Medicines"),
        ("Transport", 1800.00, "2026-03-14", "Monthly pass"),
        ("Food", 850.00, "2026-03-18", "Dining out"),
        ("Bills", 1200.00, "2026-03-20", "Internet bill"),
    ]
    db.executemany(
        "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
        [(user_id, cat, amt, date, desc) for cat, amt, date, desc in sample_expenses],
    )
    db.commit()
