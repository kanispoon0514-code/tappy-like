# session_reservation_app.py
import streamlit as st
import style
style.load_css()
st.set_page_config(page_title="予約システム", layout="wide")

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

st.title("🎸YCU Session 部室予約システム")

# ログイン状態を確認
if "user" not in st.session_state or st.session_state["user"] is None:
    st.info("予約にはログインが必要です。 👉 左のメニューから **ログイン** ページを開いてください。")
    st.page_link("pages/0_ログイン.py", label="🔐 ログインページへ")
    st.info("使い方を見るには左のメニューから **使い方** ページを開いてください。")
    st.page_link("pages/2_使い方.py", label="🔰 使い方ページへ")
else:
    st.success(f"ようこそ {st.session_state['user']} さん！（{st.session_state['role']}）")
