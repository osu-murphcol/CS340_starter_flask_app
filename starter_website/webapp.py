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
        View('Change Address', 'change_address'),
        View('Logout', 'logout')
    )

@nav.navigation()
def nav_manager():
    return Navbar(
        'Food Delivery Inc.',
        View('Home', 'home_manager'),
        View('Add Item', 'add_item'),
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

@webapp.route('/home_manager', methods=['POST','GET'])
def home_manager():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT type FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[0] == 'F':
            if request.method=='GET':
                fquery= 'SELECT * FROM Final_MenuItems WHERE foodServiceID IN (SELECT foodServiceID FROM Final_ConnectTo WHERE email = \'%s\')' % (email)
                fresult = execute_query(db_connection, fquery).fetchall()
                fSIDquery= 'SELECT foodServiceID FROM Final_ConnectTo WHERE email = \'%s\'' % (email)
                fSIDresult = execute_query(db_connection, fSIDquery).fetchall()
                result_fSIDs = [row[0] for row in fSIDresult]
                return render_template('home_manager.html', user=result, foods=fresult, fSIDs=result_fSIDs)
            elif request.method == 'POST':
                session['ItemID'] = request.form['ItemID']
                ItemID = session['ItemID']
                session['Type'] = request.form['Type']
                Type = session['Type']
                session['fSID'] = request.form['fSID']
                fSID = session['fSID']
                session['itemName'] = request.form['itemName']
                itemName = session['itemName']
                session['itemPrice'] = request.form['itemPrice']
                itemPrice = session['itemPrice']
                db_connection = connect_to_database()
                query = 'INSERT INTO Final_MenuItems VALUES (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (ItemID,Type,fSID,itemName,itemPrice)
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
        query = 'SELECT type FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[0] == 'D':
            return render_template('home_driver.html', user=result)  
    return redirect(url_for('login'))

@webapp.route('/home_customer')
def home_customer():
    if 'email' in session:
        email = session['email']
        db_connection = connect_to_database()
        query = 'SELECT type FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[0] == 'C':
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
        query = 'SELECT type FROM Final_Users WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if result[0] == 'C':
            return render_template('cart.html')
    return redirect(url_for('login')) 

#@webapp.route('/customer')
#def add_item():


@webapp.route('/change_address', methods=['POST','GET'])
def change_address():
    if 'email' in session:
        db_connection = connect_to_database()
        email = session['email']
        query = 'SELECT * FROM Final_Addresses WHERE email = \'%s\'' % (email)
        result = execute_query(db_connection, query).fetchone()
        if request.method=='GET': 
            return render_template('change_address.html', address=result)
        if request.method=='POST':
            query = 'UPDATE Final_Addresses SET street = \'%s\', zip = \'%s\', city = \'%s\', state = \'%s\' WHERE email = \'%s\'' % (request.form['street'], request.form['zip'], request.form['city'], request.form['state'], email)
            result = execute_query(db_connection, query)
            return redirect(url_for('change_address'))   
    return redirect(url_for('login'))   

@webapp.route('/logout')
def logout():
    session.pop('email', None)
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
