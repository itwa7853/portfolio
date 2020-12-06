import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocksData = db.execute("SELECT * FROM stocks WHERE users_id=?", session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
    total = 0
    for row in stocksData:
        total += (row["price"] * row["shares"])
    total += cash[0]['cash']
    return render_template("index.html", stocksData=stocksData, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        stockName = request.form.get("stockName").upper()
        shares = request.form.get("shares")
        stock = lookup(stockName)
        if stock == None:
            return apology("No such stock exists")
        stockPrice = float(stock['price'])
        usersMoney = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        for row in usersMoney:
            cash = float(row['cash'])
        if stock == None:
            return apology("No such stock exists")
        elif shares == "":
            return apology("Select an amount")
        elif cash < (stockPrice * float(shares)):
            return apology("Not enough money")
        else:
            remainingCash = cash - (stockPrice * float(shares))
            db.execute("UPDATE users SET cash = ? WHERE id = ?", remainingCash, session["user_id"])
            tempvar = db.execute("SELECT shares FROM stocks WHERE symbol = ? AND users_id = ?", stockName, session["user_id"])
            for row in tempvar:
                currentShares = row['shares']
            if len(tempvar) == 0:
                db.execute("INSERT INTO stocks (name, price, symbol, users_id, shares) VALUES (?, ?, ?, ?, ?)", stock['name'], stock['price'], stock['symbol'], session["user_id"], shares)
            else:
                db.execute("UPDATE stocks SET shares = ? WHERE users_id = ?", float(shares) + currentShares, session["user_id"])
            db.execute("INSERT INTO history (symbol, shares, price, transacted, users_id) VALUES (?, ?, ?, ?, ?)", stock['symbol'], shares, stock['price'], datetime.datetime.now(), session["user_id"])
            return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT * FROM history WHERE users_id = ?", session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("stockquote.html")
    else:
        stock = request.form.get("stockName")
        if stock == "":
            return redirect("/quote")
        stockInfo = lookup(stock)
        if stockInfo != None:
            stockDescription = "A share of " + stockInfo['name'] + " (" + stockInfo['symbol'] + ") costs $" + str(stockInfo['price']) + "."
            return render_template("stockquote.html", stockDescription=stockDescription)
        else:
            return apology("No such stock exists. Try again")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("registration.html")
    else:
        username = request.form.get("username")
        usernames = db.execute("SELECT username FROM users")
        print(username)
        for user in usernames:
            if (user['username'] == username):
                return apology("Username is taken")
        password = request.form.get("password")
        confirm = request.form.get("confirmPassword")
        if password == confirm:
            hashedPassword = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashedPassword)", username=username, hashedPassword=hashedPassword)
            return redirect("/login")
        else:
            return apology("Passwords did not match")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        currentlyOwnedStocks = db.execute("SELECT symbol FROM stocks JOIN users ON users.id = stocks.users_id WHERE id = ?", session["user_id"])
        return render_template("sell.html", currentlyOwnedStocks=currentlyOwnedStocks)
    else:
        stock = request.form.get("stockName")
        number = request.form.get("shares")
        if stock == "":
            return apology("Select a share")
        currentShares = db.execute("SELECT price, shares FROM stocks WHERE users_id = ? AND symbol = ?", session["user_id"], stock)
        stockInfo = lookup(stock)
        if currentShares[0]['shares'] - int(number) < 0:
            return apology("You cannot sell more stocks than you own")
        if currentShares[0]['shares'] - int(number) == 0:
            db.execute("DELETE FROM stocks WHERE shares = ?", int(number))
        else:
            db.execute("UPDATE stocks SET shares = shares - ? WHERE users_id = ?", int(number), session["user_id"])
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (stockInfo['price'] * int(number)), session["user_id"])
        db.execute("INSERT INTO history (symbol, shares, price, transacted, users_id) VALUES (?, ?, ?, ?, ?)", stockInfo['symbol'], (int(number) - (int(number) * 2)), stockInfo['price'], datetime.datetime.now(), session["user_id"])
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
