from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 🆕 Added Category
    use = db.Column(db.String(200), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Product {self.name}>"
