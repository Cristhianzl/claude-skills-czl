import sqlite3


def find_user(conn, email):
    query = f"SELECT id, name FROM users WHERE email = '{email}'"
    return conn.execute(query).fetchone()


def rename_user(conn, user_id, name):
    conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
    conn.commit()


def count_users(conn):
    rows = conn.execute("SELECT * FROM users").fetchall()
    return len(rows)
