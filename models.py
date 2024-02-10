from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime

db = SQLAlchemy()


class Transaction(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    vnumber = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(100), nullable=False)
    ttype = db.Column(db.String(100), nullable=False) # income/expense
    category = db.Column(db.String(100), nullable=False) # ambulance, dastarkuan, etc
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


    def __repr__(self):
        return f"Transaction('{self.details}', '{self.ttype}', '{self.category}', '{self.amount}', '{self.date}')"

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    utype = db.Column(db.Integer, nullable=False, default=2) # 1: admin, 2: user_with_full_access, 3: ambulance, 4: dastarkuan, 5: blood, 6: others 

    def __repr__(self):
        return f"User('{self.username}', '{self.password}')"