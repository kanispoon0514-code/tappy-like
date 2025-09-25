# reservation_db.py
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

DB_FILE = Path("reservations.sqlite3")

def _ensure_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        room TEXT,
        date TEXT,
        slot TEXT,
        name TEXT,
        owner TEXT,                 -- ログインユーザー名
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (room, date, slot)
    )
    """)
    # 既存DBに owner が無ければ足す
    cur.execute("PRAGMA table_info(reservations)")
    cols = [c[1] for c in cur.fetchall()]
    if "owner" not in cols:
        cur.execute("ALTER TABLE reservations ADD COLUMN owner TEXT")
    conn.commit()

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        _ensure_schema(conn)

def get_reservations_between(room: str, start_date: str, end_date: str) -> List[Dict]:
    with sqlite3.connect(DB_FILE) as conn:
        _ensure_schema(conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT room, date, slot, name, owner FROM reservations "
            "WHERE room=? AND date BETWEEN ? AND ? ORDER BY date, slot",
            (room, start_date, end_date)
        )
        rows = cur.fetchall()
    return [{"room": r, "date": d, "slot": s, "name": n, "owner": o} for (r, d, s, n, o) in rows]

def reserve_slot(room: str, d: str, slot: str, display_name: str, owner: str) -> Tuple[bool, str]:
    try:
        with sqlite3.connect(DB_FILE) as conn:
            _ensure_schema(conn)
            conn.execute(
                "INSERT INTO reservations (room, date, slot, name, owner) VALUES (?, ?, ?, ?, ?)",
                (room, d, slot, display_name, owner)
            )
            conn.commit()
        return True, "OK"
    except sqlite3.IntegrityError:
        return False, "既に予約があります"

def cancel_slot_if_allowed(room: str, d: str, slot: str, requester: str, is_admin: bool) -> Tuple[bool, str]:
    with sqlite3.connect(DB_FILE) as conn:
        _ensure_schema(conn)
        cur = conn.cursor()
        cur.execute("SELECT owner FROM reservations WHERE room=? AND date=? AND slot=?", (room, d, slot))
        row = cur.fetchone()
        if not row:
            return False, "予約が見つかりません"
        owner = row[0]
        if not is_admin and requester != owner:
            return False, "この予約を変更する権限がありません"
        cur.execute("DELETE FROM reservations WHERE room=? AND date=? AND slot=?", (room, d, slot))
        conn.commit()
        return (cur.rowcount > 0), ("キャンセルしました。" if cur.rowcount > 0 else "キャンセルできませんでした。")

# 管理者ページ用（無条件キャンセルが必要なら）
def admin_cancel(room: str, d: str, slot: str) -> Tuple[bool, str]:
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM reservations WHERE room=? AND date=? AND slot=?", (room, d, slot))
        conn.commit()
        return (cur.rowcount > 0), ("キャンセルしました（管理者）。" if cur.rowcount > 0 else "対象がありません")
