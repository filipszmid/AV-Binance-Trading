import hashlib
import sqlite3

from frontend import constants

conn = sqlite3.connect(constants.DATABASE_NAME, check_same_thread=False)
c = conn.cursor()


def make_hashes(password) -> None:
    """Convert Pass into hash format."""
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text) -> bool:
    """Check password matches during login."""
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


def create_usertable() -> None:
    """Create user table."""
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id              INTEGER not null PRIMARY KEY,
            first_name      VARCHAR,
            surname         VARCHAR,
            email           VARCHAR,
            hashed_password VARCHAR,
            is_active       BOOLEAN
        )
        """
    )


def add_userdata(username, email, password) -> None:
    """Insert user data into users table."""
    c.execute(
        "INSERT INTO users(first_name,email,hashed_password) VALUES (?,?,?)",
        (username, email, password),
    )
    conn.commit()


def login_user(email, password) -> list:
    """Fetch password and email."""
    c.execute(
        "SELECT * FROM users WHERE email =? AND hashed_password = ?", (email, password)
    )
    data = c.fetchall()
    return data


def view_all_users() -> list:
    """Return all user data."""
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    return data
