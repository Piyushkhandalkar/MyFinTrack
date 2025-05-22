from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, TransactionForm
from .models import User, Transaction
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import plotly.graph_objs as go
from datetime import datetime

# Define the blueprint
main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created!", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Login unsuccessful. Check email and password", "danger")
    return render_template("login.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@main.route("/dashboard")
@login_required
def dashboard():
    # Fetch all transactions
    transactions = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )

    # --- 1. Income vs Expense Bar Chart ---
    income = sum(txn.amount for txn in transactions if txn.type == "income")
    expenses = sum(txn.amount for txn in transactions if txn.type == "expense")

    bar_chart = go.Figure(
        data=[
            go.Bar(
                x=["Income", "Expenses"],
                y=[income, expenses],
                marker_color=["green", "red"],
            )
        ],
        layout=go.Layout(title="Income vs Expenses"),
    )

    # --- 2. Transaction Breakdown by Category (Pie Chart) ---
    category_data = {}
    for txn in transactions:
        category_data[txn.category] = category_data.get(txn.category, 0) + txn.amount

    pie_chart = go.Figure(
        data=[
            go.Pie(
                labels=list(category_data.keys()), values=list(category_data.values())
            )
        ],
        layout=go.Layout(title="Transaction Breakdown by Category"),
    )

    # --- 3. Monthly Analysis (Line Chart) ---
    monthly_data = {}
    for txn in transactions:
        month = txn.date.strftime("%Y-%m")
        monthly_data[month] = monthly_data.get(month, 0) + txn.amount

    monthly_chart = go.Figure(
        data=[
            go.Scatter(
                x=list(monthly_data.keys()),
                y=list(monthly_data.values()),
                mode="lines+markers",
                marker=dict(color="blue"),
            )
        ],
        layout=go.Layout(
            title="Monthly Analysis", xaxis_title="Month", yaxis_title="Amount"
        ),
    )

    # --- 4. Yearly Analysis (Bar Chart) ---
    yearly_data = {}
    for txn in transactions:
        year = txn.date.strftime("%Y")
        yearly_data[year] = yearly_data.get(year, 0) + txn.amount

    yearly_chart = go.Figure(
        data=[
            go.Bar(
                x=list(yearly_data.keys()),
                y=list(yearly_data.values()),
                marker_color="purple",
            )
        ],
        layout=go.Layout(
            title="Yearly Analysis", xaxis_title="Year", yaxis_title="Amount"
        ),
    )

    # Convert graphs to JSON
    graphs = {
        "bar_chart": bar_chart.to_html(full_html=False),
        "pie_chart": pie_chart.to_html(full_html=False),
        "monthly_chart": monthly_chart.to_html(full_html=False),
        "yearly_chart": yearly_chart.to_html(full_html=False),
    }

    return render_template("dashboard.html", transactions=transactions, graphs=graphs)


@main.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            category=form.category.data,
            type=form.type.data,
            description=form.description.data,
            user_id=current_user.id,
        )
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction added successfully!", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("add_transactions.html", form=form)
