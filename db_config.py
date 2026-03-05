"""
db_config.py — MySQL connection helper for Sobkaj.

Environment-aware (checked in order):
  1. MYSQL_URL   → Railway MySQL plugin
  2. JAWSDB_URL  → JawsDB / legacy Heroku add-on
  3. Local XAMPP → development fallback (root, no password)

All cloud URLs follow the DSN format:
    mysql://user:password@host:port/database

Uses mysql-connector-python (no ORM).
"""

import os
from urllib.parse import urlparse

import mysql.connector
from mysql.connector import Error


def _build_db_config() -> dict:
    """
    Return a mysql-connector-python config dict.

    Priority:
    1. MYSQL_URL   environment variable  (Railway)
    2. JAWSDB_URL  environment variable  (JawsDB)
    3. Hard-coded local XAMPP defaults   (development)
    """
    dsn = os.environ.get("MYSQL_URL") or os.environ.get("JAWSDB_URL")

    if dsn:
        # Parse  mysql://user:password@host:port/dbname
        parsed = urlparse(dsn)
        return {
            "host":     parsed.hostname,
            "user":     parsed.username,
            "password": parsed.password,
            "database": parsed.path.lstrip("/"),
            "port":     parsed.port or 3306,
        }

    # ── Local XAMPP fallback ──────────────────────────────────
    return {
        "host":     "localhost",
        "user":     "root",
        "password": "",        # XAMPP default — no password
        "database": "sobkaj",
    }


DB_CONFIG = _build_db_config()


def get_db_connection():
    """
    Open and return a new MySQL connection.

    The caller is responsible for calling connection.close()
    when finished.  Example usage:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[DB ERROR] Failed to connect to MySQL: {e}")
        return None
