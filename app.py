import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthfood.db'
db = SQLAlchemy(app)

# Create templates directory
os.makedirs('templates', exist_ok=True)

# HTML templates (only create if they don’t exist)
templates = {
    'select_condition.html': """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Select Health Condition</title>
        <style>
            body { font-family: Arial; padding: 20px; text-align: center; }
            form { display: inline-block; }
            select, button { padding: 10px; font-size: 16px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h2>Select Your Health Condition</h2>
        <form action="/foods" method="POST">
            <select name="condition" required>
                <option value="">--Select--</option>
                {% for cond in conditions %}
                <option value="{{ cond }}">{{ cond }}</option>
                {% endfor %}
            </select>
            <button type="submit">Show Foods</button>
        </form>
    </body>
    </html>
    """,
    'food_list.html': """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Recommended Foods</title>
        <style>
            body { font-family: Arial; padding: 20px; background-image: url('/static/food.jpg'); background-size: cover; }
            form { max-width: 600px; margin: auto; }
            label { display: block; margin: 10px 0; background-color: rgba(0, 0, 0, 0.6); color: white; padding: 10px; width: fit-content; }
            button { margin-top: 15px; padding: 10px; font-size: 16px; }
        </style>
    </head>
    <body>
        <h2 style="text-align: center; color: white;">Recommended Foods for {{ condition }}</h2>
        <form action="/add_to_cart" method="POST">
            {% for food in foods %}
            <label><input type="checkbox" name="selected_foods" value="{{ food }}"> {{ food }}</label>
            {% endfor %}
            <div style="text-align: center;">
                <button type="submit">Add to Cart</button>
            </div>
        </form>
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" style="color: yellow;">← Select Another Condition</a> |
            <a href="/cart" style="color: lightgreen;">View Cart</a>
        </div>
    </body>
    </html>
    """,
    'cart.html': """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Cart</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .item { background-color: #f0f0f0; margin: 10px 0; padding: 10px; display: flex; justify-content: space-between; align-items: center; }
            .actions form { display: inline-block; margin: 0 5px; }
        </style>
    </head>
    <body>
        <h2>Your Cart</h2>
        {% if cart %}
        {% for item, qty in cart.items() %}
        <div class="item">
            <span>{{ item }} (x{{ qty }})</span>
            <div class="actions">
                <form action="/update_quantity/{{ item }}/increase" method="POST">
                    <button>+</button>
                </form>
                <form action="/update_quantity/{{ item }}/decrease" method="POST">
                    <button>-</button>
                </form>
                <form action="/remove_item/{{ item }}" method="POST">
                    <button>Remove</button>
                </form>
            </div>
        </div>
        {% endfor %}
        <form action="/place_order" method="POST">
            <button>Place Order</button>
        </form>
        {% else %}
        <p>Your cart is empty.</p>
        {% endif %}
        <br><a href="/">← Continue Browsing</a>
    </body>
    </html>
    """,
    'order_success.html': """
    <!DOCTYPE html>
    <html>
    <head><title>Order Placed</title></head>
    <body>
        <h2>Thank you! Your order has been placed.</h2>
        <a href="/">← Start Over</a>
    </body>
    </html>
    """
}

for filename, content in templates.items():
    path = f'templates/{filename}'
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())

# Foods by health condition
foods_by_condition = {
    "High BP": ["Boiled Vegetables", "Oats", "Low-Sodium Soup", "Berries", "Garlic", "Leafy Greens", "Bananas"],
    "Low BP": ["Salted Crackers", "Pickles", "Soup with Salt", "Fried Fish", "Coffee", "Cheese", "Bread"],
    "Diabetes": ["Brown Rice", "Grilled Chicken", "Steamed Broccoli", "Almonds", "Salmon", "Spinach", "Lentils"],
    "Thyroid": ["Boiled Eggs", "Leafy Greens", "Berries", "Salmon", "Yogurt", "Sweet Potatoes", "Oats"],
    "Fever": ["Chicken Soup", "Boiled Rice", "Fruit Juice", "Herbal Tea", "Rice Porridge", "Ginger Tea", "Hot Broth"],
    "Cold": ["Ginger Tea", "Warm Broth", "Citrus Fruits", "Honey", "Garlic", "Onions", "Ginger Lemon Tea"],
    "Cough": ["Honey Tea", "Turmeric Milk", "Steamed Veggies", "Ginger", "Pineapple", "Lemon Water", "Peppermint Tea"],
    "Migraine": ["Spinach", "Sweet Potatoes", "Watermelon", "Bananas", "Dark Chocolate", "Cucumber", "Almonds"],
    "Heart Disease": ["Oatmeal", "Salmon", "Avocado", "Nuts", "Olive Oil", "Chia Seeds", "Leafy Greens"],
    "Obesity": ["Salad", "Grilled Veggies", "Lentil Soup", "Cucumber", "Apple", "Broccoli", "Chicken Breast"],
    "Anemia": ["Spinach", "Red Meat", "Beetroot", "Lentils", "Chickpeas", "Eggs", "Tofu"],
    "Asthma": ["Apples", "Carrots", "Ginger", "Salmon", "Broccoli", "Spinach", "Pineapple"],
    "Acidity": ["Bananas", "Oatmeal", "Aloe Vera Juice", "Coconut Water", "Papaya", "Green Tea", "Rice Pudding"],
    "Constipation": ["Papaya", "Yogurt", "Whole Grains", "Apples", "Prunes", "Oats", "Beans"],
    "Arthritis": ["Fatty Fish", "Berries", "Broccoli", "Turmeric", "Olive Oil", "Green Tea", "Ginger"],
    "Skin Allergy": ["Cucumber", "Aloe Juice", "Turmeric Milk", "Leafy Greens", "Tomatoes", "Papaya", "Carrots"],
    "Kidney Stones": ["Coconut Water", "Basil Juice", "Lemon Water", "Watermelon", "Celery", "Apples", "Ginger Tea"],
    "Depression": ["Dark Chocolate", "Walnuts", "Green Tea", "Bananas", "Oats", "Chia Seeds", "Blueberries"],
    "Eye Problems": ["Carrots", "Sweet Corn", "Spinach", "Eggs", "Liver", "Berries", "Tomatoes"],
    "Pregnancy": ["Folic Acid-rich Foods", "Milk", "Fruits", "Leafy Greens", "Eggs", "Chicken", "Yogurt"],
    "Gastritis": ["Bananas", "Rice", "Boiled Potatoes", "Oatmeal", "Carrots", "Applesauce", "Herbal Tea"]
}

# Initialize cart
@app.before_request
def setup_cart():
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}

@app.route('/')
def home():
    return render_template('select_condition.html', conditions=foods_by_condition.keys())

@app.route('/foods', methods=['POST'])
def show_foods():
    condition = request.form['condition']
    session['condition'] = condition
    return render_template('food_list.html', condition=condition, foods=foods_by_condition.get(condition, []))

@app.route('/foods/<condition>')
def show_condition_foods(condition):
    session['condition'] = condition  # Store it in session
    foods = foods_by_condition.get(condition, [])
    return render_template('food_list.html', condition=condition, foods=foods)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    selected = request.form.getlist('selected_foods')
    # Ensure the cart is a dict
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}
    cart = session['cart']
    for item in selected:
        cart[item] = cart.get(item, 0) + 1
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    return render_template('cart.html', cart=session.get('cart', {}))

@app.route('/checkout', methods=['GET'])
def checkout():
    return render_template('checkout.html')

@app.route('/update_quantity/<item>/<action>', methods=['POST'])
def update_quantity(item, action):
    cart = session.get('cart', {})
    if item in cart:
        if action == 'increase':
            cart[item] += 1
        elif action == 'decrease':
            cart[item] -= 1
            if cart[item] <= 0:
                del cart[item]
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/remove_item/<item>', methods=['POST'])
def remove_item(item):
    cart = session.get('cart', {})
    if item in cart:
        del cart[item]
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/place_order', methods=['POST'])
def place_order():
    payment_method = request.form.get('payment_method', 'Not specified')
    condition = session.get('condition', '')
    # Here you could save the order details + payment info to a DB if needed
    session.pop('cart', None)  # Clear the cart
    return render_template('order_success.html', payment_method=payment_method, condition=condition)

if __name__ == '__main__':
    app.run(debug=True)
