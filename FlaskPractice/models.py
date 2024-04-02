from app import func
from flask import Flask
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:94521Thwomp@localhost:3306/stocks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Stock(db.Model):
   __tablename__ = 'Stock'
   stockId = db.Column(db.Integer, primary_key=True, index=True)
   ticker = db.Column(db.String(10))
   price = db.Column(db.Float())
   date = db.Column(db.DateTime, default=func.now())

   def __init__(self, ticker, price):
      self.ticker = ticker
      self.price = price

   def __repr__(self):
      return f'{self.ticker} at {self.price}'


class Company(db.Model):
    __tablename__ = 'Company'
    companyId = db.Column(db.Integer, primary_key=True, index=True)
    ticker = db.Column(db.String(10))
    total_shares = db.Column(db.Float(), nullable=False)
    name = db.Column(db.String(100))
    
    def __init__(self, name, ticker, total_shares):
        self.name = name
        self.ticker = ticker
        self.total_shares = int(total_shares)
        

    
class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    portfolioid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    cashBal = db.Column(db.Integer)
    stockID = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    purchasePrice = db.Column(db.Integer)

    def __init__(self, user, cash_amount=0):
        self.user = user
        self.stocks = {}
        self.cash_amount = cash_amount

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

class User(db.Model):
   __tablename__ = 'User'
   userId = db.Column(db.Integer, primary_key=True)
   full_name = db.Column(db.String(100))
   username = db.Column(db.String(20))
   email = db.Column(db.String(100))
   password = db.Column(db.String(100))
   portfolio = db.Column(db.Integer, ForeignKey(Portfolio.portfolioid))

class Transactions(db.Model):
    __tablename__ = 'Transaction_Ledger'
    transactId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, ForeignKey(User.userId))
    stockId = db.Column(db.Integer, ForeignKey(Stock.stockId))
    isWalletTransact = db.Column(db.Boolean)
    portfolioId = db.Column(db.Integer, ForeignKey(Portfolio.portfolioid))
    cashValue = db.Column(db.Integer)

    def __init__(self, user, ticker, price, date):
      self.user = user
      self.ticker = ticker
      self.price = price
      self.date = date


   
    def __init__(self, full_name, username, email, password):
      self.full_name = full_name
      self.username = username
      self.email = email
      self.password = password
      self.portfolio = Portfolio(self)
      self.transaction_history = []

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
