from flask import *
from flask_cors import CORS, cross_origin
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
from datetime import date
import requests
import os
app = Flask(__name__)	
app.secret_key = 'nothing'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/writereview": {"origins": "*"}})
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False
def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans
@app.route("/fake_reviews",methods=["GET"])
def fake_review_display():
    if session["email"]!="admin":
        return redirect(url_for("checkuser"))
    os.system('python fake_review_detect.py')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image,products.description,reviews.reviewId,reviews.user,reviews.productId,reviews.review,reviews.fake,reviews.reason,reviews.ip FROM products,reviews WHERE products.productId = reviews.productId AND reviews.fake = 1")
        data = cur.fetchall()
        dat=parse(data)
    return render_template("fakedisplay.html",data=dat)
@app.route("/formvalidate",methods=["GET"])
def validate():
    arg=request.args.get('name')
    print(arg)
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?',(arg,))
    data = cur.fetchall()
    if(len(data)==1):
        return "1"
    return "0"
@app.route("/ang",methods=["GET"])
def ang():
    return render_template("angular.html")
@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
                print(msg)
            except:
                conn.rollback()
                msg = "Error occured"
                print(msg)
        conn.close()
        return redirect(url_for('cart')),200

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image,products.description FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        #print(int(row[2]))
        totalPrice +=float(str(row[2]).replace(",",""))
    freq = {} 
    for item in products: 
        if (item in freq): 
            freq[item] += 1
        else: 
            freq[item] = 1
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,dat=freq)
@app.route("/reviews")
def order():
    if 'email' not in session:
        return redirect(url_for('checkuser'))
    loggedIn,firstName,noOfItems=getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        orders=cur.fetchall()
        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image,products.description,orders.reviewed FROM products, orders WHERE products.productId = orders.productId AND orders.userId = ?", (userId, ))
        products = cur.fetchall()
        freq={}
        for item in products: 
            if (item in freq): 
                freq[item] += 1
            else: 
                freq[item] = 1
    return render_template("order.html",loggedIn=loggedIn, firstName=firstName,order=orders,dat=freq, noOfItems = noOfItems)
@app.route("/order",methods=["GET"])
def reviews():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn,firstName,noOfItems=getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image,products.description FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cur.fetchall()
        freq={}
        for item in products: 
            if (item in freq): 
                freq[item] += 1
            else: 
                freq[item] = 1
        for key,value in freq.items():
            cur.execute("SELECT * FROM orders WHERE userId = ? AND productId = ?",(userId,key[0],))
            ordi=cur.fetchone()
            today = date.today()
            if(ordi is None):
                cur.execute("INSERT INTO orders (userId,productId,reviewed,date) VALUES (?,?,?,?)",(userId,key[0],0,today))
            else:
                cur.execute("INSERT INTO orders (userId,productId,reviewed,date) VALUES (?,?,?,?)",(userId,key[0],1,today))
        cur.execute("DELETE FROM kart");
        conn.commit()
        cur.execute("SELECT products.productId, products.name, products.price, products.image,products.description,orders.reviewed,orders.date FROM products, orders WHERE orders.userId = ? AND products.productId = orders.productId", (userId, ))
        products=cur.fetchall()
        freq={}
        for item in products: 
            if (item in freq): 
                freq[item] += 1
            else: 
                freq[item] = 1
        return render_template("orders.html",loggedIn=loggedIn,firstName=firstName,products=freq, noOfItems = noOfItems)
@app.route("/invoice",methods=["GET"])
def invoice():
    if 'email' not in session:
        return redirect(url_for('loginForm')),200
    loggedIn,firstName,noOfItems=getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT address FROM users WHERE email = ?", (session['email'], ))
        address = cur.fetchall()[0][0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image,products.description FROM products, kart WHERE products.productId = kart.productId AND kart.userId = ?", (userId, ))
        products = cur.fetchall()
        if(len(products)==0):
            return redirect(url_for("something")),200
        freq={}
        total=0
        for item in products: 
            total=total+float(str(item[2]).replace(",",""))
            if (item in freq): 
                freq[item] += 1
            else: 
                freq[item] = 1
        today = date.today()
        return render_template("invoice.html",loggedIn=loggedIn,firstName=firstName,data=freq,date=today,total=total,address=address, noOfItems = noOfItems),200
@app.route("/writereview",methods=["POST"])
def review():
    if 'email' not in session:
        return redirect(url_for('checkuser'))
    email = session['email']
    user=request.form["user"]
    review=request.form["review"]
    product=request.form["product"] 
    print(user,review,product)
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("INSERT INTO reviews (user,productId,review,fake,ip) VALUES (?,?,?,?,?)",(user,product,review,0,request.remote_addr,))
        cur.execute("UPDATE orders set reviewed = ? where productId = ? and userId = ?",(1,int(product),userId,))
        conn.commit()
    print(user,review,product)
    return {}

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('checkuser'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM kart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, Name FROM users WHERE email = ?", (session['email'], ))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)
@app.route("/profile",methods=["GET"])
def profile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, Name, phone,password,address FROM users WHERE email = ?", (session['email'], ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("profile.html",loggedIn=loggedIn, firstName=firstName,profile=profileData, noOfItems = noOfItems)
@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
        cur.execute("SELECT user,review,fake FROM reviews WHERE productId = ? AND fake = 0", (productId, ))
        reviews=cur.fetchall()
    conn.close()
    return render_template("productDescription1.html", data=productData,review=reviews, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        Name = request.form['Name']
        phone = request.form['phone']
        address = request.form['address']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, Name, phone ,address) VALUES (?, ?, ?, ? ,?)', (hashlib.md5(password.encode()).hexdigest(), email, Name, phone,address,))
                con.commit()
                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return render_template("login.html", error=msg)
@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('checkuser'))
@app.route("/add")
def admin():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)
@app.route("/checklogin",methods=["POST","GET"])
def checkuser():
    if request.method=="GET":
        try:
            if(session["email"]=="admin"):
               return render_template("admin.html")
        except:
            pass
    if request.method=="POST":
        email = request.form['email']
        password = request.form['password']
        if(email=="admin" and password=="admin"):
            session['email']="admin"
            return render_template("admin.html")
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('something')),200
        else:
            error = 'Invalid email / Password'
            return render_template('login.html', error=error),400

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?", (categoryId, ))
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)
@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('something'))
@app.route("/registerationForm",methods=["GET"])
def registrationForm():
    return render_template("register.html")
@app.route("/remove")
def remove():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock,categoryId FROM products')
        data = cur.fetchall()
    conn.close()
    data = parse(data)
    print(data[1])
    return render_template('remove.html', data=data)
@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('checkuser'))


@app.route("/some",methods=["GET"])
def something():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)   
    return render_template('home1.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)
@app.route("/")
def root():
    print(request.remote_addr)
    return render_template('nav.html')

@app.route("/login",methods=["GET"])
def login():
    return render_template("login.html",error="")
if __name__ == '__main__':
    app.run(host= '0.0.0.0',port=5000,debug=True)
