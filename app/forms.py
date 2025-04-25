# app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FloatField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class TransactionForm(FlaskForm):
    amount = FloatField("Amount", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    type = SelectField(
        "Type",
        choices=[("income", "Income"), ("expense", "Expense")],
        validators=[DataRequired()],
    )
    description = TextAreaField("Description")
    submit = SubmitField("Add Transaction")
