from __init__ import db
from datetime import datetime
class User(db.Model):
    __tablename__= 'user' # 테이블 이름 설정
    id = db.Column(db.String(64), primary_key = True) # id 속성 생성, 고유키 지정
    password_hash = db.Column(db.String(256), nullable = False) # password_hash 생성 (암호화된 비밀번호), Null값을 허용하지 않는다


class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(64), db.ForeignKey('user.id'), nullable = False)
    question = db.Column(db.Text, nullable =False)
    answer = db.Column(db.Text, nullable =False)
    timestamp = db.Column(db.DateTime, default = datetime.now, nullable = False)

class stock_analysis(db.Model):
    __tablename__ = 'stock_analysis'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.Text)
    stock_name = db.Column(db.Text)
    broker = db.Column(db.Text)
    date = db.Column(db.Text)
    goal_price = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    sub_title = db.Column(db.Text)
    body = db.Column(db.Text)
    url = db.Column(db.Text)
    stock_code = db.Column(db.Text)
    
class finance_data(db.Model):
    __tablename__ = 'finance_data'
    stock_name = db.Column(db.Text, primary_key = True)
    stock_code = db.Column(db.Text, nullable = False)
    PE_Ratio_TTM = db.Column(db.Text)
    Price_to_Sales_TTM = db.Column(db.Text)
    Price_to_Cash_Flow_MRQ = db.Column(db.Text)
    Price_to_Free_Cash_Flow_TTM = db.Column(db.Text)
    Price_to_Book_MRQ = db.Column(db.Text)
    Price_to_Tangible_Book_MRQ = db.Column(db.Text)
    Gross_margin_TTM = db.Column(db.Text)
    Gross_margin_5YA = db.Column(db.Text)
    Operating_margin_TTM = db.Column(db.Text)
    Operating_margin_5YA = db.Column(db.Text)
    Pretax_margin_TTM = db.Column(db.Text)
    Pretax_margin_5YA = db.Column(db.Text)
    Net_Profit_margin_TTM = db.Column(db.Text)
    Net_Profit_margin_5YA = db.Column(db.Text)
    Revenue_Share_TTM = db.Column(db.Text)
    Basic_EPS_ANN = db.Column(db.Text)
    Diluted_EPS_ANN = db.Column(db.Text)
    Book_Value_Share_MRQ = db.Column(db.Text)
    Tangible_Book_Value_Share_MRQ = db.Column(db.Text)
    Cash_Share_MRQ = db.Column(db.Text)
    Cash_Flow_Share_TTM = db.Column(db.Text)
    Return_on_Equity_TTM = db.Column(db.Text)
    Return_on_Equity_5YA = db.Column(db.Text)
    Return_on_Assets_TTM = db.Column(db.Text)
    Return_on_Assets_5YA = db.Column(db.Text)
    Return_on_Investment_TTM = db.Column(db.Text)
    Return_on_Investment_5YA = db.Column(db.Text)
    EPS_MRQvsQtr_1Yr_Ago_MRQ = db.Column(db.Text)
    EPS_TTMvsTTM_1Yr_Ago_TTM = db.Column(db.Text)
    EPS_Growth_5YA = db.Column(db.Text)
    Sales_MRQvsQtr_1Yr_Ago_MRQ = db.Column(db.Text)
    Sales_TTMvsTTM_1Yr_Ago_TTM = db.Column(db.Text)
    Sales_Growth_5YA = db.Column(db.Text)
    Capital_Spending_Growth_5YA = db.Column(db.Text)
    Quick_Ratio_MRQ = db.Column(db.Text)
    Current_Ratio_MRQ = db.Column(db.Text)
    LT_Debt_to_Equity_MRQ = db.Column(db.Text)
    Total_Debt_to_Equity_MRQ = db.Column(db.Text)
    Asset_Turnover_TTM = db.Column(db.Text)
    Inventory_Turnover_TTM = db.Column(db.Text)
    Revenue_Employee_TTM = db.Column(db.Text)
    Net_Income_Employee_TTM = db.Column(db.Text)
    Receivable_Turnover_TTM = db.Column(db.Text)
    Dividend_Yield_ANN = db.Column(db.Text)
    Dividend_Yield_5Year_Avg_5YA = db.Column(db.Text)
    Dividend_Growth_Rate_ANN = db.Column(db.Text)
    Payout_Ratio_TTM = db.Column(db.Text)