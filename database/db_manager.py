import sqlite3


DB_PATH = "database/history.db"


# -------------------------
# CREATE DATABASE
# -------------------------

def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            prediction TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )

    """)

    conn.commit()

    conn.close()


# -------------------------
# SAVE SCAN
# -------------------------

def save_scan(username, email, prediction, confidence):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO scans (
            username,
            email,
            prediction,
            confidence
        )

        VALUES (?, ?, ?, ?)

    """, (
        username,
        email,
        prediction,
        float(confidence)
    ))

    conn.commit()
    conn.close()


# -------------------------
# GET HISTORY
# -------------------------

def get_history(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""

        SELECT id, email, prediction, confidence, timestamp
        FROM scans
        WHERE username=?
        ORDER BY timestamp DESC

    """, (
        username,))

    rows = cursor.fetchall()

    conn.close()

    return rows

# -------------------------
# GET STATISTICS
# -------------------------

def get_statistics(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM scans WHERE username=?",
        (username,)
    )

    total_scans = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM scans
        WHERE prediction='PHISHING' AND username=?
    """, (username,))

    phishing_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM scans
        WHERE prediction='LEGITIMATE' AND username=?
    """, (username,))

    legitimate_count = cursor.fetchone()[0]

    conn.close()

    phishing_percentage = (
        phishing_count / total_scans * 100
        if total_scans > 0
        else 0
    )

    return {
        "total": total_scans,
        "phishing": phishing_count,
        "legitimate": legitimate_count,
        "phishing_percentage": phishing_percentage
    }



# -------------------------
# GET DAILY SCAN TREND
# -------------------------

def get_daily_scan_trend():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            DATE(timestamp) as scan_date,

            COUNT(*) as total_scans

        FROM scans

        GROUP BY DATE(timestamp)

        ORDER BY scan_date

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# -------------------------
# DELETE USER SCAN HISTORY
# -------------------------

def clear_user_history(username):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM scans
        WHERE username=?

    """, (
        username,
    ))

    conn.commit()

    conn.close()

    return True


# -------------------------
# GLOBAL ADMIN STATISTICS
# -------------------------

def get_global_statistics():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM scans"
    )

    total_scans = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM scans WHERE prediction='PHISHING'"
    )

    phishing_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM scans WHERE prediction='LEGITIMATE'"
    )

    legitimate_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT username) FROM scans"
    )

    active_users = cursor.fetchone()[0]

    conn.close()

    phishing_percentage = (

        phishing_count / total_scans * 100

        if total_scans > 0

        else 0
    )

    return {

        "total": total_scans,

        "phishing": phishing_count,

        "legitimate": legitimate_count,

        "active_users": active_users,

        "phishing_percentage": phishing_percentage
    }