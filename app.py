from flask import Flask, render_template, request, redirect, url_for, flash, session
from forms import LoginForm, TransactionForm, UserForm
from models import db, User, Transaction
from datetime import datetime, timedelta
from functools import wraps
from flask_wtf.csrf import CSRFProtect
from passlib.hash import sha256_crypt
from getpass import getpass
from uuid import uuid4

app = Flask(__name__)
app.secret_key = uuid4().hex
# app.secret_key = 'secret'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CSRFProtect(app)
allow_list_services = ['all','ambulance', 'dastarkhuan', 'blood', 'others']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def create_user():
    username = input("Enter Username: ")
    password = getpass("Enter Password: ")
    password = sha256_crypt.hash(password)
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    print('User created successfully!')

@app.route('/')
@login_required
def index():
    last_month = datetime.now().date() - timedelta(days=31)
    total_all_income = Transaction.query.filter(Transaction.ttype == 'income').filter(Transaction.date >= last_month).all()
    total_all_income = sum([i.amount for i in total_all_income])
    total_ambulance_income = Transaction.query.filter(Transaction.category == 'ambulance').filter(Transaction.ttype == 'income').filter(Transaction.date >= last_month).all()
    total_ambulance_income = sum([i.amount for i in total_ambulance_income])
    total_dastarkhuan_income = Transaction.query.filter(Transaction.category == 'dastarkhuan').filter(Transaction.ttype == 'income').filter(Transaction.date >= last_month).all()
    total_dastarkhuan_income = sum([i.amount for i in total_dastarkhuan_income])
    total_blood_income = Transaction.query.filter(Transaction.category == 'blood').filter(Transaction.ttype == 'income').filter(Transaction.date >= last_month).all()
    total_blood_income = sum([i.amount for i in total_blood_income])
    total_others_income = Transaction.query.filter(Transaction.category == 'others').filter(Transaction.ttype == 'income').filter(Transaction.date >= last_month).all()
    total_others_income = sum([i.amount for i in total_others_income])
    total_expenses = Transaction.query.filter(Transaction.ttype == 'expense').filter(Transaction.date >= last_month).all()
    total_expenses = sum([i.amount for i in total_expenses])
    return render_template('index.html', total_all_income=total_all_income, total_ambulance_income=total_ambulance_income, total_dastarkhuan_income=total_dastarkhuan_income, total_blood_income=total_blood_income, total_others_income=total_others_income, total_expenses=total_expenses)


@app.get('/manage/<category>')
@login_required
def manage(category):
    category=category.lower()
    if not category in allow_list_services:
        return redirect(url_for('index'))
    todays_date = datetime.now().date()
    last_month = datetime.now().date() - timedelta(days=31)
    
    if category == 'all':
        transactions = Transaction.query.filter(Transaction.date >= last_month).order_by(Transaction.date.asc()).all()
        total_income = sum([t.amount for t in transactions if t.ttype == 'income'])
        total_expenses = sum([t.amount for t in transactions if t.ttype == 'expense'])
        return render_template('manage.html', date=todays_date, last_month=last_month, category=category.title(), transactions=transactions, total_income=total_income, total_expenses=total_expenses)
    session['logged_in'] = True
    transactions = Transaction.query.filter(Transaction.category == category).filter(Transaction.date >= last_month).order_by(Transaction.date.asc()).all()
    total_income = sum([t.amount for t in transactions if t.ttype == 'income'])
    total_expenses = sum([t.amount for t in transactions if t.ttype == 'expense'])
    return render_template('manage.html', date=todays_date, last_month=last_month, category=category.title(), transactions=transactions, total_income=total_income, total_expenses=total_expenses)


@app.post('/manage/<category>')
@login_required
def manage_post(category):
    category=category.lower()
    if not category in allow_list_services:
        return redirect(url_for('index'))
    date_from = request.form.get('from_date')
    date_to = request.form.get('to_date')
    if category == 'all':
        transactions = Transaction.query.filter(Transaction.date >= date_from).filter(Transaction.date <= date_to).order_by(Transaction.date.asc()).all()
        total_income = sum([t.amount for t in transactions if t.ttype == 'income'])
        total_expenses = sum([t.amount for t in transactions if t.ttype == 'expense'])
        return render_template('manage.html', date=date_to, last_month=date_from, category=category.title(), transactions=transactions, total_income=total_income, total_expenses=total_expenses)
    transactions = Transaction.query.filter(Transaction.category == category)
    if date_from == '' or date_to == '':
        return redirect(url_for('manage', category=category))
    if date_from > date_to:
        return redirect(url_for('manage', category=category))
    transactions = transactions.filter(Transaction.date >= date_from)
    transactions = Transaction.query.filter(Transaction.category == category).filter(Transaction.date >= date_from).filter(Transaction.date <= date_to).order_by(Transaction.date.asc()).all()
    total_income = sum([t.amount for t in transactions if t.ttype == 'income'])
    total_expenses = sum([t.amount for t in transactions if t.ttype == 'expense'])
    return render_template('manage.html', date=date_to, last_month=date_from, category=category.title(), transactions=transactions, total_income=total_income, total_expenses=total_expenses)

@app.get('/manage/<category>/add_income')
@login_required
def add_new_income(category):
    category=category.lower()
    if category == 'all':
        return redirect(url_for('index'))
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction_form = TransactionForm()
    todays_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_new_income.html', form=transaction_form, date=todays_date, category=category.title())


@app.post('/manage/<category>/add_income')
@login_required
def add_new_income_post(category):
    category=category.lower()
    if category == 'all':
        return redirect(url_for('index'))
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction_form = TransactionForm()
    if transaction_form.validate():
        new_transaction = Transaction(details=transaction_form.details.data, vnumber=transaction_form.vnumber.data,ttype='income', category=category, amount=transaction_form.amount.data, date=transaction_form.date.data)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('add_new_income', category=category))
    elif request.method == 'POST':
        flash(transaction_form.errors, 'danger')
    todays_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_new_income.html', form=transaction_form, date=todays_date, category=category.title())


@app.get('/manage/<category>/add_expense')
@login_required
def add_new_expense(category):
    category=category.lower()
    if category == 'all':
        return redirect(url_for('index'))
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction_form = TransactionForm()
    todays_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_new_expense.html', form=transaction_form, date=todays_date, category=category.title())

@app.post('/manage/<category>/add_expense')
@login_required
def add_new_expense_post(category):
    category=category.lower()
    if category == 'all':
        return redirect(url_for('index'))
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction_form = TransactionForm()
    if transaction_form.validate():
        new_transaction = Transaction(details=transaction_form.details.data, vnumber=transaction_form.vnumber.data, ttype='expense', category=category, amount=transaction_form.amount.data, date=transaction_form.date.data)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('add_new_expense', category=category))
    elif request.method == 'POST':
        flash(transaction_form.errors, 'danger')
    todays_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_new_expense.html', form=transaction_form, date=todays_date, category=category.title())

@app.get('/manage/<category>/<id>/edit')
@login_required
def edit_transaction(category, id):
    category=category.lower()
    if category == 'all':
        return redirect(url_for('index'))
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction = Transaction.query.get(id)
    transaction_form = TransactionForm(obj=transaction)
    date = transaction.date.strftime('%Y-%m-%d')
    ttype = transaction.ttype.title()
    return render_template('edit_transaction.html', form=transaction_form, transaction=transaction, date=date, ttype=ttype, category=category.title())


@app.post('/manage/<category>/<id>/edit')
@login_required
def edit_transaction_post(category, id):
    category=category.lower()
    if category == 'all':
        return redirect(url_for('index'))
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction = Transaction.query.get(id)
    transaction_form = TransactionForm()
    if request.method == "POST" and transaction_form.validate():
        transaction.vnumber = transaction_form.vnumber.data
        transaction.details = transaction_form.details.data
        transaction.amount = transaction_form.amount.data
        transaction.date = transaction_form.date.data
        db.session.commit()
        flash(f'{transaction.ttype.title()} updated successfully!', 'success')
        return redirect(url_for('edit_transaction', category=category,id=id))
    else:
        flash(transaction_form.errors, 'danger')
    return render_template('edit_transaction.html', form=transaction_form, income=transaction)


@app.get('/balance')
@login_required
def balance():
    month_from_today = datetime.now().date() - timedelta(days=31)
    transactions = Transaction.query.filter(Transaction.date >= month_from_today).order_by(Transaction.date.asc()).all()
    total_income = sum([i.amount for i in transactions if i.ttype == 'income'])
    total_expenses = sum([e.amount for e in transactions if e.ttype == 'expense'])
    return render_template('trial_balance.html', transactions=transactions, total_income=total_income, total_expenses=total_expenses)

@app.get('/manage/<category>/<id>/delete')
@login_required
def delete_transaction(category, id):
    category=category.lower()
    if not category in allow_list_services:
        return redirect(url_for('index'))
    transaction = Transaction.query.get(id)
    db.session.delete(transaction)
    db.session.commit()
    flash(f'{transaction.ttype.title()} deleted successfully!', 'success')
    return redirect(url_for('manage', category=category))

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == "POST" and login_form.validate():
        # use hashlib to encrypt password sha256
        password = login_form.password.data
        # password = sha256_crypt.hash(password)
        user = User.query.filter_by(username=login_form.username.data).first()
        if user:
            if sha256_crypt.verify(password, user.password):
                session['logged_in'] = True
                session['username'] = user.username
                return redirect(url_for('index'))
    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.get('/users')
@login_required
def users():
    if session.get('username') != 'admin':
        return redirect(url_for('index'))
    users = User.query.all()
    users_form = UserForm()
    return render_template('users.html', users=users, form=users_form)


@app.post('/users')
@login_required
def users_post():
    if session.get('username') != 'admin':
        return redirect(url_for('index'))
    users_form = UserForm()
    if users_form.validate():
        password = users_form.password.data
        password = sha256_crypt.hash(password)
        new_user = User(username=users_form.username.data, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('users'))
    flash(users_form.errors, 'danger')
    return redirect(url_for('users'))

@app.post('/users/delete')
def user_delete():
    if session.get("username") != "admin":
        return redirect(url_for("index"))
    user_id = request.form.get('delete')
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'warning')
    return redirect(url_for('users'))

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)