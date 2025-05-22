from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def get_summary(user_id):
    income = (
        Transaction.query.filter_by(user_id=user_id, type="income")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
        or 0
    )
    expense = (
        Transaction.query.filter_by(user_id=user_id, type="expense")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
        or 0
    )
    balance = income - expense
    return {"total_income": income, "total_expense": expense, "balance": balance}


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "login"
    login_manager.login_message_category = "info"

    from .routes import main

    app.register_blueprint(main)

    return app
