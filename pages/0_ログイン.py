import streamlit as st
from auth_db import init_user_db, create_user, verify_login, admin_exists

st.set_page_config(page_title="ログイン", layout="centered")
st.title("🔐 ログイン")

init_user_db()

# ---- state 初期化 ----
st.session_state.setdefault("user", None)
st.session_state.setdefault("role", None)

# 既にログイン済みなら案内ページへ誘導（自動 or リンク）
if st.session_state["user"]:
    st.success(f"ログイン中：{st.session_state['user']}（{st.session_state['role']}）")
    # 自動遷移（対応していない場合はリンクだけ表示）
    try:
        st.switch_page("pages/1_案内.py")
    except Exception:
        st.page_link("pages/1_案内.py", label="➡ 案内ページへ進む")
    st.stop()

tab_login, tab_signup = st.tabs(["ログイン", "ユーザー作成（初回/管理用）"])

# ======================
# ログインタブ
# ======================
with tab_login:
    u = st.text_input("ユーザー名", key="login_user")
    p = st.text_input("パスワード", type="password", key="login_pass")

    login_btn = st.button("ログイン", type="primary", disabled=not (u and p))
    if login_btn:
        ok, msg, role = verify_login(u, p)
        if ok:
            st.session_state["user"] = u
            st.session_state["role"] = role
            st.success(f"ようこそ {u} さん！")
            # 案内ページへ遷移
            try:
                st.switch_page("pages/1_案内.py")
            except Exception:
                st.rerun()
        else:
            st.error(msg)

# ======================
# 新規作成タブ
# ======================
with tab_signup:
    already_admin = admin_exists()
    st.caption("※ ここでは新規ユーザーを作成できます。")

    su = st.text_input("ユーザー名（新規）", key="su")
    sp = st.text_input("パスワード（新規）", type="password", key="sp")

    if not already_admin:
        st.info("⚠️ まだ管理者がいません。最初の1人は **admin** として作成できます。")
        role = st.selectbox("ロール", ["admin", "user"], index=0, key="role_select")
    else:
        st.caption("管理者は既に存在します。ここでは **一般ユーザー** のみ作成できます。")
        role = "user"

    create_btn = st.button("ユーザー作成", disabled=not (su and sp))
    if create_btn:
        ok, msg = create_user(su, sp, role)
        (st.success if ok else st.error)(msg)
        if ok and role == "admin":
            st.info("管理者が作成されました。ログインしてください。")

# ---- 未ログイン時の補助リンク（任意）----
st.divider()
st.page_link("pages/2_使い方.py", label="📘 使い方ページを開く")

# ログイン状態表示
if st.session_state["user"]:
    st.info(f"ログイン中：{st.session_state['user']}（{st.session_state['role']}）")

    if st.button("ログアウト"):
        # セッション情報をクリア
        st.session_state["user"] = None
        st.session_state["role"] = None
        st.success("ログアウトしました。")
        st.rerun()
