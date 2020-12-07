from flask import Flask, flash, jsonify, redirect, render_template, request, session

# from flask import Flask
app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

# Configure application
# app = Flask(__name__)

# Ensure templates are auto-reloaded
# app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")

@app.route("/")
def index():
        return render_template("about.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/chart")
def chart():
    return render_template("chart.html")
