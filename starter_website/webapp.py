from flask import Flask, render_template, session, request, redirect, url_for, escape
from db_connector.db_connector import connect_to_database, execute_query
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_inputs import Inputs
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.validators import DataRequired

nav = Nav()

#create the web application
webapp = Flask(__name__)
webapp.secret_key = 'cs340_2019'

Bootstrap(webapp)
nav.init_app(webapp)

### NAVIGATION

@nav.navigation()
def nav_login():
    return Navbar(
        'Food Delivery Inc.'
    )

@nav.navigation()
def nav_customer():
    return Navbar(
        'Food Delivery Inc.',
        View('Home', 'home_customer'),
        View('Search', 'search'),
        View('View Cart', 'cart'),
        View('Change Address', 'change_address'),
        View('Logout', 'logout')
    )

@nav.navigation()
def nav_driver():
    return Navbar(
        'Food Delivery Inc.',
        View('Home', 'home_driver'),
        View('View Orders', 'orders_driver'),
        View('Change Address', 'change_address'),
        View('Logout', 'logout')
    )

@nav.navigation()
def nav_manager():
    return Navbar(
        'Food Delivery Inc.',
        View('Home', 'home_manager'),
        View('View Orders', 'orders_manager'),
        View('Change Address', 'change_address'),
        View('Logout', 'logout')
    )

### FORMS

class AddressForm(FlaskForm):
    street = TextField('street', validators=[DataRequired()])
    zip_code = IntegerField('zip', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = StringField('state', validators=[DataRequired()])

class ItemForm(FlaskForm):
    location = TextField('fSID', validators=[DataRequired()])
    food_type = TextField('Type', validators=[DataRequired()])
    name = TextField('itemName', validators=[DataRequired()])
    price = IntegerField('itemPrice', validators=[DataRequired()])


### ROUTES

@webapp.route('/')
def index():
    return redirect(url_for('login')) 

@webapp.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        db_connection = connect_to_database()
        query = "SELECT email from Final_Users;"
        result = execute_query(db_connection, query).fetchall()
        result_emails = [row[0] for row in result]
        return render_template('login.html', emails=result_emails)
    elif request.method == 'POST':
        session['email'] = request.form['email']
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT type from Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[0] == 'C':
            return redirect(url_for('home_customer'))
        elif result[0] == 'D':
            return redirect(url_for('home_driver'))
        elif result[0] == 'F':
            return redirect(url_for('home_manager'))
        return redirect(url_for('login'))

@webapp.route('/home')
def home():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'C':
            return redirect(url_for('home_customer'))
        if result[1] == 'D':
            return redirect(url_for('home_driver'))
        if result[1] == 'F':
            return redirect(url_for('home_manager'))
    return redirect(url_for('login'))
        
@webapp.route('/home_manager', methods=['POST','GET'])
def home_manager():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'F':
            if request.method=='GET':
                fquery= 'SELECT Final_FoodServices.serviceName, Final_MenuItems.type, Final_MenuItems.itemName, Final_MenuItems.itemPrice, Final_MenuItems.ItemID FROM Final_MenuItems JOIN Final_FoodServices on Final_MenuItems.foodServiceID = Final_FoodServices.foodServiceID WHERE Final_FoodServices.foodServiceID IN(SELECT foodServiceID FROM Final_ConnectTo WHERE email = \'%s\')' % (email)
                fresult = execute_query(db_connection, fquery).fetchall()
                fSIDquery= 'SELECT foodServiceID FROM Final_ConnectTo WHERE email = \'%s\'' % (email)
                fSIDquery= 'SELECT * FROM Final_FoodServices WHERE foodServiceID IN (SELECT foodServiceID FROM Final_ConnectTo WHERE email = \'%s\')' % (email)
                fSIDresult = execute_query(db_connection, fSIDquery).fetchall()
                return render_template('home_manager.html', user=result, foods=fresult, locations=fSIDresult)
            elif request.method == 'POST':
                Type = request.form['Type']
                fSID = request.form['fSID']
                itemName = request.form['itemName']
                itemPrice = request.form['itemPrice']
                db_connection = connect_to_database()
                uquery='Select (1+MAX(ItemID)) FROM Final_MenuItems'
                uresult = execute_query(db_connection, uquery).fetchone()
                query = 'INSERT INTO Final_MenuItems VALUES (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (uresult[0],Type,fSID,itemName,itemPrice)
                execute_query(db_connection, query)
                equery = 'SELECT type from Final_Users WHERE email = \'%s\'' % (email)
                result = execute_query(db_connection, equery).fetchone()
                return redirect(url_for('home_manager'))
    return redirect(url_for('login')) 

@webapp.route('/remove_item', methods=['POST','GET'])
def remove_item():
    if request.method=='POST':
        itemID = request.form['to_remove']
        db_connection = connect_to_database()
        query='DELETE FROM Final_MenuItems WHERE ItemID=\'%s\'' % (itemID)
        execute_query(db_connection, query)
        return redirect(url_for('home_manager'))
    return redirect(url_for('login'))


@webapp.route('/home_driver')
def home_driver():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\' AND deliverEmail IS NULL ' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'D':
            return render_template('home_driver.html', user=result)  
    return redirect(url_for('login'))

@webapp.route('/home_customer')
def home_customer():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'C':
            return render_template('home_customer.html', user=result)  
    return redirect(url_for('login'))

@webapp.route('/add_item')
def add_item():
    db_connection = connect_to_database()
    email = session['email']
    return render_template('add_item.html')    

@webapp.route('/search', methods=['POST','GET'])
def search():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT type FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[0] == 'C':
            query = 'SELECT DISTINCT type FROM Final_MenuItems'
            food_types = execute_query(db_connection, query).fetchall()
            if request.method=='GET':
                return render_template('search.html', food_types=food_types)
            if request.method=='POST':
                query = 'SELECT * FROM Final_MenuItems NATURAL JOIN Final_FoodServices WHERE type = \'%s\'' % (request.form['type'])
                food_items = execute_query(db_connection, query).fetchall()
                return render_template('search.html', food_types=food_types, food_items=food_items)
    return redirect(url_for('login')) 

@webapp.route('/cart', methods=['POST','GET'])
def cart():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'C':
            if request.method=='GET':
                if 'cart' in session:
                    result = []
                    print(session['cart'])
                    for item_id in session['cart']:
                        query = 'SELECT * FROM Final_MenuItems WHERE itemID = \'%s\'' % (item_id)
                        result.append(execute_query(db_connection, query).fetchone())
                    return render_template('cart.html', cart=result)
                else:
                    return render_template('emptycart.html')
            elif request.method=='POST':
                if 'cart' not in session:
                    session['cart'] = []
                session['cart'].append(request.form['item_id'])
                session.modified = True
                return redirect(url_for('cart'), code=303) 
    return redirect(url_for('login')) 

@webapp.route('/remove_cart_item', methods=['POST'])
def remove_cart_item():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'C':
            if request.method=='POST':
                if 'cart' in session:
                    if len(session['cart']) == 1:
                        session.pop('cart', None)
                    else:
                        session['cart'].remove(request.form['item_id'])
                        session.modified = True
    return redirect(url_for('cart'), code=303) 


@webapp.route('/place_order', methods=['POST','GET'])
def place_order():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users NATURAL JOIN Final_Addresses WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'C':
                query = 'INSERT INTO Final_Orders (status, orderEmail, street) VALUES (\'%s\',\'%s\',\'%s\')' % ('P', email, result[4])
                execute_query(db_connection, query)
                query = 'SELECT LAST_INSERT_ID()'
                auto_id = execute_query(db_connection, query).fetchone()
                for item in session['cart']:
                    query = 'INSERT INTO Final_ConsistOf (orderID, itemID, orderCount) VALUES (\'%s\',\'%s\',\'%s\')' % (auto_id[0], item, '1')
                    execute_query(db_connection, query)
                session.pop('cart', None)
                return render_template('placeorder.html')
                
    return redirect(url_for('login'))   
                

@webapp.route('/change_address', methods=['POST','GET'])
def change_address():
    if 'email' in session:
        db_connection = connect_to_database()
        email = session['email']
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        user = execute_query(db_connection, query).fetchone()
        query = 'SELECT * FROM Final_Addresses WHERE email = \'%s\'' % (email)
        address = execute_query(db_connection, query).fetchone()
        if request.method=='GET': 
            return render_template('change_address.html', user=user, address=address)
        if request.method=='POST':
            form = AddressForm(request.form)
            if form.validate():
                query = 'UPDATE Final_Addresses SET street = \'%s\', zip = \'%s\', city = \'%s\', state = \'%s\' WHERE email = \'%s\'' % (request.form['street'], request.form['zip'], request.form['city'], request.form['state'], email)
                execute_query(db_connection, query)
                return redirect(url_for('change_address'))   
    return redirect(url_for('login'))   

@webapp.route('/orders_driver')
def orders_driver():
    if 'email' in session:
        db_connection = connect_to_database()
        email = session['email']
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'D':
            query = 'SELECT * FROM Final_Orders'
            orders = execute_query(db_connection, query).fetchall()
            return render_template('orders_driver.html', orders=orders)
    return redirect(url_for('home'))   

@webapp.route('/orders_manager')
def orders_manager():
    if 'email' in session:
        db_connection = connect_to_database()
        email = session['email']
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'F':
            query = 'SELECT orderTime, orderEmail, type, itemName, itemPrice, deliverEmail FROM Final_Orders NATURAL JOIN Final_ConsistOf NATURAL JOIN Final_MenuItems WHERE status = \'P\' AND deliverEmail IS NOT NULL AND foodServiceID IN ( SELECT foodServiceID FROM Final_Addresses NATURAL JOIN Final_FoodServices WHERE email = \'%s\' ) GROUP BY orderID' % (email)
            orders = execute_query(db_connection, query).fetchall()
            return render_template('orders_manager.html', orders=orders)
    return redirect(url_for('home'))   


@webapp.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('cart', None)
    return redirect(url_for('login'))


