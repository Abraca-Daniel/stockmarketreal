# Version 3/17/2024
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import os

app = Flask(__name__)
app.app_context()
app.debug = True
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
file_path=".\instance\db.sqlite"

class User(db.Model):
   __tablename__ = 'User'
   userId = db.Column(db.Integer, primary_key=True, index=True)
   first_name = db.Column(db.String(100))
   last_name = db.Column(db.String(100))
   email = db.Column(db.String(100))
   password = db.Column(db.String(100))
   cashBal = db.Column(db.Integer)
   

   def __init__(self, fName, lName, email, password, cash_amount):
       self.first_name = fName
       self.last_name = lName
       self.email = email
       self.password = password
       self.cashBal = cash_amount

class Stock(db.Model):
   __tablename__ = 'Stock'
   stockId = db.Column(db.Integer, primary_key=True, index=True)
   ticker = db.Column(db.String(5))
   price = db.Column(db.Float())

   def __init__(self, ticker, price):
      self.ticker = ticker
      self.price = price

   def __repr__(self):
      return f'{self.ticker} at {self.price}'

class Company(db.Model):
    __tablename__ = 'Company'
    companyId = db.Column(db.Integer, primary_key=True, index=True)
    ticker = db.Column(db.String(5))
    total_shares = db.Column(db.Float(), nullable=False)
    name = db.Column(db.String(100))
    
    def __init__(self, name, ticker, total_shares):
        self.name = name
        self.ticker = ticker
        self.total_shares = int(total_shares)
            
class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    portfolioid = db.Column(db.Integer, primary_key=True, index=True)
    userid = db.Column(db.Integer, ForeignKey(User.userId))
    stockID = db.Column(db.Integer, ForeignKey(Stock.stockId))
    quantity = db.Column(db.Integer)
    purchasePrice = db.Column(db.Integer) 

    def __init__(self, userID, Stock, quantity, purchasePrice):
        self.userid = userID
        self.stockID = Stock
        self.quantity = quantity
        self.purchasePrice = purchasePrice

    def add_stock(self, stock, quantity):
        if stock.ticker not in self.stocks:
            self.stocks[stock.ticker] = quantity
        else:
            self.stocks[stock.ticker] += quantity

    def remove_stock(self, stock, quantity):
        if stock.ticker not in self.stocks or self.stocks[stock.ticker] < quantity:
            print("You don't have enough shares of this stock to sell.")
            return
        self.stocks[stock.ticker] -= quantity

    def view_portfolio(self):
        print("Portfolio:")
        for ticker, quantity in self.stocks.items():
            print(f"{ticker}: {quantity} shares")

    def view_balance(self):
        return self.cash_amount

    def deposit_cash(self, amount):
        self.cash_amount += amount

    def withdraw_cash(self, amount):
        if amount > self.cash_amount:
            print("Insufficient funds in wallet.")
            return False
        self.cash_amount -= amount
        return True
    
    def view_transaction_history(self):
        print("Transaction History:")
        for transaction in self.transaction_history:
            print(transaction)

class Transactions(db.Model):
    __tablename__ = 'Transaction_Ledger'
    transactId = db.Column(db.Integer, primary_key=True, index = True)
    userId = db.Column(db.Integer, ForeignKey(User.userId))
    stockId = db.Column(db.Integer, ForeignKey(Stock.stockId))
    isWalletTransact = db.Column(db.Boolean)
    portfolioId = db.Column(db.Integer, ForeignKey(Portfolio.portfolioid))
    cashValue = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=func.now())

    def __init__(self, userId, stockId, walletBool, portfolioId, cashValue):
      self.userId = userId
      self.stockId = stockId
      self.isWalletTransact = walletBool
      self.portfolioId = portfolioId
      self.cashValue = cashValue

    def buy_stock(self, stock, quantity):
        if stock.price * quantity > self.portfolio.view_balance():
            print("Not enough money available to buy this quantity of stock.")
            return
        self.portfolio.add_stock(stock, quantity)
        self.portfolio.withdraw_cash(stock.price * quantity)
        self.transaction_history.append(f"Bought {quantity} shares of {stock.company.name} at ${stock.price} per share")

    def sell_stock(self, stock, quantity):
        self.portfolio.remove_stock(stock, quantity)
        self.portfolio.deposit_cash(stock.price * quantity)
        self.transaction_history.append(f"Sold {quantity} shares of {stock.company.name} at ${stock.price} per share")

    def deposit_cash(self, amount):
        self.portfolio.deposit_cash(amount)
        self.transaction_history.append(f"Deposited ${amount} into cash account")

    def withdraw_cash(self, amount):
        if self.portfolio.withdraw_cash(amount):
            self.transaction_history.append(f"Withdrew ${amount} from cash account")

    def view_portfolio(self):
        self.portfolio.view_portfolio()

    def view_balance(self):
        self.portfolio.view_balance

    def view_transaction_history(self):
        self.portfolio.view_transaction_history()

class Administrator:
    def __init__(self):
        self.companies = []
        self.stocks = []

    def add_company(self, name, symbol):
        self.companies.append(Company(name, symbol))
        print(f"Company {name} added successfully.")

    def add_stock(self, company, ticker, volume, price):
        self.stocks.append(Stock(company, ticker, volume, price))
        print(f"Stock {ticker} added successfully.")

 #   def change_market_hours(self, start_time, end_time):
 #       print(f"Market hours changed to {start_time} - {end_time}")

 #   def change_market_schedule(self, weekdays, holidays):
 #       print(f"Market open on weekdays: {weekdays}")
 #       print(f"Market closed on holidays: {holidays}")

@app.route("/")
def hello_world():
   return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Print the form data to the console
        for key, value in request.form.items():
            print(f'{key}: {value}')
    return render_template('signup.html')

@app.route("/signupUser", methods=['POST'])
def signupUser():
    session['user_id'] = None
    name = request.form.get('name')
    fname, lname = name.split(' ', 1)
    email = request.form.get('email')
    password = request.form.get('psw')
    cashBal = request.form.get('cashBal')
    new_user = User(fname, lname, email, password, cashBal)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route("/login-signup", methods=['GET','POST'])
def login():
    return render_template('login-signup.html')

@app.route("/loginattempt", methods=['POST'])
def loginattempt():
    email = request.form.get("email")
    password = request.form.get("psw")
    if email == 'admin@stocks.com':
        return redirect(url_for('adminPage'))
    user = User.query.filter_by(email=email, password=password).first()
    print
    if user:
        session['user_id'] = user.userId
        return redirect(url_for('wallet'))
    else:
        return redirect(url_for('login'))

@app.route("/wallet", methods=['GET', 'POST'])
def wallet():
    user_id = session.get('user_id')
    if not user_id:
       return redirect(url_for('login'))
    
    user = User.query.filter_by(userId=user_id).first()
    if user is not None:
        balance = user.cashBal
    else:
        balance = "User not found"
    return render_template('wallet.html', balance=balance)

@app.route("/addcash", methods=["POST"])
def add_cash():
    user_id = session.get('user_id')
    addamount = request.form.get("addAmount")
    user = User.query.filter_by(userId=user_id).first()
    if user is not None:
        user.cashBal += int(addamount)
        db.session.commit()
        
    return redirect(url_for("wallet"))

@app.route("/withdraw", methods=["POST"])
def withdraw():
    user_id = session.get('user_id')
    withdrawAmount = request.form.get("withdrawAmount")
    user = User.query.filter_by(userId=user_id).first()
    if user is not None:
        user.cashBal -= int(withdrawAmount)
        db.session.commit()
    return redirect(url_for("wallet"))


@app.route("/portfolio", methods=["GET"])
def portfolio():
   user_id = session.get('user_id')
   if user_id is None:
       return redirect(url_for('login'))
   portfolio = db.session.query(Portfolio, Stock).join(Stock, Portfolio.stockID == Stock.stockId).filter(Portfolio.userid == user_id).all()   
   return render_template('portfolio.html', portfolio=portfolio)

@app.route("/sellastock/<int:stockID>/", methods=["GET"])
def sellaStock(stockID):
   user_id = session.get('user_id')
   portfolio_entry = Portfolio.query.filter_by(userid=user_id, stockID=stockID).first()
   stockName = Stock.query.filter_by(stockId=stockID).first()
   stockName = stockName.ticker
   availQuantity = portfolio_entry.quantity
   return render_template('sellastock.html', availQuantity=availQuantity, stockName=stockName)

@app.route("/sellthestock", methods=["POST"])
def sellthestock():
   user_id = session.get('user_id')
   quantity = request.form.get('sellQuantity')
   if user_id is None:
       return redirect(url_for('login'))
   user = User.query.filter_by(userId=user_id).first()
   ticker = request.form.get('stockTicker')
   stock = Stock.query.filter_by(ticker=ticker).first()
   company = Company.query.filter_by(ticker=ticker).first()
   stockID = stock.stockId
   portfolio_entry = Portfolio.query.filter_by(userid=user_id, stockID=stockID).first()
   user.cashBal += (int(quantity) * portfolio_entry.purchasePrice)
   portfolio_entry.quantity -= int(quantity)
   company.total_shares += int(quantity)
   test = portfolio_entry.quantity
   if test == 0:
       db.session.delete(portfolio_entry)
       db.session.commit()
       return redirect(url_for('portfolio'))
   else:
       db.session.commit()
       return redirect(url_for('portfolio'))

@app.route("/searchstock")
def searchStock():
    stock_list = Stock.query.all()
    return render_template('searchstock.html', stock_list=stock_list)

@app.route("/buyastock/<int:stockID>", methods=["GET"])
def buyaStock(stockID):
   user_id = session.get('user_id')
   portfolio_entry = Portfolio.query.filter_by(userid=user_id, stockID=stockID).first()
   stockName = Stock.query.filter_by(stockId=stockID).first()
   stockName = stockName.ticker
   company = Company.query.filter_by(ticker=stockName).first()
   availShares = company.total_shares
   return render_template('buyastock.html', availShares=availShares, stockName=stockName)    

@app.route("/buythestock", methods = ["POST"])
def buythestock():
    user_id = session.get('user_id')
    quantity = request.form.get('buyQuantity')
    if user_id is None:
        return redirect(url_for('login'))
    user = User.query.filter_by(userId=user_id).first()
    ticker = request.form.get('stockTicker')
    stock = Stock.query.filter_by(ticker=ticker).first()
    company = Company.query.filter_by(ticker=ticker).first()
    stockID = stock.stockId
    company.total_shares -= int(quantity)
    cost = (int(quantity)*stock.price)
    test = user.cashBal - cost
    if test == 0:
        return redirect(url_for('wallet'))
    else:
       user.cashBal -= cost
    portfolio_entry = Portfolio.query.filter_by(userid=user_id, stockID=stockID).first()
    if portfolio_entry is None:
        portfolio_entry=Portfolio(user_id, stockID, quantity, stock.price)
    else:
        portfolio_entry.quantity += int(quantity)
    db.session.add(portfolio_entry)
    db.session.commit()
    return redirect(url_for('portfolio'))





@app.route("/searchresult", methods=["POST"])
def searching():
    search_query = request.form.get("stockName")
    stock_list = Stock.query.filter(Stock.ticker.ilike(f'%{search_query}%')).all()
    return render_template('searchstock.html', stock_list=stock_list)


@app.route("/adminpage")
def adminPage():
    stock_list = Stock.query.all()
    company_list = Company.query.all()
    return render_template('admin_homepage.html', stock_list=stock_list, company_list=company_list)

@app.route("/addstock", methods=["POST"])
def add_stock():
    ticker = request.form.get("stockName")
    price = request.form.get("stockPrice")
    new_stock = Stock(ticker, price)
    db.session.add(new_stock)
    db.session.commit()
    return redirect(url_for("adminPage"))

@app.route("/addcompany", methods=["POST"])
def add_company():
    name = request.form.get("companyName")
    ticker = request.form.get("companyTicker")
    amtStock = request.form.get("companyAmtShares")
    new_company = Company(name, ticker, amtStock)
    db.session.add(new_company)
    db.session.commit()
    return redirect(url_for("adminPage"))

@app.route("/deletecompany/<int:companyId>")
def del_company(companyId):
    company = Company.query.filter_by(companyId=companyId).first()
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for("adminPage"))

@app.route("/deletestock/<int:stockId>")
def del_Stock(stockId):
    stock = Stock.query.filter_by(stockId=stockId).first()
    db.session.delete(stock)
    db.session.commit()
    return redirect(url_for("adminPage"))

@app.route("/transactions")
def transactionPage():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
    transactions = db.session.query(Transactions, Stock).join(Stock, Transactions.stockId == Stock.stockId).filter(Transactions.userId == user_id).all()   
    if not transactions:
        return "No transactions for current user"
    return render_template("transactions.html", transactions=transactions)


if __name__ == "__main__":
    with app.app_context():
        if os.path.isfile(file_path):
            app.run(debug=True)
        else:
            db.create_all()
            db.session.add(Transactions(1, 1, False, 1, 2000))
            db.session.add(User('Daniel', 'Polonsky','polonsky.da@live.com','SoupwithSririacha','59382'))
            db.session.add(Stock('APPL', 56))
            db.session.add(Stock('NVDA', 200))
            db.session.add(Stock('MSFT', 2000))
            db.session.add(Company('Apple Inc.', 'APPL', 20000))
            db.session.add(Company('Microsoft Corporation', 'MSFT', 10000))
            db.session.add(Company('Nvidia Corporation', 'NVDA', 100))
            db.session.add(Portfolio(1, 1, 200, 40))
            db.session.add(Portfolio(1, 2, 100, 300))
            db.session.commit()
            app.run(debug=True)