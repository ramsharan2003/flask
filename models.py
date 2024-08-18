from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db=SQLAlchemy()
bcrypt=Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True,  nullable=False)
    password = db.Column(db.String(60), nullable=False)
    contact = db.relationship('Contact',backref='owner', lazy=True)

    def set_password(self,password):
        self.password=bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password)
    

class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(120))
    phone=db.Column(db.String(20),nullable=False)
    address=db.Column(db.String(200))
    country=db.Column(db.String(50))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)