from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from flask_bootstrap import Bootstrap
import smtplib
from email.message import EmailMessage
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

app = Flask(__name__)
global email
    
bootstrap = Bootstrap(app) 
app.secret_key = 'a'

  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'dharsh'
app.config['MYSQL_PASSWORD'] = 'y7SaG8yR5o'
app.config['MYSQL_DB'] = 'dharsh'

mysql = MySQL(app)

def send_email(email):
    sg = sendgrid.SendGridAPIClient('Sendgrid api key')
    from_email = Email("dharshdummy@gmail.com")  # Change to your verified sender
    to_email = To(email)  # Change to your recipient
    subject = "Alert! You are in a Containment zone"
    content = Content("text/plain", "You are in a Containment zone. Move out to a safer zone and take preventive measures. Get tested to check if you are infected too for the safety of your family members and friends. Get vaccinated too. Stay safe!")
    mail = Mail(from_email, to_email, subject, content)      
    # Get a JSON-ready representation of the Mail object
    print("MAIL JSON")
    mail_json = mail.get()
    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    #print("ReSPONSE STATUS CODE LINE")
    print(response.status_code)
    #print("Body")
    print(response.body)
    #print("Headers")
    print(response.headers)

def check_if_in_zone(email):
    email=email
    user=get_user_details()
    cur = mysql.connection.cursor()
    cur.execute(f'SELECT * FROM zones WHERE pincode={user[3]}')
    mysql.connection.commit()
    dataa = cur.fetchall()
    list_of_locations=[]
    for x in dataa:
        x=list(x)
        x[-1]=0
        list_of_locations.append(x)
    if user in list_of_locations:
        send_email(email)
    

def get_user_details():
    res = requests.get('https://ipinfo.io/')
    dataa = res.json()
    city=dataa['city']
    pincode=int(dataa['postal'])
    location = dataa['loc'].split(',')
    latitude = location[0]
    latitude=float(latitude[0:5])
    longitude = location[1]
    longitude=float(longitude[0:5])
    user=[latitude, longitude, city, pincode, 0]
    return user    


@app.route('/')
def homer():
    return render_template('base.html')

   
@app.route('/log', methods =['GET', 'POST'])
def register():
    global email
    msg = ''
    if request.method == 'POST' :
      
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tab WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
            return render_template('log.html', msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            return render_template('log.html', msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
            return render_template('log.html', msg=msg)
        else:
            cursor.execute('INSERT INTO tab VALUES (% s, % s, % s)', (username,password,email))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('signin.html', msg=msg)
    
    return render_template('log.html', msg = msg)

@app.route('/reg',methods =['GET', 'POST'])
def login():
    global email
    msg = ''
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tab WHERE username = % s AND password = % s', (username, password ),)
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            
            msg = 'Logged in successfully !'
            return render_template('main.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('signin.html', msg = msg)


@app.route('/host', methods=['POST', 'GET'])
def admin_login():
    global email
    msg = ''
    if request.method == 'POST' :
        username = request.form['uname']
        password = request.form['pwd']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = % s AND password = % s', (username, password))
        account = cursor.fetchone()
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=account[0]
            session['uname'] = account[1]
            msg = 'Logged in successfully !'
            return render_template('logged.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('host.html', msg = msg)

@app.route('/loc', methods=['POST'])   
def main_html():
    if request.method == 'POST':
        email=request.form.get("mail")
        if email:
            check_if_in_zone(email)
            res = requests.get('https://ipinfo.io/')
            dataa = res.json()
            city=dataa['city']
            return render_template('location.html', city=city)
    return render_template('main.html')

@app.route('/check',methods =['GET', 'POST'])
def display():
    #######################THIS IS WHERE THE FUN BEGINS
    #############CHECK IF THE USER'S CURRENT LOCATION IS IN THE DATABASE LOVE to send the email
    ################just a few other minor changes
    res = requests.get('https://ipinfo.io/')
    dataa = res.json()
    city=dataa['city'] 
    return render_template('location.html', city=city)
    
  # print("its a zone")
            # print(mail)
            # message = "You are in containment zone .Please take care and be SAFE!!!USE Sanitizer and wear MASK."
            # msg = 'Subject:{}\n\n'.format("Alerting mail",message)
            # server = smtplib.SMTP("smtp.gmail.com",587)
            # server.set_debuglevel(1)
            # server.ehlo()
            # server.starttls()
            # server.ehlo()
            # server.login("cozo.containmentzone@gmail.com", "covid19cozo")
            # server.ehlo()
            # server.sendmail("cozo.containmentzone@gmail.com", mail, msg)
            # server.quit()
    
@app.route('/table')
def table():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM zones")
    data = cur.fetchall()
    return render_template('table.html', data=data)

@app.route('/addzone', methods=['GET', 'POST'])
def add_zone():
    if request.method == 'POST' :
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        city = request.form['city']
        pincode = request.form['pincode']
        number= 'NULL'
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO zones VALUES (% s, % s, % s, % s, %s)', (latitude, longitude, city, pincode,number))
        mysql.connection.commit()
        return render_template('success.html')
      
    return render_template('addzone.html')

@app.route('/getpincode', methods=['GET','POST'])
def get_pin_code():
    if request.method=='POST':
        pincode=request.form['pincode']
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM zones WHERE pincode={pincode}')
        mysql.connection.commit()
        data = cur.fetchall()
        return render_template('display_for_pincode.html', data=data)
        
    return render_template('get_pincode.html')   



@app.route('/removezone', methods=['GET', 'POST'])
def remove_zone():
    if request.method== 'POST':
        # latitude = request.form['latitude']
        # longitude = request.form['longitude']
        # city = request.form['city']
        number = request.form['number']
        cur = mysql.connection.cursor()
        cur.execute(f'DELETE FROM zones WHERE number={number}')
        mysql.connection.commit()
        return render_template('success.html')
        
        # cur.execute('SELECT id FROM ')
        # cur.execute(f'DELETE FROM zones WHERE latitude={latitude} AND longitude={longitude}  AND pincode={pincode}')
        # mysql.connection.commit()
    
    return render_template('removezone.html')



@app.route('/link')
def link():
    return render_template('links.html')

##############################################################
#######################################################
#############################################################

@app.route("/android_sign_up", methods=["POST"])
def upload():
    if(request.method == "POST"):

        # get the data from the form
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        # hash the password
        #pw_hash = create_bcrypt_hash(password)

        # initialize the cursor
        signup_cursor = mysql.connection.cursor()

        # check whether user already exists
        user_result = signup_cursor.execute(
            "SELECT * FROM tab WHERE email=%s", [email]
        )
        if(user_result > 0):
            signup_cursor.close()
            return {'status': 'failure'}
        else:
            # execute the query
            signup_cursor.execute(
                'INSERT INTO tab (username,password,email) VALUES(%s,%s,%s)', (
                    name,password,email)
                )

            mysql.connection.commit()
            id_result = signup_cursor.execute(
                'SELECT username FROM tab WHERE email = %s', [email]
            )
            if(id_result > 0):
                id = signup_cursor.fetchone()
                return {"id": id[0]}
            signup_cursor.close()

    return {"status": "failure"}

##########################################################
##########################################################


if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True,port = 8080)
