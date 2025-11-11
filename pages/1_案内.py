import streamlit as st

import style
style.load_css()

st.set_page_config(page_title="案内", initial_sidebar_state="collapsed")

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

st.title("👋 ようこそ")

st.markdown("""
旧部の予約は **「旧部室カレンダー」** を開いてください。  
新部の予約は **「新部室カレンダー」** を開いてください。  
初めて利用する方は **「使い方」** ページをご覧ください。
""")

st.divider()
st.markdown("### クイックリンク")

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/3_旧部室カレンダー.py", label="📅 旧部室カレンダーを開く")
with col2:
    st.page_link("pages/4_新部室カレンダー.py", label="📅 新部室カレンダーを開く")

st.page_link("pages/2_使い方.py", label="📘 使い方ページを開く")

# すでにログイン状態の表示（任意）
user = st.session_state.get("user")
role = st.session_state.get("role")
if user:
    st.caption(f"ログイン中：{user}（{role}）")
