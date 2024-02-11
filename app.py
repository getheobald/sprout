from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_mysqldb import MySQL
import random
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2122.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2122'
app.config['MYSQL_PASSWORD'] = 'm545CS42122'
app.config['MYSQL_DB'] = '2122project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 's3cr3tk3yth4tisnotjustr4ndom13tt3rsb3c4us3th4tisboth3rsom3'
mysql = MySQL(app)

#code explained by ms. o'neal
#and obtained from https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
#any page with the login_required decorator will only load if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('gracetheobald_username') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#landing page
#from here user either has to enter their information or go to sign up page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        #display log in page
        return render_template('login.html', error=request.args.get('error'))
    if request.method == 'POST':
        #user has entered account info
        username = request.values.get("username")
        password = request.values.get("password")
        cursor = mysql.connection.cursor()
        query = "SELECT password FROM gracetheobald_users WHERE username=%s;"
        queryVars = (username,)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        queryResults = cursor.fetchall()
        #I learned most of this code from the login system mini lesson
        if (len(queryResults) == 1):
            securedPassword = queryResults[0]['password']
            if check_password_hash(securedPassword, password):
                session['gracetheobald_username'] = username
                return redirect(url_for('home'))
            else: #password was wrong
                return redirect(url_for('login', error=True))
        else: #username doesn't exist
            return redirect(url_for('login', error=True))

#sign up page
#from sign up button on landing page (log in page)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='GET':
        #display sign up page
        return render_template('signup.html')
    if request.method=='POST':
        #user has signed up for an account
        first_name = request.values.get("first_name")
        last_name = request.values.get("last_name")
        username = request.values.get("username")
        email = request.values.get("email")
        password = request.values.get("password")
        securePassword = generate_password_hash(password)
        cursor = mysql.connection.cursor()
        query = "INSERT INTO gracetheobald_users (first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s);"
        queryVars = (first_name, last_name, username, email, securePassword)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        data = cursor.fetchall()
        session['gracetheobald_username'] = username
        return redirect(url_for('home'))

#home page
#user lands here afting logging in or signing up
#can be accessed from logo button at the top of every page
@app.route('/', methods=['GET'])
@login_required
def home():
    cursor = mysql.connection.cursor()
    query = "SELECT id FROM gracetheobald_plants;"
    cursor.execute(query)
    mysql.connection.commit()
    queryResults = cursor.fetchall()
    numPlants = len(queryResults)
    chosenPlantNum = random.randint(0, numPlants-1)
    chosenPlantId = queryResults[chosenPlantNum]['id']
    cursorTwo = mysql.connection.cursor()
    queryTwo = "SELECT * FROM gracetheobald_plants WHERE id=%s;"
    queryVarsTwo = (chosenPlantId,)
    cursorTwo.execute(queryTwo, queryVarsTwo)
    mysql.connection.commit()
    queryResultsTwo = cursorTwo.fetchall()
    plantData = queryResultsTwo
    return render_template('home.html', plantData=plantData)

#garden page
#routes from button at the top of every page
@app.route('/garden', methods=['GET', 'POST'])
@login_required
def garden():
    if request.method=='GET':
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM gracetheobald_userplants up JOIN gracetheobald_plants p ON p.id=up.plants_id WHERE up.users_id IN (SELECT id FROM gracetheobald_users WHERE username=%s);"
        queryVars = (session.get('gracetheobald_username'),)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        queryResults = cursor.fetchall()
        return render_template('garden.html', queryResults=queryResults, username=session.get('gracetheobald_username'))
    if request.method=='POST':
        return render_template('garden.html')

#pre-filled plant add page
#get here from link on garden page
@app.route('/addplant', methods=['GET', 'POST'])
@login_required
def addplant():
    if request.method=='GET':
        cursor = mysql.connection.cursor()
        query = "SELECT common_name, latin_name FROM gracetheobald_plants"
        cursor.execute(query)
        mysql.connection.commit()
        queryResults = cursor.fetchall()
        return render_template('addplant.html', queryResults=queryResults)
    if request.method=='POST':
        plant = request.values.get("plant")
        date = request.values.get("date")
        room = request.values.get("room")
        nickname = request.values.get("nickname")
        note = request.values.get("note")
        cursor = mysql.connection.cursor()
        query = "INSERT INTO gracetheobald_userplants (users_id, plants_id, date, room, nickname, note) VALUES ((SELECT id FROM gracetheobald_users WHERE username=%s), (SELECT id FROM gracetheobald_plants WHERE latin_name=%s), %s, %s, %s, %s);"
        queryVars = (session.get('gracetheobald_username'), plant, date, room, nickname, note)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        queryResults = cursor.fetchall()
        return redirect(url_for('garden'))

#manual plant add page
#get here from link on automatic page
@app.route('/addplantmanual', methods=['GET', 'POST'])
@login_required
def addplantmanual():
    if request.method=='GET':
        return render_template('addplantmanual.html')
    if request.method=='POST':
        #set up queries by getting all variables
        commonName = request.values.get("common_name")
        latinName = request.values.get("latin_name")
        water = request.values.get("water")
        fertilize = request.values.get("fertilize")
        sun = request.values.get("sun")
        propagate = request.values.getlist("propagate")
        propagate = ", ".join(propagate)
        image = request.values.get("image")
        date = request.values.get("date")
        room = request.values.get("room")
        nickname = request.values.get("nickname")
        note = request.values.get("note")
        cursor = mysql.connection.cursor()
        #first query where I add the plant to the plants database
        query = "INSERT INTO gracetheobald_plants (common_name, latin_name, water, fertilize, sun, propagate, image) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        queryVars = (commonName, latinName, water, fertilize, sun, propagate, image)
        cursor.execute(query, queryVars)
        #use the id of the plant that was just created to assign it to the user along with some other info
        queryTwo = "INSERT INTO gracetheobald_userplants (users_id, plants_id, date, room, nickname, note) VALUES ((SELECT id FROM gracetheobald_users WHERE username=%s), (SELECT id FROM gracetheobald_plants WHERE latin_name=%s), %s, %s, %s, %s);"
        queryVarsTwo = (session.get('gracetheobald_username'), latinName, date, room, nickname, note)
        cursor.execute(queryTwo, queryVarsTwo)
        #final stuff to run both queries
        mysql.connection.commit()
        return redirect(url_for('garden'))

#remove plant page
#get here from link on garden page
@app.route('/removeplant', methods=['GET', 'POST'])
@login_required
def removeplant():
    if request.method=='GET':
        cursor = mysql.connection.cursor()
        query = "SELECT common_name, latin_name, nickname FROM gracetheobald_userplants up JOIN gracetheobald_plants p ON p.id=up.plants_id WHERE up.users_id IN (SELECT id FROM gracetheobald_users WHERE username=%s);"
        queryVars = (session.get('gracetheobald_username'),)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        queryResults = cursor.fetchall()
        return render_template('removeplant.html', queryResults=queryResults)
    if request.method=='POST':
        plant = request.values.get("plant")
        data = plant.split(", ")
        latin_name = data[0]
        nickname = data[1]
        cursor = mysql.connection.cursor()
        query = "DELETE FROM gracetheobald_userplants WHERE plants_id=(SELECT id FROM gracetheobald_plants WHERE latin_name=%s) AND nickname=%s;"
        queryVars = (latin_name, nickname)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
        return redirect(url_for('garden'))

#profile page
#routes from button at the top of every page
#currently not in use (nothing on it and no way to get to it)
#but I'm leaving it here because I do think it would be cool to have
#a profile page at some point if I ever expand on this
@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')

#logs user out on click of logout button
@app.route('/logout')
def logout():
    session.pop('gracetheobald_username', None)
    return redirect(url_for('login'))
