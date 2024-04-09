# Version 3/17/2024
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import os
app = Flask(__name__)
app.debug = True

dasedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:94521Thwomp@localhost:3306/stocks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
   __tablename__ = 'User'
   userId = db.Column(db.Integer, primary_key=True, index=True)
   first_name = db.Column(db.String(100))
   last_name = db.Column(db.String(100))
   username = db.Column(db.String(20))
   email = db.Column(db.String(100))
   password = db.Column(db.String(100))
   cashBal = db.Column(db.Integer)
   

   def __init__(self, fName, lName, uName, email, password, cash_amount):
       self.first_name = fName
       self.last_name = lName
       self.username = uName
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
        self.userID = userID
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
      cashValue = cashValue

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


class Accounts:
    def __init__(self):
        self.users = {}

    def create_account(self, full_name, username, email, password):
        if username in self.users:
            print('Username already exists. Pleases choose a different username.')
            return False
        self.users[username] = User(full_name, username, email, password)
        print('Acount created successfully. Thank you for joining NotARealStock.Exchange')
        return True
    
    def login(self, username, password):
        if username in self.users and self.users[username].password == password:
            print('Login successful')
            return self.user[username]
        else:
            print('Invalid username or password.')
            return None


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

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Print the form data to the console
        for key, value in request.form.items():
            print(f'{key}: {value}')
    return render_template('login.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Print the form data to the console
        for key, value in request.form.items():
            print(f'{key}: {value}')
    return render_template('contact.html')

@app.route("/trade", methods=['GET', 'POST'])
def trade():
    if request.method == 'POST':
        # Print the form data to the console
        for key, value in request.form.items():
            print(f'{key}: {value}')
    return render_template('trade.html')

@app.route("/portfolio")
def portfolio():
   portfolio = Portfolio.query.all()
   return render_template('portfolio.html', portfolio=portfolio)

@app.route("/transaction")
def transaction():
  # stock = Stock.query.all()
   return render_template('transaction.html')

@app.route("/support")
def support():
    return render_template('support.html')

@app.route("/faq")
def faq():
   return render_template('faq.html')