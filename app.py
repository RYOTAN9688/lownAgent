# app.py

import streamlit as st
from app_agent import run_loan_agent
from loan_calculator_tool import calculate_loan_payment, get_amortization_schedule
import pandas as pd
import numpy as np

st.set_page_config(page_title="住宅ローン返済シミュレーション", layout="wide")

st.title("🏡 住宅ローン返済シミュレーション")
st.markdown("以下の情報を入力して、月々の返済額と総支払額を計算します。")

# ユーザー入力ウィジェット
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

try:
    result_dict = calculate_loan_payment(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)

    if "error" in result_dict:
        st.error(result_dict["error"])
    else:
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="毎月の返済額 (元金均等返済の場合は初回返済額)", value=f"約 {int(round(result_dict['monthly_payment'])):,}円")
        with col4:
            st.metric(label="総支払額", value=f"約 {int(round(result_dict['total_payment'])):,}円")

        # グラフ表示のためのデータ取得
        amortization_df = get_amortization_schedule(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)

        # データを年単位で集計
        amortization_df['年'] = (amortization_df['月'] - 1) // 12 + 1
        yearly_df = amortization_df.groupby('年')[['元金', '利息']].sum().reset_index()

        # グラフの描画
        st.subheader("年間の元金と利息の推移")
        # 元金が下、利息が上になるように順番を修正
        st.bar_chart(yearly_df, x='年', y=['元金', '利息'])

        st.subheader("ローン残高の推移")
        # 年単位の残高を取得
        yearly_df_balance = amortization_df.loc[amortization_df['月'] % 12 == 0].copy()
        yearly_df_balance.rename(columns={'月': '返済月'}, inplace=True)
        yearly_df_balance['年'] = yearly_df_balance['返済月'] // 12
        st.line_chart(yearly_df_balance, x='年', y='残高')

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
