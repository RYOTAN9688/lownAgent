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
        model="gemini-2.5-pro",
        temperature=0,
        google_api_key=google_api_key
    )

    st.session_state.prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="あなたは住宅ローンの計算結果をユーザーに分かりやすく説明するアシスタントです。計算結果と前提条件を基に、親切で丁寧な文章を生成してください。"),
        HumanMessage(content="{input}")
    ])


def run_loan_agent(loan_amount: int, annual_interest_rate: float, years: int) -> str:
    """
    住宅ローンの計算と、その結果をAIが分かりやすく説明する機能を実行します。
    """
    try:
        # 1. 計算ツールを直接呼び出して結果のテキストを取得
        result_text = calculate_loan_payment(loan_amount, annual_interest_rate, years)

        # 2. 計算結果と前提条件を組み合わせて、AIへの入力を生成
        llm_input_text = (
            f"借入額: {loan_amount}万円, 金利: 年{annual_interest_rate}%, 返済期間: {years}年。この条件での計算結果は以下の通りです: {result_text}"
        )

        # 3. LangChainを使って自然な文章を生成
        response_chain = st.session_state.prompt | st.session_state.llm
        agent_output = response_chain.invoke({"input": llm_input_text})

        return agent_output.content

    except Exception as e:
        return f"エラーが発生しました: {e}"
