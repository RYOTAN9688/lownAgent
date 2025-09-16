# loan_calculator_tool.py

def calculate_loan_payment(loan_amount: int, annual_interest_rate: float, years: int) -> str:
    """
    住宅ローンの月々の返済額と総支払額を計算します。
    
    Args:
        loan_amount (int): 借入希望額（万円）。
        annual_interest_rate (float): 年利（%）。
        years (int): 返済期間（年）。
        
    Returns:
        str: 月々の返済額と総支払額を含む、フォーマットされた文字列。
    """
    # エラーハンドリング: 無効な入力値をチェック
    if loan_amount <= 0 or annual_interest_rate < 0 or years <= 0:
        return "入力値が無効です。借入額、金利、返済期間は正の数でなければなりません。"

    # 計算のために単位を変換
    principal = loan_amount * 10000
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    number_of_payments = years * 12
    
    # 計算ロジック
    if monthly_interest_rate == 0:
        monthly_payment = principal / number_of_payments
    else:
        monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / (((1 + monthly_interest_rate) ** number_of_payments) - 1)
        
    total_payment = monthly_payment * number_of_payments

    # 結果を整形して文字列で返す
    monthly_payment_formatted = f"{int(round(monthly_payment)):,}"
    total_payment_formatted = f"{int(round(total_payment)):,}"
    
    result = (
        f"借入額 {loan_amount}万円、年利 {annual_interest_rate}%、返済期間 {years}年の場合、"
        f"月々の返済額は **{monthly_payment_formatted}円** です。"
        f"総支払額は **{total_payment_formatted}円** となります。"
    )
    
    return result
