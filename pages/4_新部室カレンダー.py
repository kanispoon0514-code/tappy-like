# pages/3_旧部室カレンダー.py
import streamlit as st
import reservation_db as rdb
from datetime import date, datetime, timedelta
import calendar
from streamlit_calendar import calendar as st_calendar

# ページ設定は最初に
st.set_page_config(page_title="旧部室カレンダー", layout="wide")

with st.sidebar:
    user = st.session_state.get("user")
    role = st.session_state.get("role")
    if user:
        st.caption(f"ログイン中：{user}（{role}）")
        if st.button("ログアウト", key="logout_global"):
            st.session_state["user"] = None
            st.session_state["role"] = None
            # ログアウト後はログインページへ（対応していない場合は rerun）
            try:
                st.switch_page("pages/0_ログイン.py")
            except Exception:
                st.rerun()

ROOM_KEY = "new"  # new ページは "new" にする
ROOM_LABEL = {"old": "旧部室", "new": "新部室"}
SLOTS = ["朝","1限", "2限","昼休み", "3限", "4限", "5限","6限","夜"]
SLOT_TIMES = {
    "朝": ("05:00:00", "08:50:00"),
    "1限": ("08:50:00", "10:20:00"),
    "2限": ("10:30:00", "12:00:00"),
    "昼休み": ("12:00:00", "12:50:00"),
    "3限": ("12:50:00", "14:20:00"),
    "4限": ("14:30:00", "16:00:00"),
    "5限": ("16:10:00", "17:40:00"),
    "6限": ("17:50:00", "19:20:00"),
    "夜": ("19:30:00", "22:00:00"),

# ---- helpers ----
def month_bounds(any_day: date):
    first = any_day.replace(day=1)
    last_day = calendar.monthrange(first.year, first.month)[1]
    last = any_day.replace(day=last_day)
    return first, last

def ymd(d: date) -> str:
    return d.strftime("%Y-%m-%d")

def fetch_day_summary(room: str, d: date):
    """その日の予約（枠ごとに誰が入っているか）を辞書で返す"""
    rows = rdb.get_reservations_between(room, ymd(d), ymd(d))
    who_by_slot = {slot: None for slot in SLOTS}
    for r in rows:
        sl = r.get("slot")
        if sl in who_by_slot:
            # name は表示名、owner は内部ユーザー名（必要なら r["owner"] も利用可）
            who_by_slot[sl] = r.get("name")
    count = sum(1 for v in who_by_slot.values() if v)
    return who_by_slot, count

def mk_events(room_key: str, month_first: date, month_last: date):
    rows = rdb.get_reservations_between(room_key, month_first.isoformat(), month_last.isoformat())
    evs = []
    color = "#f97316" if room_key == "old" else "#3b82f6"
    for r in rows:
        d = r["date"]; s = r["slot"]; who = r["name"]
        t0, t1 = SLOT_TIMES.get(s, ("09:00:00","10:00:00"))
        evs.append({
            "title": f"{s} {who}",
            "start": f"{d}T{t0}",
            "end":   f"{d}T{t1}",
            "allDay": False,
            "backgroundColor": color,
            "borderColor": color
        })
    return evs

def _extract_clicked_date(ret: dict) -> date | None:
    if not ret:
        return None
    cb = ret.get("callback")
    raw = None
    if cb == "dateClick":
        dc = ret.get("dateClick") or {}
        raw = dc.get("dateStr") or dc.get("date")
    elif cb == "select":
        sel = ret.get("select") or {}
        raw = sel.get("startStr") or sel.get("start")
    if not raw:
        return None
    try:
        # ISO 文字列に時間や Z が含まれる場合は JST(+9h) に補正
        if "T" in raw or raw.endswith("Z"):
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return (dt + timedelta(hours=9)).date()
        return date.fromisoformat(raw[:10])
    except Exception:
        return None

# ---- guard: 要ログイン ----
if "user" not in st.session_state or not st.session_state["user"]:
    st.error("このページはログインが必要です。左の「ログイン」ページからログインしてください。")
    st.stop()

current_user = st.session_state["user"]
is_admin = (st.session_state.get("role") == "admin")

st.title(f"📅 {ROOM_LABEL[ROOM_KEY]} 月ビュー")
rdb.init_db()

today = date.today()
PM_KEY = f"picked_month_{ROOM_KEY}"
SD_KEY = f"selected_day_{ROOM_KEY}"

with st.sidebar:
    if PM_KEY not in st.session_state:
        st.session_state[PM_KEY] = today.replace(day=1)
    picked = st.date_input(
        "月の基準日（その月を表示）",
        value=st.session_state[PM_KEY],
        format="YYYY-MM-DD",
        key=f"picked_month_input_{ROOM_KEY}"
    )
    st.session_state[PM_KEY] = picked.replace(day=1)

    c_prev, c_next = st.columns(2)
    with c_prev:
        if st.button("◀ 前月", key=f"prev_{ROOM_KEY}"):
            first, _ = month_bounds(st.session_state[PM_KEY])
            st.session_state[PM_KEY] = (first - timedelta(days=1)).replace(day=1)
            st.rerun()
    with c_next:
        if st.button("次月 ▶", key=f"next_{ROOM_KEY}"):
            first, last = month_bounds(st.session_state[PM_KEY])
            st.session_state[PM_KEY] = (last + timedelta(days=1)).replace(day=1)
            st.rerun()

display_name = st.text_input("画面表示用の名前（相手に見える名前）", value=current_user)

if SD_KEY not in st.session_state:
    st.session_state[SD_KEY] = today

month_first, month_last = month_bounds(st.session_state[PM_KEY])
ym_key = st.session_state[PM_KEY].strftime("%Y%m")

cal_opts = {
    "initialView": "dayGridMonth",
    "firstDay": 0,  # 日曜始まり
    "headerToolbar": {"left": "today prev,next", "center": "title", "right": ""},
    "height": 720,
    "locale": "ja",
    "dayMaxEventRows": True,
    "selectable": True,
}

events = mk_events(ROOM_KEY, month_first, month_last)
ret = st_calendar(events=events, options=cal_opts, key=f"cal_{ROOM_KEY}_{ym_key}")
clicked = _extract_clicked_date(ret)
if clicked and clicked != st.session_state[SD_KEY]:
    st.session_state[SD_KEY] = clicked
    st.rerun()

sel_day = st.session_state[SD_KEY]
st.subheader(f"🗓 {ROOM_LABEL[ROOM_KEY]}: {sel_day.strftime('%Y-%m-%d')} の予約")

who_by_slot, _ = fetch_day_summary(ROOM_KEY, sel_day)
cols = st.columns(len(SLOTS))
for i, s in enumerate(SLOTS):
    with cols[i]:
        who = who_by_slot[s]

        def card(html_body, bg="#ffffff"):
            st.markdown(
                f"""
                <div style="border:1px solid #e5e7eb; padding:10px; border-radius:10px; background:{bg}; text-align:center;">
                  {html_body}
                </div>
                """,
                unsafe_allow_html=True
            )

        base_key = f"{ROOM_KEY}|{ymd(sel_day)}|{s}"
        if who:
            # 予約済み：所有者 or 管理者のみキャンセル可
            if st.button(f"{s} の予約をキャンセル", key=f"cancel_btn|{base_key}"):
                ok, msg = rdb.cancel_slot_if_allowed(
                    ROOM_KEY, ymd(sel_day), s,
                    requester=current_user, is_admin=is_admin
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            card(f"<b>{s}</b><br>× 予約済（{who}）", bg="#f1f5f9")
        else:
            if st.button(f"{s} を予約", key=f"reserve_btn|{base_key}"):
                if not display_name.strip():
                    st.warning("表示名を入力してください。")
                else:
                    ok, msg = rdb.reserve_slot(
                        ROOM_KEY, ymd(sel_day), s,
                        display_name.strip(), owner=current_user
                    )
                    if ok:
                        st.success(f"{ROOM_LABEL[ROOM_KEY]} {ymd(sel_day)} {s} の予約が完了しました。")
                        st.rerun()
                    else:
                        st.error(msg)
            card(f"<b>{s}</b><br>○ 空き", bg="#ecfeff")
