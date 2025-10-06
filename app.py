from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, Product

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ------------------- DATABASE SETUP -------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makeup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------- LOGIN REQUIRED DECORATOR -------------------
def login_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

# ------------------- ROUTES -------------------

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/get_summary')
def get_summary():
    total_products = Product.query.count()
    total_stock = db.session.query(db.func.sum(Product.stock)).scalar() or 0
    low_stock = Product.query.filter(Product.stock <= 5, Product.stock > 0).count()
    out_of_stock = Product.query.filter(Product.stock == 0).count()

    return jsonify({
        "total_products": total_products,
        "total_stock": total_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock
    })

# ------------------- LOGIN -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# ------------------- LOGOUT -------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------- SHOW PRODUCTS -------------------
@app.route('/products')
@login_required
def show_products():
    query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "")
    company_filter = request.args.get("company", "")

    # Base query
    products_query = Product.query

    if query:
        products_query = products_query.filter(Product.name.ilike(f"%{query}%"))
    if category_filter and category_filter != "All Categories":
        products_query = products_query.filter_by(category=category_filter)
    if company_filter and company_filter != "All Companies":
        products_query = products_query.filter_by(company=company_filter)

    products = products_query.all()

    # Dropdown: distinct company names
    companies = [p.company for p in Product.query.distinct(Product.company).all()]

    return render_template("products.html", products=products, companies=companies)

# ------------------- ADD PRODUCT -------------------
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        company = request.form['company']
        category = request.form['category']
        use = request.form['use']
        stock = request.form['stock']

        new_product = Product(
            name=name,
            price=price,
            company=company,
            category=category,
            use=use,
            stock=stock
        )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('show_products'))

    return render_template("add_product.html")

# ------------------- EDIT PRODUCT -------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.company = request.form['company']
        product.category = request.form['category']
        product.use = request.form['use']
        product.stock = request.form['stock']

        db.session.commit()
        return redirect(url_for('show_products'))

    return render_template("edit_product.html", product=product)

# ------------------- DELETE PRODUCT -------------------
@app.route('/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('show_products'))

# ------------------- MAIN -------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
