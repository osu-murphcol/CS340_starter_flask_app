from flask import Flask, render_template, session, request, redirect, url_for, escape
from db_connector.db_connector import connect_to_database, execute_query
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

nav = Nav()

#create the web application
webapp = Flask(__name__)
webapp.secret_key = 'cs340_2019'

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
        #View('Add Item', 'add_item'),
        View('View Orders', 'orders_manager'),
        View('Change Address', 'change_address'),
        View('Logout', 'logout')
    )

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
                fquery= 'SELECT Final_FoodServices.serviceName, Final_MenuItems.type, Final_MenuItems.itemName, Final_MenuItems.itemPrice FROM Final_MenuItems JOIN Final_FoodServices on Final_MenuItems.foodServiceID = Final_FoodServices.foodServiceID IN(SELECT foodServiceID FROM Final_ConnectTo WHERE email = \'%s\')' % (email)
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

@webapp.route('/home_driver')
def home_driver():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
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
                    for item_id in session['cart']:
                        query = 'SELECT * FROM Final_MenuItems WHERE itemID = \'%s\'' % (item_id)
                        result.append(execute_query(db_connection, query).fetchone())
                    return render_template('cart.html', cart=result)
                else:
                    return render_template('emptycart.html')
            elif request.method=='POST':
                if 'cart' not in session:
                    session['cart'] = []
                cart = session['cart'] 
                cart.append(request.form['item_id'])
                return redirect(url_for('cart')) 
    return redirect(url_for('login')) 

@webapp.route('/remove_item', methods=['POST'])
def remove_item():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT * FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[1] == 'C':
            if request.method=='POST':
                if 'cart' in session:
                    cart = session['cart']
                    print(request.form['item_id'])
                    if request.form['item_id'] in cart: 
                        cart.remove(request.form['item_id'])
    return redirect(url_for('cart')) 


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
            query = 'UPDATE Final_Addresses SET street = \'%s\', zip = \'%s\', city = \'%s\', state = \'%s\' WHERE email = \'%s\'' % (request.form['street'], request.form['zip'], request.form['city'], request.form['state'], email)
            result = execute_query(db_connection, query)
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
            query = 'SELECT * FROM Final_Orders'
            orders = execute_query(db_connection, query).fetchall()
            return render_template('orders_manager.html', orders=orders)
    return redirect(url_for('home'))   


@webapp.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('cart', None)
    return redirect(url_for('login'))


Bootstrap(webapp)
nav.init_app(webapp)

# @webapp.route('/browse_bsg_people')
# #the name of this function is just a cosmetic thing
# def browse_people():
#     print("Fetching and rendering people web page")
#     db_connection = connect_to_database()
#     query = "SELECT fname, lname, homeworld, age, character_id from bsg_people;"
#     result = execute_query(db_connection, query).fetchall();
#     print(result)
#     return render_template('people_browse.html', rows=result)

# @webapp.route('/add_new_people', methods=['POST','GET'])
# def add_new_people():
#     db_connection = connect_to_database()
#     if request.method == 'GET':
#         query = 'SELECT planet_id, name from bsg_planets'
#         result = execute_query(db_connection, query).fetchall();
#         print(result)

#         return render_template('people_add_new.html', planets = result)
#     elif request.method == 'POST':
#         print("Add new people!");
#         fname = request.form['fname']
#         lname = request.form['lname']
#         age = request.form['age']
#         homeworld = request.form['homeworld']

#         query = 'INSERT INTO bsg_people (fname, lname, age, homeworld) VALUES (%s,%s,%s,%s)'
#         data = (fname, lname, age, homeworld)
#         execute_query(db_connection, query, data)
#         return ('Person added!');

# @webapp.route('/db-test')
# #provide a route where requests on the web application can be addressed
# def test_database_connection():
#     print("Executing a sample query on the database using the credentials from db_credentials.py")
#     db_connection = connect_to_database()
#     query = "SELECT * from bsg_people;"
#     result = execute_query(db_connection, query);
#     return render_template('db_test.html', rows=result)

# #display update form and process any updates, using the same function
# @webapp.route('/update_people/<int:id>', methods=['POST','GET'])
# def update_people(id):
#     db_connection = connect_to_database()
#     #display existing data
#     if request.method == 'GET':
#         people_query = 'SELECT character_id, fname, lname, homeworld, age from bsg_people WHERE character_id = %s' % (id)
#         people_result = execute_query(db_connection, people_query).fetchone()

#         if people_result == None:
#             return "No such person found!"

#         planets_query = 'SELECT planet_id, name from bsg_planets'
#         planets_results = execute_query(db_connection, planets_query).fetchall();

#         return render_template('people_update.html', planets = planets_results, person = people_result)
#     elif request.method == 'POST':
#         print("Update people!");
#         character_id = request.form['character_id']
#         fname = request.form['fname']
#         lname = request.form['lname']
#         age = request.form['age']
#         homeworld = request.form['homeworld']

#         print(request.form);

#         query = "UPDATE bsg_people SET fname = %s, lname = %s, age = %s, homeworld = %s WHERE character_id = %s"
#         data = (fname, lname, age, homeworld, character_id)
#         result = execute_query(db_connection, query, data)
#         print(str(result.rowcount) + " row(s) updated");

#         return redirect('/browse_bsg_people')

# @webapp.route('/delete_people/<int:id>')
# def delete_people(id):
#     '''deletes a person with the given id'''
#     db_connection = connect_to_database()
#     query = "DELETE FROM bsg_people WHERE character_id = %s"
#     data = (id,)

#     result = execute_query(db_connection, query, data)
#     return (str(result.rowcount) + "row deleted")
