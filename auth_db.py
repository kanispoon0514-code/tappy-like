# auth_db.py
import sqlite3
from pathlib import Path
import bcrypt
from typing import Optional, Tuple

DB_FILE = Path("reservations.sqlite3")

def _ensure_users(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        pass_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin','user')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

def init_user_db():
    with sqlite3.connect(DB_FILE) as conn:
        _ensure_users(conn)

def admin_exists() -> bool:
    with sqlite3.connect(DB_FILE) as conn:
        _ensure_users(conn)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1")
        return cur.fetchone() is not None

def create_user(username: str, password: str, role: str = "user") -> Tuple[bool, str]:
    if not username or not password:
        return False, "ユーザー名とパスワードは必須です。"
    if role not in ("admin", "user"):
        return False, "role は admin か user を指定してください。"

    # ★ 管理者は1人だけ：既にadminがいるなら admin 追加を拒否
    if role == "admin" and admin_exists():
        return False, "管理者は既に存在します。"

    try:
        with sqlite3.connect(DB_FILE) as conn:
            _ensure_users(conn)
            ph = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            conn.execute(
                "INSERT INTO users (username, pass_hash, role) VALUES (?, ?, ?)",
                (username, ph, role)
            )
            conn.commit()
        return True, "作成しました。"
    except sqlite3.IntegrityError:
        return False, "そのユーザー名は既に存在します。"

def verify_login(username: str, password: str) -> Tuple[bool, str, Optional[str]]:
    with sqlite3.connect(DB_FILE) as conn:
        _ensure_users(conn)
        cur = conn.cursor()
        cur.execute("SELECT pass_hash, role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            return False, "ユーザーが見つかりません。", None
        ph, role = row
        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), ph.encode("utf-8"))
        except Exception:
            ok = False
        if not ok:
            return False, "パスワードが違います。", None
        return True, "OK", role