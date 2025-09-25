# pages/1_使い方.py
import streamlit as st

st.set_page_config(page_title="使い方")
st.title("📘 使い方ガイド")

# サイドバーに現在のログイン状態＆ログアウト（どのページからでも使えると便利）
with st.sidebar:
    user = st.session_state.get("user")
    role = st.session_state.get("role")
    if user:
        st.caption(f"ログイン中：{user}（{role}）")
        if st.button("ログアウト", key="logout_from_help"):
            st.session_state["user"] = None
            st.session_state["role"] = None
            try:
                st.switch_page("pages/0_ログイン.py")
            except Exception:
                st.rerun()
    else:
        st.caption("未ログインです。")
        st.page_link("pages/0_ログイン.py", label="🔐 ログインページへ")

st.markdown("""
このシステムは **旧部室** と **新部室** の予約を、**月カレンダー**で管理します。  
予約の保存先はプロジェクト直下の **SQLiteファイル（`reservations.sqlite3`）** です。
""")

st.divider()
st.markdown("## 🚪 はじめに（ログイン）")
st.markdown("""
- 先に **[ログイン]** が必要です。アカウントが無い場合は **ユーザー作成** から登録してください。
- **adminは最初の1人だけ**作成可能です（以降は一般ユーザーのみ作成できます）。
""")
col0a, col0b = st.columns(2)
with col0a:
    st.page_link("pages/0_ログイン.py", label="🔐 ログイン / ユーザー作成へ")
with col0b:
    st.page_link("pages/1_案内.py", label="📖 案内ページへ")

st.divider()
st.markdown("## 🗓 予約のしかた")
with st.expander("手順を見る（簡単 3 ステップ）", expanded=True):
    st.markdown("""
1. **案内ページ**から、対象の部屋のページを開く  
   - 旧部：**旧部室カレンダー**  
   - 新部：**新部室カレンダー**
2. 画面上部の **「表示名」** に、相手に見せたい名前を入力  
3. 月カレンダーで **日付をクリック** → 下部に表示される **枠（1〜5限）** の **空き（○）** を **予約** ボタンで確定
    """)
    st.markdown("> 同じ **部屋×日付×枠** は1件だけ。二重予約はできません。")

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/3_旧部室カレンダー.py", label="📅 旧部室カレンダーを開く")
with col2:
    st.page_link("pages/4_新部室カレンダー.py", label="📅 新部室カレンダーを開く")

st.divider()
st.markdown("## ♻️ 予約の変更 / キャンセル")

with st.expander("🔻 予約をキャンセルする手順（プルダウン）", expanded=False):
    st.markdown("""
**一般ユーザー（自分の予約）**

1. まず **案内ページ**から部屋を選択して開く  
   - 旧部：**旧部室カレンダー**／新部：**新部室カレンダー**
2. 月カレンダーで **予約を入れている日付** をクリック  
3. 画面下部の「🗓 選択日の枠予約」の一覧で、**自分の名前が入っている枠**を探す  
4. その枠に表示される **「〇〇 の予約をキャンセル」** ボタンを押す  
5. 画面に **「キャンセルしました」** と出たら完了（自動で更新）

> 別の枠や日付に変更したいときは、**一度キャンセル → 希望の枠を取り直し** で対応します。
""")

    st.markdown("""
**管理者（admin）**

- どのユーザーの予約でも **キャンセル可能** です（カレンダーページから実行可）
- 一括で扱いたい場合は管理ページを用意して運用してください（必要なら追加します）
""")

with st.expander("🔧 キャンセルで困ったとき（チェックリスト）", expanded=False):
    st.markdown("""
- **ログインしているか？**（未ログインだとボタンが出ません）
- **自分の予約か？**（一般ユーザーは自分の予約だけキャンセル可能）
- **日付の選択は合っているか？**（カレンダーで対象日をクリックしてから下部の一覧を確認）
- **画面が更新されない？** → ボタン押下後に自動で更新されます。変化が無ければブラウザの再読込
- **日本時間（JST）で動いているか？** PC の時刻/タイムゾーンを確認
""")
st.divider()
st.markdown("## 📆 カレンダーの操作")
st.markdown("""
- **日曜はじまり**の月ビューです。  
- サイドバーの **「月の基準日」** で月を変更できます。  
- **前月 / 次月** ボタンでも切り替え可能。  
- カレンダー上の日付をクリックすると、下部の「選択日の枠予約」がその日に切り替わります。
""")

st.divider()
st.markdown("## 👥 権限とルール")
st.markdown("""
- **一般ユーザー（user）**  
  - 自分の予約の作成／キャンセルが可能  
  - 他人の予約のキャンセルは不可
- **admin**（※すでに設定済み、3長にユーザー名とpw配布） 
  - すべての予約を管理可能（強制キャンセル等）
""")

st.divider()
st.markdown("## 💾 データの保存先とバックアップ")
st.markdown("""
- 予約は **`reservations.sqlite3`** に保存されます（プロジェクト直下）。  
- バックアップはこのファイルをコピーするだけでOK。  
- 他環境へ移行する場合は **`reservation_db.py` / `auth_db.py` / `reservations.sqlite3`** を一緒に持っていけば基本的に動きます。
""")

st.divider()
st.markdown("## 🧩 よくある質問（FAQ）")
with st.expander("クリックした日と違う日が選ばれる"):
    st.markdown("""
- ブラウザを再読み込みしてみてください。  
- PC の時刻やタイムゾーンが **日本時間（JST）** になっているか確認してください。  
- 日付クリック後に画面が更新されない場合は、ページ上部のメッセージやボタンの反応を確認し、ネットワーク状況も見てください。
""")
with st.expander("予約できない / 反応がない"):
    st.markdown("""
- **表示名** が空の可能性があります。上部の入力欄に名前を入れてください。  
- その枠がすでに埋まっている可能性があります（同じ **部屋×日付×枠** は1件のみ）。
""")
with st.expander("他人の予約を修正したい"):
    st.markdown("""
- 一般ユーザーは不可です。**管理者**に依頼してください。  
- 管理者は該当予約をキャンセルの上、正しい内容で取り直してください。
""")
with st.expander("管理者を増やしたい / 交代したい"):
    st.markdown("""
- 本システムは **管理者1人**の運用です。交代が必要な場合は管理者UIを追加するか、SQLite を直接更新してロールを移譲してください。  
- 迷ったら開発者（吉兼）に相談してください。
""")

st.divider()
st.markdown("## 🔗 便利リンク")
st.page_link("pages/0_ログイン.py", label="🔐 ログイン / ユーザー作成へ")
cols = st.columns(2)
with cols[0]:
    st.page_link("pages/3_旧部室カレンダー.py", label="📅 旧部室カレンダー")
with cols[1]:
    st.page_link("pages/4_新部室カレンダー.py", label="📅 新部室カレンダー")

st.success("この予約サービスに関する要望、アイデアがありましたら開発者（吉兼）に連絡してください")
