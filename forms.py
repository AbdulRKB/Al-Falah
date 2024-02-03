from wtforms import StringField, validators, IntegerField, DateField, PasswordField, SelectField
from flask_wtf import FlaskForm as Form

class TransactionForm(Form):
    vnumber = StringField('VNumber*', [validators.DataRequired()], render_kw={"placeholder": "Enter Voucher Number"})
    details = StringField('Details*', [validators.Length(min=5, max=100), validators.DataRequired()], render_kw={"placeholder": "Enter Details"})
    amount = IntegerField('Amount*', [validators.NumberRange(min=1, max=99_000_000), validators.DataRequired()], render_kw={"placeholder": "Enter Amount"})
    date = DateField('Date*', format='%Y-%m-%d')

class LoginForm(Form):
    username = StringField('Username*', [validators.Length(min=3, max=50), validators.DataRequired()], render_kw={"placeholder": "Enter Username"})
    password = PasswordField('Password*', [validators.Length(min=8), validators.DataRequired()], render_kw={"placeholder": "Enter Password"})

class UserForm(Form):
    username = StringField('Username*', [validators.Length(min=3, max=50), validators.DataRequired()], render_kw={"placeholder": "Enter Username"})
    password = PasswordField('Password*', [validators.Length(min=8), validators.DataRequired()], render_kw={"placeholder": "Enter Password"})