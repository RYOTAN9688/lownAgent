# app.py

import streamlit as st
import pandas as pd
import altair as alt
from app_agent import run_loan_agent
from loan_calculator_tool import calculate_loan_payment, get_amortization_schedule

st.set_page_config(page_title="住宅ローン返済シミュレーション", layout="wide")

st.title("🏡 住宅ローン返済シミュレーション")

# セッション状態の初期化
if 'simulations' not in st.session_state:
    st.session_state.simulations = []

# UIレイアウトの分割
col_left, col_right = st.columns([1, 2])

# --- 左側のUI: 入力フォームとプラン管理 ---
with col_left:
    st.header("ローン情報入力")
    loan_amount = st.number_input(
        "借入希望額 (万円)",
        min_value=100,
        max_value=20000,
        value=3000,
        step=100,
        help="例: 年収の5〜7倍が目安とされています。"
    )
    loan_years = st.number_input(
        "返済期間 (年)",
        min_value=1,
        max_value=50,
        value=35,
        step=1,
        help="最長35年ローンが一般的です。"
    )
    annual_interest_rate = st.number_input(
        "年利 (%)",
        min_value=0.01,
        max_value=10.0,
        value=1.5,
        step=0.01,
        help="最新の金利情報を確認して入力してください。"
    )
    repayment_method = st.selectbox(
        "返済方法",
        ("元利均等返済", "元金均等返済"),
        help="元利均等返済: 毎月の返済額が一定で、家計の管理がしやすいです。\n\n"
             "元金均等返済: 毎月の返済額が徐々に減少し、総支払利息額が少ないです。"
    )
    use_bonus_payment = st.checkbox("ボーナス返済を利用する")
    bonus_payment = 0
    if use_bonus_payment:
        bonus_payment = st.number_input(
            "ボーナス返済額 (万円/年2回)",
            min_value=0,
            value=10,
            step=1
        )
    
    plan_name = st.text_input("プラン名", value=f"プラン {len(st.session_state.simulations) + 1}")
    
    if st.button("現在のプランを保存"):
        result_dict = calculate_loan_payment(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)
        amortization_data = get_amortization_schedule(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)
        
        st.session_state.simulations.append({
            'name': plan_name,
            'data': amortization_data,
            'result': result_dict
        })
        st.success("プランを保存しました！")

    st.markdown("---")
    if len(st.session_state.simulations) > 0:
        st.subheader("保存したプラン")
        for i, sim in enumerate(st.session_state.simulations):
            st.markdown(f"**{sim['name']}**")
            if st.button("削除", key=f"del_{i}"):
                st.session_state.simulations.pop(i)
                st.rerun()
    
    if len(st.session_state.simulations) > 0 and st.button("すべてクリア"):
        st.session_state.simulations = []
        st.rerun()

# --- 右側のUI: 計算結果とAIアドバイス ---
with col_right:
    st.header("計算結果とAIアドバイス")

    try:
        current_result_dict = calculate_loan_payment(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)
        current_amortization_data = get_amortization_schedule(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)

        if "error" in current_result_dict:
            st.error(current_result_dict["error"])
        else:
            summary_data = []
            if len(st.session_state.simulations) > 0:
                for sim in st.session_state.simulations:
                    summary_data.append({
                        "プラン名": sim['name'],
                        "借入額 (万円)": sim['result']['loan_amount'],
                        "返済期間 (年)": sim['result']['years'],
                        "年利 (%)": sim['result']['annual_interest_rate'],
                        "毎月返済額 (円)": f"{int(round(sim['result']['monthly_payment'])):,}",
                        "総支払額 (円)": f"{int(round(sim['result']['total_payment'])):,}"
                    })
            
            summary_data.append({
                "プラン名": "現在のプラン",
                "借入額 (万円)": current_result_dict['loan_amount'],
                "返済期間 (年)": current_result_dict['years'],
                "年利 (%)": current_result_dict['annual_interest_rate'],
                "毎月返済額 (円)": f"{int(round(current_result_dict['monthly_payment'])):,}",
                "総支払額 (円)": f"{int(round(current_result_dict['total_payment'])):,}"
            })
            
            summary_df = pd.DataFrame(summary_data)
            
            st.subheader("シミュレーション比較")
            st.table(summary_df)

            if len(st.session_state.simulations) > 0:
                st.subheader("保存したプランとの比較")
                
                comparison_balance_df = pd.DataFrame()
                
                for sim in st.session_state.simulations:
                    df = sim['data']['yearly_balance_df'].copy()
                    df['プラン'] = sim['name']
                    comparison_balance_df = pd.concat([comparison_balance_df, df], ignore_index=True)
                
                current_df = current_amortization_data['yearly_balance_df'].copy()
                current_df['プラン'] = '現在のプラン'
                comparison_balance_df = pd.concat([comparison_balance_df, current_df], ignore_index=True)

                chart = alt.Chart(comparison_balance_df).mark_line().encode(
                    x=alt.X('年:Q', title='経過年数'),
                    y=alt.Y('残高:Q', axis=alt.Axis(format=',d', title='残高 (円)')),
                    color='プラン:N',
                    tooltip=[
                        alt.Tooltip('年', title='経過年数'),
                        alt.Tooltip('残高', title='残高 (円)', format=',.0f'),
                        'プラン'
                    ]
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            
            st.subheader("現在のプラン詳細")
            col_detail_1, col_detail_2 = st.columns(2)
            with col_detail_1:
                st.metric(label="毎月の返済額", value=f"約 {int(round(current_result_dict['monthly_payment'])):,}円")
            with col_detail_2:
                st.metric(label="総支払額", value=f"約 {int(round(current_result_dict['total_payment'])):,}円")
                
            yearly_df = current_amortization_data['yearly_df']
            st.subheader("年間の元金と利息の推移")
            
            bar_chart = alt.Chart(yearly_df).mark_bar().encode(
                x='年:O',
                y=alt.Y('value:Q', stack='zero', axis=alt.Axis(format=',d', title='金額 (円)')),
                color=alt.Color('variable:N', legend=alt.Legend(title="内訳")),
                tooltip=[
                    alt.Tooltip('年:O'),
                    alt.Tooltip('variable:N', title='内訳'),
                    alt.Tooltip('value:Q', title='金額 (円)', format=',.0f')
                ]
            ).transform_fold(
                ['元金', '利息'],
                as_=['variable', 'value']
            )
            st.altair_chart(bar_chart, use_container_width=True)
            
            yearly_balance_df = current_amortization_data['yearly_balance_df']
            st.subheader("ローン残高の推移")
            
            line_chart = alt.Chart(yearly_balance_df).mark_line().encode(
                x=alt.X('年:Q', title='経過年数'),
                y=alt.Y('残高:Q', axis=alt.Axis(format=',d', title='残高 (円)')),
                tooltip=[
                    alt.Tooltip('年', title='経過年数'),
                    alt.Tooltip('残高', title='残高 (円)', format=',.0f')
                ]
            ).interactive()
            st.altair_chart(line_chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"計算エラーが発生しました: {e}")

    if st.button("AIによる詳細な説明を見る"):
        with st.spinner("AIが説明文を生成中です..."):
            try:
                agent_output = run_loan_agent(loan_amount, annual_interest_rate, loan_years, repayment_method, bonus_payment)
                st.info(agent_output)
            except Exception as e:
                st.error(f"AIによる説明文の生成中にエラーが発生しました: {e}")
