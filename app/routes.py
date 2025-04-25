from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, TransactionForm
from .models import User, Transaction
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

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
    transactions = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )
    return render_template("dashboard.html", transactions=transactions)


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
    return render_template("add_transaction.html", form=form)
