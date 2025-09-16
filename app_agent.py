# app_agent.py

import streamlit as st
from loan_calculator_tool import calculate_loan_payment
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# セッション状態にLLMとプロンプトが存在しない場合のみ初期化を実行
if "llm" not in st.session_state or "prompt" not in st.session_state:
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except KeyError:
        st.error("Google APIキーが見つかりません。'.streamlit/secrets.toml'ファイルに 'GOOGLE_API_KEY' を設定してください。")
        st.stop()

    st.session_state.llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=google_api_key
    )

    st.session_state.prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="あなたは住宅ローンの計算結果をユーザーに分かりやすく説明するアシスタントです。計算結果と前提条件を基に、親切で丁寧な文章を生成してください。テンプレートや特定のフォーマットは使用せず、完全に自然な文章で回答してください。"
            ),
        HumanMessage(content="{input}")
    ])


def run_loan_agent(loan_amount: int, annual_interest_rate: float, years: int, repayment_method: str, bonus_payment: int) -> str:
    """
    住宅ローンの計算と、その結果をAIが分かりやすく説明する機能を実行します。
    """
    try:
        # 1. 計算ツールを直接呼び出して結果の辞書を取得
        result_dict = calculate_loan_payment(loan_amount, annual_interest_rate, years, repayment_method, bonus_payment)

        # エラーハンドリング
        if "error" in result_dict:
            return result_dict["error"]

        # 2. 辞書から必要な値を取得し、LLMへの入力を自然な文章で作成
        loan_amount_str = f"{result_dict['loan_amount']:,}万円"
        annual_interest_rate_str = f"年{result_dict['annual_interest_rate']}%"
        years_str = f"{result_dict['years']}年"
        repayment_method_str = f"{result_dict['repayment_method']}"
        monthly_payment_str = f"約{int(round(result_dict['monthly_payment'])):,}円"
        total_payment_str = f"約{int(round(result_dict['total_payment'])):,}円"
        
        # LLMへの入力文字列を、テンプレートを一切含まない形式で作成
        llm_input_text = (
            f"以下の条件で住宅ローンのシミュレーションを行いました。\n\n"
            f"・お借入希望額: {loan_amount_str}\n"
            f"・返済期間: {years_str}\n"
            f"・金利: {annual_interest_rate_str}\n"
            f"・返済方法: {repayment_method_str}\n\n"
            f"計算結果として、毎月のご返済額は{monthly_payment_str}となり、総返済額は約{total_payment_str}となりました。この結果を分かりやすく説明してください。"
        )

        # 3. LangChainを使って自然な文章を生成
        response_chain = st.session_state.prompt | st.session_state.llm
        agent_output = response_chain.invoke({"input": llm_input_text})

        return agent_output.content

    except Exception as e:
        return f"エラーが発生しました: {e}"
