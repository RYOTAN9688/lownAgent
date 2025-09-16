import pandas as pd
import numpy as np

def calculate_loan_payment(loan_amount: int, annual_interest_rate: float, years: int, repayment_method: str, bonus_payment: int) -> dict:
    """
    住宅ローンの月々の返済額と総支払額を計算します。
    """
    if loan_amount <= 0 or years <= 0 or annual_interest_rate < 0:
        return {"error": "入力値は正の数である必要があります。"}

    principal = loan_amount * 10000
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    number_of_payments = years * 12
    bonus_payment_per_year = bonus_payment * 10000 * 2
    
    total_payment = 0
    monthly_payment = 0

    if repayment_method == "元利均等返済":
        if monthly_interest_rate == 0:
            monthly_payment = principal / number_of_payments
        else:
            monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / (((1 + monthly_interest_rate) ** number_of_payments) - 1)
        
        # ボーナス返済額を考慮した総支払額を計算
        if bonus_payment > 0:
            remaining_principal = principal
            total_payment = 0
            for month in range(1, number_of_payments + 1):
                monthly_interest = remaining_principal * monthly_interest_rate
                
                if month % 6 == 0:
                    principal_paid = (monthly_payment + bonus_payment_per_year / 2) - monthly_interest
                    total_payment += (monthly_payment + bonus_payment_per_year / 2)
                else:
                    principal_paid = monthly_payment - monthly_interest
                    total_payment += monthly_payment
                    
                remaining_principal -= principal_paid
                if remaining_principal <= 0:
                    total_payment += remaining_principal
                    break
        else:
            total_payment = monthly_payment * number_of_payments

    elif repayment_method == "元金均等返済":
        principal_per_month = principal / number_of_payments
        total_payment = 0
        for month in range(1, number_of_payments + 1):
            remaining_principal = principal - principal_per_month * (month - 1)
            monthly_interest = remaining_principal * monthly_interest_rate
            
            if month % 6 == 0 and bonus_payment > 0:
                total_payment += (principal_per_month + monthly_interest + bonus_payment_per_year / 2)
                if month == 1:
                    monthly_payment = principal_per_month + monthly_interest
            else:
                total_payment += (principal_per_month + monthly_interest)
                if month == 1:
                    monthly_payment = principal_per_month + monthly_interest
    
    return {
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "loan_amount": loan_amount,
        "years": years,
        "annual_interest_rate": annual_interest_rate,
        "repayment_method": repayment_method
    }


def get_amortization_schedule(loan_amount: int, annual_interest_rate: float, years: int, repayment_method: str, bonus_payment: int) -> dict:
    """
    毎月の返済額の内訳と残高の推移を計算し、DataFrameとして返します。
    """
    principal = loan_amount * 10000
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    number_of_payments = years * 12
    bonus_payment_per_year = bonus_payment * 10000 * 2

    principal_payments = []
    interest_payments = []
    loan_balances = []
    
    current_principal = principal
    
    # 毎月の返済スケジュールを計算
    if repayment_method == "元利均等返済":
        if monthly_interest_rate == 0:
            monthly_payment = principal / number_of_payments
        else:
            monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / (((1 + monthly_interest_rate) ** number_of_payments) - 1)
        
        for month in range(1, number_of_payments + 1):
            interest = current_principal * monthly_interest_rate
            principal_paid = monthly_payment - interest
            
            if month % 6 == 0 and bonus_payment > 0:
                principal_paid += (bonus_payment_per_year / 2)
            
            current_principal -= principal_paid
            
            interest_payments.append(interest)
            principal_payments.append(principal_paid)
            loan_balances.append(max(current_principal, 0))

    elif repayment_method == "元金均等返済":
        principal_per_month = principal / number_of_payments
        
        for month in range(1, number_of_payments + 1):
            if month % 6 == 0 and bonus_payment > 0:
                current_principal -= (bonus_payment_per_year / 2)
                
            interest = (principal - principal_per_month * (month - 1)) * monthly_interest_rate
            
            current_principal -= principal_per_month
            
            interest_payments.append(interest)
            principal_payments.append(principal_per_month)
            loan_balances.append(max(current_principal, 0))
    
    # 月単位のDataFrameを作成
    monthly_df = pd.DataFrame({
        '月': range(1, number_of_payments + 1),
        '元金': principal_payments,
        '利息': interest_payments,
        '残高': loan_balances
    })

    # 年単位のデータフレームに集計
    monthly_df['年'] = (monthly_df['月'] - 1) // 12 + 1
    
    # 年ごとの元金と利息の合計
    yearly_df = monthly_df.groupby('年')[['元金', '利息']].sum().reset_index()
    
    # 年ごとの月末残高
    yearly_balance_df = monthly_df.loc[monthly_df['月'] % 12 == 0].copy()
    yearly_balance_df['年'] = (yearly_balance_df['月'] - 1) // 12 + 1
    
    return {
        "monthly_df": monthly_df,
        "yearly_df": yearly_df,
        "yearly_balance_df": yearly_balance_df
    }
