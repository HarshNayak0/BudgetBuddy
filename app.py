from flask import Flask, render_template, request, session, redirect, url_for
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

from helpers import login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# start database
db = SQL("sqlite:///finance.db")

#create tables
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL)")

db.execute("CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY NOT NULL, user_id INTEGER NOT NULL, date DATE NOT NULL, amount REAL NOT NULL, category TEXT, description TEXT, FOREIGN KEY (user_id) REFERENCES users(id))")

db.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY NOT NULL, user_id INTEGER NOT NULL, amount REAL NOT NULL, date DATE NOT NULL, category TEXT NOT NULL, description TEXT, FOREIGN KEY (user_id) REFERENCES users(id))")

db.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY NOT NULL, user_id INTEGER NOT NULL, total INTEGER, category TEXT, allocated_amount INTEGER, FOREIGN KEY (user_id) REFERENCES users(id))")

#create indices NOT DONE

db.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username)")

date_today = datetime.today().date()

income_categories = ["Salary", "Freelance Work", "Business Income", "Investments", "Rental Income", "Side Hustle", "Gifts", "Royalties", "Retirement", "Government Assistance", "Alimony", "Misc"]
expense_categories = ["Housing", "Food", "Transportation", "Healthcare", "Entertainment", "Education", "Debt", "Personal", "Savings", "Gifts", "Travel", "Insurance", "Tax", "Childcare", "Home", "Utilities", "Subscriptions", "Misc"]


@app.route("/")
@login_required
def index():

    name = session["username"]

    income = db.execute("SELECT date, amount, category, description FROM income WHERE date BETWEEN DATE('now', '-30 days') AND DATE('now')")

    expenses = db.execute("SELECT date, amount, category, description FROM expenses WHERE date BETWEEN DATE('now', '-30 days') AND DATE('now')")

    totalincome = 0
    totalexpenses = 0

    for row in income:
        totalincome += row["amount"]

    for row in expenses:
        totalexpenses += row["amount"]

    net = totalincome - totalexpenses

    loss = False
    if net <= 0:
        msg = "Oh no! Looks like you're in the red!"
        loss = True
        net = abs(net)
    elif 0 < net < 500:
        msg = "You've made more than you spent! Go treat Yourself!"
    else:
        msg = "Wow! That's a lot of money! Have you considered investing some of it?"

    return render_template("index.html", name=name, income=income, expenses=expenses, net=net, totalincome=totalincome, totalexpenses=totalexpenses, msg=msg, loss=loss)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        if len(db.execute("SELECT username FROM users WHERE username = ?", username)) > 0:
            name_fail = True
            return render_template("register.html", name_fail=name_fail)
        
        if len(password) < 8 or password != confirmation:
            invalid = True
            return render_template("register.html", invalid=invalid)

        valid = False
        for ch in password:
            if ch.isnumeric():
                valid = True

        if valid == False:
            confirm_fail = True
            return render_template("register.html", confirm_fail=confirm_fail)

        hash = generate_password_hash(password, method='sha256')

        db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, hash)
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = user_id

        return redirect("/")
        
@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        hash = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not username or not password or len(hash) != 1:
            invalid = True
            return render_template("login.html", invalid=invalid)
        
        check = check_password_hash(hash[0]["hash"], password)

        if check == False:
            invalid = True
            return render_template("login.html", invalid=invalid)
        
        session["user_id"] = hash[0]["id"]
        session["username"] = hash[0]["username"]

        return redirect("/")


@app.route("/logout")
def logout():
    
    session.clear()

    return redirect("/")

@app.route("/log", methods=["GET", "POST"])
@login_required
def log():
    user_id = session["user_id"]

    if request.method == "GET":
        log_type = None
        return render_template("log.html", log_type=log_type)
    
    else:
        session["log_type"] = request.form.get("log_type")

        return redirect("/logger")

@app.route("/logger", methods=["GET", "POST"])
@login_required
def logger():
    user_id = session["user_id"]
    log_type = session["log_type"]
    
    if request.method == "GET":
        return render_template("logger.html", income_categories=income_categories, expense_categories=expense_categories, log_type=log_type)
    
    else:
        amount = request.form.get("amount")
        category = request.form.get("category")
        date = request.form.get("date")
        description = request.form.get("description")

        if not amount or int(amount) < 0 or not category:
            error = True
            return render_template("logger.html", income_categories=income_categories, expense_categories=expense_categories, error=error)

        if not date:
            date = date_today

        if log_type == "Expense":
            db.execute("INSERT INTO expenses (user_id, amount, date, category, description) VALUES (?, ?, ?, ?, ?)", user_id, amount, date, category, description)
        
        else:
            db.execute("INSERT INTO income (user_id, amount, date, category, description) VALUES (?, ?, ?, ?, ?)", user_id, amount, date, category, description)

        session.pop("log_type")

        return redirect("/")


@app.route("/income")
@login_required
def income():

    rows = db.execute("SELECT id, date, amount, category, description FROM income")

    return render_template("income.html", rows=rows)

@app.route("/expenses")
@login_required
def expenses():

    rows = db.execute("SELECT id, date, amount, category, description FROM expenses")

    return render_template("expense.html", rows=rows)

@app.route("/delete/<table>/<int:id>", methods=["GET", "POST"])
@login_required
def delete(table, id):

    db.execute("DELETE FROM ? WHERE id = ?", table, id)

    return redirect(url_for(table))

@app.route("/delete_budget", methods=["POST"])
@login_required
def delete_budget():
    user_id = session["user_id"]

    db.execute("DELETE FROM budget WHERE user_id = ?", user_id)

    return redirect("/")


@app.route("/create_budget", methods=["GET", "POST"])
@login_required
def create_budget():
    if request.method == "GET":
        return render_template("create_budget.html")
    else:
        user_id = session["user_id"]

        totalbudget = request.form.get("totalbudget")
        if not totalbudget:
            error = True
            return render_template("create_budget.html", error=error)

        if len(db.execute("SELECT total FROM budget WHERE user_id = ?", user_id)) == 0:
            db.execute("INSERT INTO budget (total, user_id) VALUES (?, ?)", totalbudget, user_id)

        else:
            budget_exists = True
            return render_template("create_budget.html", budget_exists=budget_exists)
        return redirect("/allocate_budget")

@app.route("/allocate_budget", methods=["GET", "POST"])
@login_required
def allocate_budget():

    user_id = session["user_id"]

    totalbudget = db.execute("SELECT total FROM budget WHERE user_id = ?", user_id)[0]["total"]

    if request.method == "GET":
        return render_template("allocate_budget.html", totalbudget=totalbudget, expense_categories=expense_categories)

    else:

        allocations = {}

        for category in expense_categories:
            allocations[category] = request.form.get(category, 0)
            
        checkbudget = 0
        for key in allocations:
            if allocations[key]:

                checkbudget += int(allocations[key])
            
        if checkbudget > totalbudget:
            error=True
            return render_template("allocate_budget.html", error=error, totalbudget=totalbudget, expense_categories=expense_categories)

        for category, value in allocations.items():
            db.execute("INSERT INTO budget (category, allocated_amount, user_id) VALUES (?, ?, ?)", category, value, user_id)

        return redirect("/view_budget")

@app.route("/view_budget", methods=["GET", "POST"])
@login_required
def view_budget():

    user_id = session["user_id"]

    query = db.execute("SELECT total FROM budget WHERE user_id = ?", user_id)

    if query:
        totalbudget = query[0]["total"]
    else:
        return redirect("create_budget")

    expense_data = db.execute("SELECT category, allocated_amount FROM budget WHERE user_id = ? ORDER BY category", user_id)

    usedBudget = 0

    for row in expense_data:
        if row["allocated_amount"]:
            usedBudget += row["allocated_amount"]
    
    if totalbudget - usedBudget < 0:
        error = True
        
    if totalbudget - usedBudget > 100:
        msg = 'There is still some room left in your budget. Go and treat yourself!'
    else:
        msg = "Good job allocating your budget so precisely!"
    
    dataset = json.dumps(expense_data, indent=4)

    months = list(range(1, 13))

    current_year = datetime.now().year
    years = list(range(current_year - 10, current_year + 1))

    if request.method == "GET":
        get = True
        return render_template("view_budget.html", totalbudget=totalbudget, dataset=dataset, usedBudget=usedBudget, msg=msg, months=months, years=years, get=get)

    else:
        selected_month = int(request.form.get("month_select"))
        selected_year = int(request.form.get("year_select"))

        start_date = datetime(selected_year, selected_month, 1)
        end_date = datetime(selected_year, selected_month + 1, 1) if selected_month != 12 else datetime(selected_year + 1, 1, 1)
        start_date -= timedelta(days=1)

        compare_expenses = db.execute("SELECT amount, category FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY category", user_id, start_date, end_date)

        if  len(compare_expenses) < 1:
            noData = True
            get = True
            return render_template("view_budget.html", totalbudget=totalbudget, dataset=dataset, usedBudget=usedBudget, msg=msg, noData=noData, get=get, months=months, years=years)

        compare_dataset = json.dumps(compare_expenses, indent=4)

        return render_template("view_budget.html", totalbudget=totalbudget, dataset=dataset, usedBudget=usedBudget, msg=msg, months=months, years=years, compare_dataset=compare_dataset, selected_month=selected_month, selected_year=selected_year)

        

