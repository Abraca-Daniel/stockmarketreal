# Version 3/17/2024
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.app_context()
app.debug = True
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
   __tablename__ = 'User'
   userId = db.Column(db.Integer, primary_key=True, index=True)
   first_name = db.Column(db.String(100))
   last_name = db.Column(db.String(100))
   email = db.Column(db.String(100))
   password = db.Column(db.String(100))
   cashBal = db.Column(db.Integer)
   username = db.Column(db.String(100))
   

   def __init__(self, fName, lName, email, password, cash_amount, username):
       self.first_name = fName
       self.last_name = lName
       self.email = email
       self.password = password
       self.cashBal = cash_amount
       self.username = username

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
    cashValue = db.Column(db.Integer)
    buyorsell = db.Column(db.Boolean)
    date = db.Column(db.DateTime, default=func.now())
    stock = db.relationship('Stock', backref=db.backref('transactions', lazy=True))

    def __init__(self, userId, stockId, cashValue, buyorsell):
        self.userId = userId
        self.stockId = stockId
        self.cashValue = cashValue
        buyorsell = buyorsell

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
    name = request.form.get('name')
    fname, lname = name.split(' ', 1)
    email = request.form.get('email')
    username = request.form.get('email')
    password = request.form.get('psw')
    cashBal = request.form.get('cashBal')
    new_user = User(fname, lname, email, password, cashBal, username)
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


@app.route("/portfolio")
def portfolio():
   return render_template('portfolio.html')

@app.route("/searchstock")
def searchStock():
    return render_template('searchstock.html')

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
    transactions = Transactions.query.filter_by(userId=user_id).all()
    if not transactions:
        return "No transactions for current user"
    

    return render_template("transactions.html", transactions=transactions)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Transactions.query.first() is None:
            db.session.add(Transactions(1, 2, 1512, False))
            db.session.add(Transactions(1, 1, 1386, True))
            db.session.add(Transactions(1, 4, 1386, True))
            db.session.add(Transactions(1, 5, 9030, False))
        if User.query.first() is None:
            db.session.add(User('Daniel', 'Polonsky','polonsky.da@live.com','1234','59382', 'AbracaDaniel'))
        if Stock.query.first() is None:
            db.session.add(Stock('APPL', 56))
            db.session.add(Stock('NVDA', 200))
            db.session.add(Stock('MSFT', 2000))
            db.session.add(Stock('GOOG', 1000))
            db.session.add(Stock('AMZN', 1500))
        if Company.query.first() is None:
            db.session.add(Company('Apple Inc.', 'APPL', 20000))
            db.session.add(Company('Microsoft Corporation', 'MSFT', 10000))
            db.session.add(Company('Nvidia Corporation', 'NVDA', 100))
            db.session.add(Company('Google LLC', 'GOOG', 30000))
            db.session.add(Company('Amazon.com, Inc.', 'AMZN', 40000))
        db.session.commit()
        db.session.commit()
        app.run(debug=True)