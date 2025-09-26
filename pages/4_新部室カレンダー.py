# pages/3_旧部室カレンダー.py
import streamlit as st
import reservation_db as rdb
from datetime import date, datetime, timedelta
import calendar
from streamlit_calendar import calendar as st_calendar

import style
style.load_css()

st.markdown("""
<style>
/* --- 共通: イベントカードをコンパクトに --- */
.fc .fc-daygrid-event {
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 8px !important;
  padding: 4px 6px !important;
}

/* 3x3タイル（絵文字）用。改行を効かせて中央寄せ */
.fc .fc-daygrid-event .fc-event-title {
  white-space: pre;
  text-align: center;
  line-height: 1.05;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono",
               "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji", monospace !important;
  font-size: 16px;  /* デスクトップ標準 */
}

/* 今日のセルの軽いハイライト（任意） */
.fc .fc-daygrid-day.fc-day-today { background: #fffbea !important; }

/* --- モバイル幅向け（～640px）での最適化 --- */
@media (max-width: 640px) {
  /* カレンダーのイベントをさらに凝縮 */
  .fc .fc-daygrid-event { padding: 2px 4px !important; }

  /* タイルの文字を自動縮小（10～14pxの範囲で可変） */
  .fc .fc-daygrid-event .fc-event-title {
    font-size: clamp(10px, 3.2vw, 14px);
    line-height: 1.0;
    letter-spacing: 0; /* 絵文字のズレ防止 */
  }

  /* 日付番号の文字を少し小さく */
  .fc .fc-daygrid-day-top .fc-daygrid-day-number { font-size: 12px; }

  /* 1日セルの最低高さを少し確保（折返しで潰れにくく） */
  .fc .fc-daygrid-day-frame { min-height: 72px; }
}
</style>
""", unsafe_allow_html=True)

# ========================
# ページ設定は最初に
# ========================
st.set_page_config(page_title="旧部室カレンダー", layout="wide")

# ---------- サイドバー：ログイン状態 ----------
with st.sidebar:
    user = st.session_state.get("user")
    role = st.session_state.get("role")
    if user:
        st.caption(f"ログイン中：{user}（{role}）")
        if st.button("ログアウト", key="logout_global"):
            st.session_state["user"] = None
            st.session_state["role"] = None
            try:
                st.switch_page("pages/0_ログイン.py")
            except Exception:
                st.rerun()

# ---------- 定数 ----------
ROOM_KEY = "new"  # new ページは "new" にする
ROOM_LABEL = {"old": "旧部室", "new": "新部室"}
SLOTS = ["朝","1限", "2限","昼休み", "3限", "4限", "5限","6限","夜"]
NINE_SLOTS = ["朝","1限","2限","昼休み","3限","4限","5限","6限","夜"]

# （参考）時間帯を使う箇所があれば利用
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
}

# ========================
# スタイル（タイル用の最適化）
# ========================
st.markdown("""
<style>
/* ミニカード風＆中央寄せ */
.fc .fc-daygrid-event {
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 8px !important;
  padding: 4px 6px !important;
}

/* タイトルに 3x3 の絵文字タイルをそのまま描く */
.fc .fc-daygrid-event .fc-event-title {
  white-space: pre;      /* \n を改行として表示 */
  text-align: center;
  line-height: 1.05;
  font-size: 16px;       /* タイルを見やすく */
}
</style>
""", unsafe_allow_html=True)


# ========================
# ヘルパー
# ========================
def build_emoji_grid_title(reserved: set[str]) -> str:
    # 予約=🟥, 空き=🟩
    filled, empty = "🟥", "🟩"
    cells = [filled if s in reserved else empty for s in NINE_SLOTS]
    count = sum(1 for s in reserved)
    # 3x3 + 件数ラベル（例: 3/9）
    grid = f"{cells[0]}{cells[1]}{cells[2]}\n{cells[3]}{cells[4]}{cells[5]}\n{cells[6]}{cells[7]}{cells[8]}"
    return f"{grid}\n{count}/9"

def fetch_day_slot_set(room: str, d: date) -> set[str]:
    rows = rdb.get_reservations_between(room, ymd(d), ymd(d))
    return {r["slot"] for r in rows if r.get("slot")}

def card(slot, status, who=None, color="#ecfeff"):
    st.markdown(f"""
    <div style="border:1px solid #e5e7eb;
                border-radius:12px;
                padding:16px;
                margin:6px;
                text-align:center;
                background:{color};">
      <b style="font-size:16px;">{slot}</b><br>
      <span style="font-size:14px;">{status}{'（'+who+'）' if who else ''}</span>
    </div>
    """, unsafe_allow_html=True)

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
            who_by_slot[sl] = r.get("name")
    count = sum(1 for v in who_by_slot.values() if v)
    return who_by_slot, count

def mk_summary_events(room_key: str, month_first: date, month_last: date):
    evs = []
    d = month_first
    while d <= month_last:
        reserved = fetch_day_slot_set(room_key, d)
        title = build_emoji_grid_title(reserved)  # ← ここを差し替え
        evs.append({
            "title": title,                        # ← タイトルで描画
            "start": f"{d.isoformat()}T00:00:00",
            "end":   f"{d.isoformat()}T23:59:00",
            "allDay": True,
            "backgroundColor": "#ffffff",
            "borderColor": "#94a3b8",
            "textColor": "#0f172a",
        })
        d += timedelta(days=1)
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

# ========================
# ガード：要ログイン
# ========================
if "user" not in st.session_state or not st.session_state["user"]:
    st.error("このページはログインが必要です。左の「ログイン」ページからログインしてください。")
    st.stop()

current_user = st.session_state["user"]
is_admin = (st.session_state.get("role") == "admin")

st.title(f"📅 {ROOM_LABEL[ROOM_KEY]} 月ビュー（9タイル表示）")
rdb.init_db()

today = date.today()
PM_KEY = f"picked_month_{ROOM_KEY}"
SD_KEY = f"selected_day_{ROOM_KEY}"

# ---------- 月切り替え ----------
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

# ========================
# カレンダーオプション（9タイル描画の本体）
# ========================
cal_opts = {
    "initialView": "dayGridMonth",
    "firstDay": 0,  # 日曜始まり
    "headerToolbar": {"left": "today prev,next", "center": "title", "right": ""},
    "height": 720,
    "locale": "ja",
    "dayMaxEventRows": True,
    "selectable": True,
}

# ========================
# カレンダー表示
# ========================
events = mk_summary_events(ROOM_KEY, month_first, month_last)
ret = st_calendar(events=events, options=cal_opts, key=f"cal_{ROOM_KEY}_{ym_key}")

with st.expander("凡例"):
    st.markdown("🟥 = 予約 / 🟩 = 空き")

# クリックで日付選択
clicked = _extract_clicked_date(ret)
if clicked and clicked != st.session_state[SD_KEY]:
    st.session_state[SD_KEY] = clicked
    st.rerun()

# 凡例
with st.expander("凡例"):
    st.markdown("""
- <span style="display:inline-block;width:10px;height:10px;background:#fb7185;border:1px solid #cbd5e1;border-radius:2px;"></span> = 予約済  
- <span style="display:inline-block;width:10px;height:10px;background:#22c55e;border:1px solid #cbd5e1;border-radius:2px;"></span> = 空き
""", unsafe_allow_html=True)

# ========================
# 選択日の予約UI（従来どおり）
# ========================
sel_day = st.session_state[SD_KEY]
st.subheader(f"🗓 {ROOM_LABEL[ROOM_KEY]}: {sel_day.strftime('%Y-%m-%d')} の予約")

# ===== 選択した日の枠予約 =====
who_by_slot, _ = fetch_day_summary(ROOM_KEY, sel_day)

# ★ 3列×3行に分ける（スマホでも見やすい）
for row_start in range(0, len(SLOTS), 3):
    row_slots = SLOTS[row_start:row_start+3]
    cols = st.columns(len(row_slots))
    for i, s in enumerate(row_slots):
        with cols[i]:
            who = who_by_slot[s]
            base_key = f"{ROOM_KEY}|{ymd(sel_day)}|{s}"

            if who:
                if st.button(f"{s} の予約をキャンセル", key=f"cancel_btn|{base_key}"):
                    ok, msg = rdb.cancel_slot_if_allowed(
                        ROOM_KEY, ymd(sel_day), s,
                        requester=current_user, is_admin=is_admin
                    )
                    if ok: st.success(msg); st.rerun()
                    else:  st.error(msg)

                # 予約済カード（薄い赤）
                card(s, "× 予約済", who, color="#fee2e2")

            else:
                if st.button(f"{s} を予約", key=f"reserve_btn|{base_key}"):
                    if not display_name.strip():
                        st.warning("表示名を入力してください。")
                    else:
                        ok, msg = rdb.reserve_slot(
                            ROOM_KEY, ymd(sel_day), s,
                            display_name.strip(), owner=current_user
                        )
                        if ok: st.success(f"{ROOM_LABEL[ROOM_KEY]} {ymd(sel_day)} {s} の予約が完了しました。"); st.rerun()
                        else:  st.error(msg)

                # 空きカード（薄い緑）
                card(s, "○ 空き", color="#dcfce7")
