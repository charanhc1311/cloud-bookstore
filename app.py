from flask import Flask, request, redirect, session
import mysql.connector
import boto3
import os

app = Flask(__name__)
s3_client = boto3.client("s3", region_name="ap-south-1")
S3_BUCKET = "charan-bookstore-images-2026"
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "")

db_config = {
    "host": "bookstore-db.cvmw0geswixy.ap-south-1.rds.amazonaws.com",
    "user": "admin",
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": "bookstore",
    "port": 3306
}

ADMIN_EMAIL = "admin@bookstore.com"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def page_style():
    return """
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #222;
        }

        .navbar {
            background: #111827;
            color: white;
            padding: 18px 8%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar a {
            color: white;
            text-decoration: none;
            margin-left: 20px;
        }

        .container {
            width: 84%;
            max-width: 1100px;
            margin: 40px auto;
        }

        .hero {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }

        .books {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 22px;
        }

        .book {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }

        .book h2 {
            margin-top: 0;
        }

        .price {
            font-size: 20px;
            font-weight: bold;
        }

        .stock {
            color: #555;
        }

        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #1d4ed8;
        }

        button:disabled {
            background: #999;
            cursor: not-allowed;
        }

        .order {
            background: white;
            padding: 22px;
            margin-bottom: 18px;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.07);
        }

        .login-box {
            width: 400px;
            max-width: 90%;
            margin: 80px auto;
            background: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        input, select {
            width: 100%;
            padding: 12px;
            margin: 8px 0 18px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }

        .link {
            text-align: center;
            margin-top: 20px;
        }

        .footer {
            text-align: center;
            margin: 40px 0;
            color: #666;
        }

        .admin {
            border-left: 5px solid #2563eb;
        }
    </style>
    """


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email
            FROM customers
            WHERE email = %s AND password = %s
            """,
            (email, password)
        )

        customer = cursor.fetchone()

        cursor.close()
        connection.close()

        if customer:
            session.clear()
            session["customer_id"] = customer["id"]
            session["customer_name"] = customer["name"]

            return redirect("/")

        return f"""
        <html>
        <head>{page_style()}</head>
        <body>
            <div class="login-box">
                <h2>Invalid email or password</h2>
                <a href="/login">Try Again</a>
            </div>
        </body>
        </html>
        """

    return f"""
    <html>
    <head>
        <title>Cloud Bookstore Login</title>
        {page_style()}
    </head>

    <body>

        <div class="login-box">

            <h1>📚 Cloud Bookstore</h1>

            <p>Login to continue</p>

            <form method="post">

                <label>Email</label>

                <input
                    type="email"
                    name="email"
                    placeholder="Enter your email"
                    required
                >

                <label>Password</label>

                <input
                    type="password"
                    name="password"
                    placeholder="Enter your password"
                    required
                >

                <button type="submit">Login</button>

            </form>

            <div class="link">
                New customer?
                <a href="/register">Create an account</a>
            </div>

            <div class="link">
                <a href="/admin/login">Admin Login</a>
            </div>

        </div>

    </body>
    </html>
    """


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM customers WHERE email = %s",
            (email,)
        )

        existing_customer = cursor.fetchone()

        if existing_customer:

            cursor.close()
            connection.close()

            return """
            <html>
            <body>
                <h2>Email already registered.</h2>
                <a href="/login">Go to Login</a>
            </body>
            </html>
            """

        cursor.execute(
            """
            INSERT INTO customers (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, password)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/login")

    return f"""
    <html>

    <head>
        <title>Create Account</title>
        {page_style()}
    </head>

    <body>

        <div class="login-box">

            <h1>📚 Create Account</h1>

            <p>Join Cloud Bookstore</p>

            <form method="post">

                <label>Name</label>

                <input
                    type="text"
                    name="name"
                    placeholder="Enter your name"
                    required
                >

                <label>Email</label>

                <input
                    type="email"
                    name="email"
                    placeholder="Enter your email"
                    required
                >

                <label>Password</label>

                <input
                    type="password"
                    name="password"
                    placeholder="Create a password"
                    required
                >

                <button type="submit">
                    Create Account
                </button>

            </form>

            <div class="link">
                Already have an account?
                <a href="/login">Login</a>
            </div>

        </div>

    </body>

    </html>
    """


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/")
def home():

    if "customer_id" not in session:
        return redirect("/login")

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, title, author, price,image_url, stock
        FROM books
        """
    )

    books = cursor.fetchall()

    cursor.close()
    connection.close()

    book_cards = ""

    for book in books:
        image_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": book["image_url"]
            },
            ExpiresIn=3600
        )
        if book["stock"] > 0:

            button = f"""
            <form action="/buy/{book['id']}" method="post">
                <button type="submit">Buy Now</button>
            </form>
            """

        else:

            button = """
            <button disabled>Out of Stock</button>
            """
        book_cards += f"""
         <div class="book">

            <img src="{image_url}"
                 alt="{book['title']}"
                 style="width:180px;height:240px;object-fit:cover;border-radius:10px;">

            <h2>📖 {book['title']}</h2>

            <p>
                <b>Author:</b> {book['author']}
            </p>

            <p class="price">
                ₹{book['price']}
            </p>

            <p class="stock">
                Stock available: {book['stock']}
            </p>

            {button}

        </div>
        """

    return f"""
    <html>

    <head>
        <title>Cloud Bookstore</title>
        {page_style()}
    </head>

    <body>

        <div class="navbar">

            <b>📚 Cloud Bookstore</b>

            <div>
                <a href="/">Home</a>
                <a href="/orders">My Orders</a>
                <a href="/logout">Logout</a>
            </div>

        </div>

        <div class="container">

            <div class="hero">

                <h1>Welcome, {session['customer_name']}! 👋</h1>

                <p>
                    Browse our books and place your order.
                </p>

            </div>

            <h2>Available Books</h2>

            <div class="books">
                {book_cards}
            </div>

            <div class="footer">
                Hosted on AWS EC2 |
                Database: Amazon RDS MySQL
            </div>

        </div>

    </body>

    </html>
    """


@app.route("/buy/<int:book_id>", methods=["POST"])
def buy(book_id):

    if "customer_id" not in session:
        return redirect("/login")

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, title, price, stock
        FROM books
        WHERE id = %s
        """,
        (book_id,)
    )

    book = cursor.fetchone()

    if not book:

        cursor.close()
        connection.close()

        return "Book not found"

    if book["stock"] <= 0:

        cursor.close()
        connection.close()

        return "Sorry, this book is out of stock"

    customer_id = session["customer_id"]

    cursor.execute(
        """
        INSERT INTO orders
        (customer_id, book_id, total_amount, status)
        VALUES (%s, %s, %s, 'Placed')
        """,
        (customer_id, book_id, book["price"])
    )

    cursor.execute(
        """
        UPDATE books
        SET stock = stock - 1
        WHERE id = %s
        """,
        (book_id,)
    )

    cursor.execute(
        """
        UPDATE inventory
        SET quantity = quantity - 1,
            last_updated = NOW()
        WHERE book_id = %s
        """,
        (book_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return f"""
    <html>

    <head>
        <title>Order Successful</title>
        {page_style()}
    </head>

    <body>

        <div class="container">

            <div class="hero">

                <h1>✅ Order Successful!</h1>

                <h2>{book['title']}</h2>

                <p class="price">
                    ₹{book['price']}
                </p>

                <p>
                    Your order has been placed successfully.
                </p>

                <a href="/">
                    <button>Back to Bookstore</button>
                </a>

                <br><br>

                <a href="/orders">
                    <button>View My Orders</button>
                </a>

            </div>

        </div>

    </body>

    </html>
    """


@app.route("/orders")
def orders():

    if "customer_id" not in session:
        return redirect("/login")

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    customer_id = session["customer_id"]

    cursor.execute(
        """
        SELECT
            orders.id,
            orders.order_date,
            orders.total_amount,
            orders.status,
            books.title,
            books.author
        FROM orders
        LEFT JOIN books
            ON orders.book_id = books.id
        WHERE orders.customer_id = %s
        ORDER BY orders.order_date DESC
        """,
        (customer_id,)
    )

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    order_list = ""

    for order in orders:

        book_title = order["title"] or "Book information unavailable"
        author = order["author"] or "Unknown"

        order_list += f"""
        <div class="order">

            <h2>📦 Order #{order['id']}</h2>

            <h3>📖 {book_title}</h3>

            <p>
                <b>Author:</b> {author}
            </p>

            <p>
                <b>Date:</b> {order['order_date']}
            </p>

            <p class="price">
                ₹{order['total_amount']}
            </p>

            <p>
                <b>Status:</b> {order['status']}
            </p>

        </div>
        """

    if not order_list:

        order_list = """
        <div class="hero">
            <h3>No orders yet.</h3>
            <p>Start shopping from the bookstore.</p>
        </div>
        """

    return f"""
    <html>

    <head>
        <title>My Orders</title>
        {page_style()}
    </head>

    <body>

        <div class="navbar">

            <b>📚 Cloud Bookstore</b>

            <div>
                <a href="/">Home</a>
                <a href="/logout">Logout</a>
            </div>

        </div>

        <div class="container">

            <h1>📋 My Orders</h1>

            {order_list}

        </div>

    </body>

    </html>
    """


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:

            session.clear()
            session["admin"] = True

            return redirect("/admin/orders")

        return """
        <html>
        <body>
            <h2>Invalid admin credentials</h2>
            <a href="/admin/login">Try Again</a>
        </body>
        </html>
        """

    return f"""
    <html>

    <head>
        <title>Admin Login</title>
        {page_style()}
    </head>

    <body>

        <div class="login-box">

            <h1>🔐 Admin Login</h1>

            <form method="post">

                <label>Email</label>

                <input
                    type="email"
                    name="email"
                    placeholder="Admin email"
                    required
                >

                <label>Password</label>

                <input
                    type="password"
                    name="password"
                    placeholder="Admin password"
                    required
                >

                <button type="submit">
                    Admin Login
                </button>


            </form>

            <div class="link">
                <a href="/login">Customer Login</a>
            </div>

        </div>

    </body>

    </html>
    """


@app.route("/admin/orders")
def admin_orders():

    if not session.get("admin"):
        return redirect("/admin/login")

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            orders.id,
            orders.order_date,
            orders.total_amount,
            orders.status,
            customers.name,
            customers.email,
            books.title
        FROM orders
        LEFT JOIN customers
            ON orders.customer_id = customers.id
        LEFT JOIN books
            ON orders.book_id = books.id
        ORDER BY orders.order_date DESC
        """
    )

    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    order_list = ""

    for order in orders:

        book_title = order["title"] or "Book information unavailable"

        order_list += f"""
        <div class="order admin">

            <h2>📦 Order #{order['id']}</h2>

            <p>
                <b>Customer:</b> {order['name']}
            </p>

            <p>
                <b>Email:</b> {order['email']}
            </p>

            <p>
                <b>Book:</b> {book_title}
            </p>

            <p>
                <b>Date:</b> {order['order_date']}
            </p>

            <p class="price">
                ₹{order['total_amount']}
            </p>

            <p>
                <b>Current Status:</b> {order['status']}
            </p>

            <form
                action="/admin/orders/{order['id']}/status"
                method="post"
            >

                <label>Update Status</label>

                <select name="status">

                    <option value="Placed"
                        {'selected' if order['status'] == 'Placed' else ''}>
                        Placed
                    </option>

                    <option value="Processing"
                        {'selected' if order['status'] == 'Processing' else ''}>
                        Processing
                    </option>

                    <option value="Shipped"
                        {'selected' if order['status'] == 'Shipped' else ''}>
                        Shipped
                    </option>

                    <option value="Delivered"
                        {'selected' if order['status'] == 'Delivered' else ''}>
                        Delivered
                    </option>

                    <option value="Cancelled"
                        {'selected' if order['status'] == 'Cancelled' else ''}>
                        Cancelled
                    </option>

                </select>

                <button type="submit">
                    Update Status
                </button>

            </form>

        </div>
        """

    return f"""
    <html>

    <head>
        <title>Admin Orders</title>
        {page_style()}
    </head>

    <body>

        <div class="navbar">

            <b>🔐 Cloud Bookstore Admin</b>

            <div>
                <a href="/admin/orders">Orders</a>
                <a href="/admin/logout">Logout</a>
            </div>

        </div>

        <div class="container">

            <div class="hero">

                <h1>📊 Order Management</h1>

                <p>
                    Manage customer orders and update order status.
                </p>

            </div>

            {order_list}

        </div>

    </body>

    </html>
    """


@app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):

    if not session.get("admin"):
        return redirect("/admin/login")

    status = request.form["status"]

    allowed_statuses = [
        "Placed",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        return "Invalid status"

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE orders
        SET status = %s
        WHERE id = %s
        """,
        (status, order_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/admin/orders")


@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect("/admin/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
