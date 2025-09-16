# app.py

import streamlit as st
from app_agent import run_loan_agent
from loan_calculator_tool import calculate_loan_payment
import pandas as pd
import numpy as np

st.set_page_config(page_title="住宅ローン返済シミュレーション", layout="wide")

st.title("🏡 住宅ローン返済シミュレーション")
st.markdown("以下の情報を入力して、月々の返済額と総支払額を計算します。")

# ユーザー入力ウィジェット（フォームを削除）
st.subheader("住宅ローン情報")
col1, col2 = st.columns(2)
with col1:
    loan_amount = st.number_input(
        "借入希望額 (万円)",
        min_value=100,
        max_value=20000,
        value=3000,
        step=100
    )
    loan_years = st.number_input(
        "返済期間 (年)",
        min_value=1,
        max_value=50,
        value=35,
        step=1
    )
with col2:
    annual_interest_rate = st.number_input(
        "年利 (%)",
        min_value=0.01,
        max_value=10.0,
        value=1.5,
        step=0.01
    )
    repayment_method = st.selectbox(
        "返済方法",
        ("元利均等返済", "元金均等返済")
    )
    
bonus_payment = st.number_input(
    "ボーナス返済額 (万円/年2回)",
    min_value=0,
    value=0,
    step=1
)

# リアルタイムで計算結果を表示
st.markdown("---")
st.subheader("計算結果")

# loan_calculator_tool.py の変更を考慮し、辞書を直接受け取る
try:
    result_dict = calculate_loan_payment(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)
    
    if "error" in result_dict:
        st.error(result_dict["error"])
    else:
        st.metric(label="毎月の返済額 (元金均等返済の場合は初回返済額)", value=f"約 {int(round(result_dict['monthly_payment'])):,}円")
        st.metric(label="総支払額", value=f"約 {int(round(result_dict['total_payment'])):,}円")

        # ステップ2: グラフ表示のために、計算ツールから詳細なデータを取得
        # この部分は次のステップで実装します

except Exception as e:
    st.error(f"計算エラーが発生しました: {e}")

# AIによる説明文をボタンで生成
if st.button("AIによる詳細な説明を見る"):
    with st.spinner("AIが説明文を生成中です..."):
        try:
            agent_output = run_loan_agent(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)
            st.info(agent_output)
        except Exception as e:
            st.error(f"AIによる説明文の生成中にエラーが発生しました: {e}")
