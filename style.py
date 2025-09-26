# style.py
import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* 背景や文字色はデフォルトのまま */

        /* ボタンのスタイルだけ残す */
        div.stButton > button {
            background-color: #2563eb;
            color: white !important;
            border-radius: 8px;
            height: 3em;
            width: 100%;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #1d4ed8;
            color: #f9fafb !important;
        }
        </style>
    """, unsafe_allow_html=True)
