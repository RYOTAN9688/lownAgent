# loan_calculator_tool.py

def calculate_loan_payment(loan_amount: int, annual_interest_rate: float, years: int, repayment_method: str, bonus_payment: int) -> dict:
    """
    住宅ローンの月々の返済額と総支払額を計算します。
    
    Args:
        loan_amount (int): 借入希望額（万円）。
        annual_interest_rate (float): 年利（%）。
        years (int): 返済期間（年）。
        repayment_method (str): 返済方法（'元利均等返済' or '元金均等返済'）。
        bonus_payment (int): ボーナス返済額（万円/年2回）。
        
    Returns:
        dict: 計算結果を含む辞書。
    """
    # エラーハンドリング: 無効な入力値をチェック
    if loan_amount <= 0 or annual_interest_rate < 0 or years <= 0 or bonus_payment < 0:
        return {"error": "入力値が無効です。借入額、金利、返済期間は正の数で、ボーナス払いは0以上でなければなりません。"}

    principal = loan_amount * 10000
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    number_of_payments = years * 12

    # ボーナス返済分を控除
    bonus_total = bonus_payment * 10000 * 2 * years
    principal_after_bonus = principal - bonus_total
    
    # 計算ロジック
    monthly_payment = 0
    total_payment = 0

    if repayment_method == "元利均等返済":
        if principal_after_bonus > 0:
            if monthly_interest_rate == 0:
                monthly_payment = principal_after_bonus / number_of_payments
            else:
                monthly_payment = principal_after_bonus * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / (((1 + monthly_interest_rate) ** number_of_payments) - 1)
        
        total_payment = (monthly_payment * number_of_payments) + bonus_total

    elif repayment_method == "元金均等返済":
        if principal_after_bonus > 0:
            principal_payment_per_month = principal_after_bonus / number_of_payments
            
            # 総支払額の計算
            current_principal = principal_after_bonus
            for _ in range(number_of_payments):
                interest_for_month = current_principal * monthly_interest_rate
                total_payment += (principal_payment_per_month + interest_for_month)
                current_principal -= principal_payment_per_month

        total_payment += bonus_total
        # 元金均等返済の初回返済額を計算
        first_month_interest = principal_after_bonus * monthly_interest_rate
        monthly_payment = principal_after_bonus / number_of_payments + first_month_interest
    
    # 応答形式を辞書に変更
    return {
        "loan_amount": loan_amount,
        "annual_interest_rate": annual_interest_rate,
        "years": years,
        "repayment_method": repayment_method,
        "bonus_payment": bonus_payment,
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
    }
