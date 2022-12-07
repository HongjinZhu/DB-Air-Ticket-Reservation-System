from flask import Flask, render_template, request, url_for, redirect, session
import pymysql.cursors
import datetime
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from werkzeug.security import generate_password_hash,check_password_hash
plt.switch_backend('Agg') 
#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airticket',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
@app.route('/')
def welcome():
    # session.clear()
	return render_template('welcome.html')

@app.route('/upcoming_flight',methods=['GET', 'POST'])
def upcoming_flight():
	cursor = conn.cursor()
	query = "SELECT * FROM Flight where flight_status = 'upcoming'"
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	try:
		if session['username']:
			username = session["username"]
			role = session["role"]
			print(role)
			return render_template("upcoming_flight.html", upcoming_flight = data, role = role,username = username)
        # have not initialize
		else:
			return render_template("upcoming_flight.html", upcoming_flight=data, role =session["role"],username = session["username"])
	except KeyError:
		return render_template('upcoming_flight.html', upcoming_flight = data)

@app.route('/login',methods=['GET', 'POST'])
def login():
    # session.clear()
    return render_template('login.html')

@app.route('/customer_register',methods=['GET', 'POST'])
def register_customer():
	return render_template('customer_register.html')

@app.route('/staff_register',methods=['GET', 'POST'])
def register_staff():
	query = "select name from airline"
	cursor = conn.cursor()
	cursor.execute(query)
	
	airline = cursor.fetchall()
	cursor.close()
	airlines = []
	for i in airline:
		airlines.append(i['name'])
	print(airlines)
	return render_template('staff_register.html',airlines = airlines)

@app.route('/agent_register',methods=['GET', 'POST'])
def register_agent():
	return render_template('agent_register.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
# request.form[name] \name/ should be the name in the html file 
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	role = request.form['role']

	if role == "Customer":
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = "SELECT * FROM customer WHERE email = '{}'"
		cursor.execute(query.format(username))
		#stores the results in a variable
		db_password = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()

		error = None
		if(db_password):
			#creates a session for the the user
			#session is a built in
			db_password = db_password["c_password"]
			hashed_db_password = generate_password_hash(db_password)
			flag = check_password_hash(hashed_db_password,password)
			if flag:
				# session['username'] = username
				# session['role'] = role
				# session.permanent = True
				return redirect(url_for('customer_home',customer_email = username))
			else:
				error = 'Wrong password'
			return render_template('login.html', error=error)
		else:
			#returns an error message to the html page
			error = 'Invalid login name'
			return render_template('login.html', error=error)
			
	#Looks Okay============
	elif role =="Airline Staff":
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = "SELECT * FROM airlineStaff WHERE username = '{}'"
		cursor.execute(query.format(username))
		#stores the results in a variable
		db_password = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()
		error = None
		if(db_password):
			db_password = db_password["s_password"]
			flag = check_password_hash(db_password,password)
			if flag:
				#creates a session for the the user
				#session is a built in
				session['username'] = username
				session['role'] = role
				cursor = conn.cursor()
				query_permission = "SELECT permission from permission where permission.username = '{}'"
				cursor.execute(query_permission.format(username))
				permission =  cursor.fetchall()

				query_company = "select airline_name from airlineStaff where airlineStaff.username = '{}' "
				cursor.execute(query_company.format(username))
				company =  cursor.fetchall()
				cursor.close()
				# session['status'] = data[0]["permission_type"]
				session['status'] = []
				for i in permission:
					session['status'].append(i['permission'])
				session['company'] = company[0]['airline_name']
				print(session['status'],session["company"])
				session.permanent = True
				return redirect(url_for('staff_home', staff_email = username))
			else:
				error = 'Wrong password'
				return render_template('login.html', error=error)
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

	elif role =="Booking agent":
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = "SELECT * FROM bookingagent WHERE email = '{}'"
		cursor.execute(query.format(username))
		#stores the results in a variable
		db_password = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		cursor.close()
		error = None
		if(db_password):
			db_password = db_password["b_password"]
			flag = check_password_hash(db_password,password)
			if flag:
				#creates a session for the the user
				#session is a built in
				session['username'] = username
				session['role'] = role
				session.permanent = True

				# get the company that the agent works for
				cursor = conn.cursor()
				#executes query
				query = "SELECT airline_name from bookingagent WHERE email = '{}'"
				cursor.execute(query.format(username))
				#stores the results in a variable
				companyAll = cursor.fetchall()
				#use fetchall() if you are expecting more than 1 data row
				cursor.close()
				session['company'] = []
				for i in companyAll:
					session['company'].append(i['airline_name'])
				# print('HERE!!', session['company'])
				return redirect(url_for('agent_home', agent_email = username))
			else:
				error = 'Wrong password'
				return render_template('login.html', error=error)
		else:
			#returns an error message to the html page
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

@app.route('/registerAuth_customer', methods=['GET', 'POST'])
def registerAuth_customer():
	try:
		#grabs information from the forms
		email = request.form['email']
		password = request.form['password']
		password2 = request.form['password2']
		#cursor used to send queries
		cursor = conn.cursor()
		
		#executes query
		query = "SELECT * FROM customer WHERE email = '{}'"
		cursor.execute(query.format(email))
		#stores the results in a variable
		data = cursor.fetchone()
		print(data)
		#use fetchall() if you are expecting more than 1 data row
		error = None
		if password != password2:
			error = "Password does not match"
			return render_template('customer_register.html', error = error)
		elif(data):
			#If the previous query returns data, then user exists
			error = "This user already exists"
			return render_template('customer_register.html', error = error)
		else:

			# how to store multivalue
			# how to store as DATE
			username = request.form["username"]
			birthday = request.form["birthday"]
			state = request.form["state"]
			city = request.form["city"]
			street = request.form["street"]
			building = request.form["building"]
			passport_num = request.form["passport number"]
			passport_country = request.form["Passport Country"]
			expiration = request.form["expiration date"]
			phone = int(request.form["phone"])
			ins = "INSERT INTO customer VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
			password = generate_password_hash(password)
			print(len(password))
			cursor.execute(ins.format(email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday))
			conn.commit()
			cursor.close()
			return render_template('customer_register.html',success = username)
	except:
		return render_template('customer_register.html',error = "Wrong Input")

@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
	try:
		email = request.form['email']
		password = request.form['password']
		password2 = request.form['password2']
		airlineName = request.form['airlineName']

		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query_email = "SELECT * FROM booking_agent WHERE email = '{}' "
		cursor.execute(query_email.format(email))
		#stores the results in a variable
		data1 = cursor.fetchone()
		#use fetchall() if you are expecting more than 1 data row
		#decide whether user already exist
		error = None

		if data1 != None:
			error = 'User already exists.'
			return render_template('agent_register.html', error = error)

		# #return a list of airline names
		# query_airline = 'SELECT * FROM airline WHERE airline_name = %s'
		# cursor.execute(query_airline, (airline_name))
		# #stores the results in a variable
		# data2 = cursor.fetchone()

		# if data2 == None:
		#     error = 'Airline name does not exist in the database.'
		#     return render_template('agent_register.html', error = error)

		if password != password2:
			error = "Passwords do not match"
			return render_template('agent_register.html', error = error)

		# if(data1):
		# 	#If the previous query returns data, then user exists
		# 	error = "This user already exists"
		# 	return render_template('agent_register.html', error = error)
		else:
			query = "select max(booking_agent_id) from booking_agent"
			cursor.execute(query)
			booking_agent_id = cursor.fetchone()
			print(booking_agent_id)

			if booking_agent_id[max(booking_agent_id)]:
				id = booking_agent_id[max(booking_agent_id)] + 1
			else:
				id = 1
			print(email,password,id,airlineName)
			password = generate_password_hash(password)
			ins1 = "INSERT INTO booking_agent VALUES('{}', '{}', '{}','{}')"
			cursor.execute(ins1.format(email, password, id,airlineName))

			# ins2 = 'INSERT INTO booking_agent_work_for VALUES(%s, %s)'
			# cursor.execute(ins2, (email, airline_name))
			
			
			conn.commit()
			cursor.close()
			return render_template('agent_register.html',id = id) 
	except:
		return render_template('agent_register.html', error = "Invalid Input")

@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
	query = "select airline_name from airline"
	cursor = conn.cursor()
	cursor.execute(query)
	airline = cursor.fetchall()
	cursor.close()
	airlines = []
	for i in airline:
		airlines.append(i['airline_name'])

	# try:
	#grabs information from the forms
	#Here username is this person's email
	username = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']
	airline_name = request.form["airline_name"]
	print("airline_name: ",airline_name)

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	#here username is this person's email
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row

	query_airline = 'SELECT * FROM airline WHERE airline_name = %s'
	cursor.execute(query_airline, airline_name)
	print(airline_name)
	data2 = cursor.fetchone()

	error = None

	if data2 == None:
		error = 'Airline name does not exist in the database.'
		return render_template('staff_register.html', error = error,airlines = airlines)

	if password != password2:
		error = "Password does not match"
		return render_template('staff_register.html', error = error,airlines = airlines)

	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staff_register.html', error = error,airlines = airlines)

	else:
		firstName = request.form["first_name"]
		lastName = request.form["last_name"]
		d_birth = request.form['date_of_birth']
		birthday = datetime.datetime.strptime(d_birth,'%Y-%m-%d')
		password = generate_password_hash(password)
		ins1 = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins1, (username, airline_name, password, firstName, lastName, birthday))

		ins2 = 'INSERT INTO permission VALUES(%s, %s)'
		cursor.execute(ins2, (username,''))

		conn.commit()
		cursor.close()
		return render_template('staff_register.html',success = username,airlines = airlines)

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
