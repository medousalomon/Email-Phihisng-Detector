import sqlite3
import bcrypt


DB_PATH = "database/history.db"


# -------------------------
# CREATE USER TABLE
# -------------------------

def initialize_users():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            password BLOB,

            role TEXT DEFAULT 'user'

        )

    """)

    conn.commit()

    conn.close()


# -------------------------
# REGISTER USER
# -------------------------

def register_user(username, password):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    role = "admin" if user_count == 0 else "user"

    try:

        cursor.execute("""

            INSERT INTO users (
                username,
                password,
                role
            )

            VALUES (?, ?, ?)

        """, (
            username,
            hashed,
            role
        ))

        conn.commit()

        return True

    except:

        return False

    finally:

        conn.close()


# -------------------------
# LOGIN USER
# -------------------------

def login_user(username, password):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT password
        FROM users
        WHERE username=?

    """, (username,))

    result = cursor.fetchone()

    conn.close()

    if result:

        stored_password = result[0]

        return bcrypt.checkpw(
            password.encode(),
            stored_password
        )

    return False


def change_password(username, old_password, new_password):

    if not login_user(username, old_password):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_hashed = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    )

    cursor.execute("""

        UPDATE users
        SET password=?
        WHERE username=?

    """, (
        new_hashed,
        username
    ))

    conn.commit()
    conn.close()

    return True


def delete_user(username, password):

    if not login_user(username, password):
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM users
        WHERE username=?

    """, (
        username,
    ))

    conn.commit()
    conn.close()

    return True


def get_user_role(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""

        SELECT role
        FROM users
        WHERE username=?

    """, (
        username,
    ))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return "user"


def initialize_sessions():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_sessions (
            username TEXT PRIMARY KEY,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()

def get_all_users():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, role
        FROM users
        ORDER BY id ASC
    """)

    users = cursor.fetchall()

    conn.close()

    return users


def admin_delete_user(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE username=?
    """, (username,))

    cursor.execute("""
        DELETE FROM scans
        WHERE username=?
    """, (username,))

    conn.commit()
    conn.close()

    return True


def activate_session(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO active_sessions (
            username,
            is_active
        )
        VALUES (?, 1)
    """, (username,))

    conn.commit()
    conn.close()


def deactivate_session(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE active_sessions
        SET is_active=0
        WHERE username=?
    """, (username,))

    conn.commit()
    conn.close()


def is_session_active(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_active
        FROM active_sessions
        WHERE username=?
    """, (username,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return False

    return result[0] == 1