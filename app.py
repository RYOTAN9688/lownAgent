# app.py

import streamlit as st
from app_agent import run_loan_agent

st.set_page_config(page_title="住宅ローン返済シミュレーション", layout="wide")

st.title("🏡 住宅ローン返済シミュレーション")
st.markdown("以下の情報を入力して、月々の返済額と総支払額を計算します。")

# ユーザー入力フォーム
with st.form("loan_form"):
    st.subheader("住宅ローン情報")
    loan_amount = st.number_input(
        "借入希望額 (万円)",
        min_value=100,
        max_value=20000,
        value=3000,
        step=100,
        format="%d"
    )
    loan_years = st.number_input(
        "返済期間 (年)",
        min_value=1,
        max_value=50,
        value=35,
        step=1
    )
    annual_interest_rate = st.number_input(
        "年利 (%)",
        min_value=0.01,
        max_value=10.0,
        value=1.5,
        step=0.01
    )

    submitted = st.form_submit_button("シミュレーションを実行")

if submitted:
    st.markdown("---")
    st.subheader("計算結果")

    with st.spinner("計算中です..."):
        try:
            # `run_loan_agent`関数に直接数値を渡す
            agent_output = run_loan_agent(loan_amount, annual_interest_rate, loan_years)
            st.info(agent_output)
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
