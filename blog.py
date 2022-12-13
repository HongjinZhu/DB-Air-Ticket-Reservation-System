from flask import Flask, render_template, request, url_for, redirect, session
import pymysql.cursors
import datetime
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from werkzeug.security import generate_password_hash,check_password_hash

plt.switch_backend('Agg')
app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airticket',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

###############################################################################################################
#                                                Public Space                                                 #
###############################################################################################################
@app.route('/')
def welcome():
	session.clear()
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
			return render_template("upcoming_flight.html", upcoming_flight = data, role = role,username = username)

		else:
			return render_template("upcoming_flight.html", upcoming_flight=data, role =session["role"],username = session["username"])
	except KeyError:
		return render_template('upcoming_flight.html', upcoming_flight = data)

@app.route('/upcoming_flight/search', methods=['GET', 'POST'])
def upcoming_flight_search():
	query = "SELECT * from flight where "
	appendix = ""
	if request.form['departure_date']:
		d_date = request.form['departure_date']
		d_start = datetime.datetime.strptime(d_date, '%Y-%m-%d')
		d_end = d_start + datetime.timedelta(days=1)
		add = "and '" + str(d_start)[:10] + "' <=depart_time  and depart_time <='" + str(d_end)[:10] + "'"
		appendix += add
	if request.form['arrival_date']:
		a_date = request.form['arrival_date']
		a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
		a_end = a_start + datetime.timedelta(days=1)
		dd = "and '" + str(a_start)[:10] + "' <=arrive_time  and arrive_time <='" + str(a_end)[:10] + "'"
		appendix += dd
	if request.form['flight']:
		flight_num = request.form['flight']
		appendix += "and flight_num = '"+flight_num+"'"
	if request.form['departure_airport']:
		d_airport = request.form['departure_airport']
		appendix += "and depart_name = '"
		appendix += d_airport
		appendix += "'"
	if request.form['arrival_airport']:
		a_airport = request.form['arrival_airport']
		appendix += "and arrive_name = '"
		appendix += a_airport
		appendix += "'"
	if request.form['departure_city']:
		d_city = request.form['departure_city']
		add = "and depart_name in (select name from airport where city ='" + d_city + "')"
		appendix += add
	if request.form['arrival_city']:
		a_city = request.form['arrival_city']
		add = "and arrive_name in (select name from airport where city = '" + a_city + "')"
		appendix += add
	if appendix == "":
		query = "SELECT * from flight"
	else:
		query += appendix[3:]
	cursor = conn.cursor()
	cursor.execute(query)
	data = cursor.fetchall()
	cursor.close()
	error = None
	if (data):
		return render_template('upcoming_flight.html', upcoming_flight=data)
	else:
		return render_template('upcoming_flight.html',
								error1="Sorry, no flights are found. Please check your input again.")


@app.route('/login',methods=['GET', 'POST'])
def login():
    session.clear()
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
	return render_template('staff_register.html',airlines = airlines)

@app.route('/agent_register',methods=['GET', 'POST'])
def register_agent():
	query = "select name from airline"
	cursor = conn.cursor()
	cursor.execute(query)
	
	airline = cursor.fetchall()
	cursor.close()
	airlines = []
	for i in airline:
		airlines.append(i['name'])
	return render_template('agent_register.html', airlines = airlines)

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	username = request.form['username']
	password = request.form['password']
	role = request.form['role']

	if role == "Customer":
		cursor = conn.cursor()
		query = "SELECT * FROM customer WHERE email = '{}'"
		cursor.execute(query.format(username))
		db_password = cursor.fetchone()
		cursor.close()

		error = None
		if(db_password):
			db_password = db_password["c_password"]
			flag = check_password_hash(db_password,password)
			if flag:
				session['username'] = username
				session['role'] = role
				session.permanent = True
				return redirect(url_for('customer_home',customer_email = username))
			else:
				error = 'Wrong password'
			return render_template('login.html', error=error)
		else:
			error = 'Invalid login name'
			return render_template('login.html', error=error)

	elif role =="Airline Staff":
		cursor = conn.cursor()
		query = "SELECT * FROM airlineStaff WHERE username = '{}'"
		cursor.execute(query.format(username))
		db_password = cursor.fetchone()
		cursor.close()
		error = None
		if(db_password):
			db_password = db_password["s_password"]
			flag = check_password_hash(db_password,password)
			if flag:
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
				session['status'] = []
				for i in permission:
					session['status'].append(i['permission'])
				session['company'] = company[0]['airline_name']
				session.permanent = True
				return redirect(url_for('staff_home', staff_email = username))
			else:
				error = 'Wrong password'
				return render_template('login.html', error=error)
		else:
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

	elif role =="Booking agent":
		cursor = conn.cursor()
		query = "SELECT * FROM bookingagent WHERE email = '{}'"
		cursor.execute(query.format(username))
		db_password = cursor.fetchone()
		cursor.close()
		error = None
		if(db_password):
			db_password = db_password["b_password"]
			flag = check_password_hash(db_password,password)
			if flag:
				session['username'] = username
				session['role'] = role
				session.permanent = True

				cursor = conn.cursor()
				query = "SELECT airline_name from bookingagent WHERE email = '{}'"
				cursor.execute(query.format(username))
				companyAll = cursor.fetchall()
				cursor.close()
				session['company'] = []
				for i in companyAll:
					session['company'].append(i['airline_name'])
				return redirect(url_for('agent_home', agent_email = username))
			else:
				error = 'Wrong password'
				return render_template('login.html', error=error)
		else:
			error = 'Invalid login or username'
			return render_template('login.html', error=error)

@app.route('/registerAuth_customer', methods=['GET', 'POST'])
def registerAuth_customer():
	try:
		email = request.form['email']
		password = request.form['password']
		password2 = request.form['password2']
		cursor = conn.cursor()
		
		query = "SELECT * FROM customer WHERE email = '{}'"
		cursor.execute(query.format(email))
		data = cursor.fetchone()
		error = None
		if password != password2:
			error = "Password does not match"
			return render_template('customer_register.html', error = error)
		elif(data):
			error = "This user already exists"
			return render_template('customer_register.html', error = error)
		else:
			username = request.form["username"]
			birthday = request.form["birthday"]
			state = request.form["state"]
			city = request.form["city"]
			street = request.form["street"]
			building = request.form["building"]
			passport_num = request.form["passport number"]
			passport_country = request.form["Passport Country"]
			expiration = request.form["expiration date"]
			phone = request.form["phone"]
			ins = "INSERT INTO customer VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
			password = generate_password_hash(password)
			cursor.execute(ins.format(email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday))
			conn.commit()
			cursor.close()
			return render_template('customer_register.html',success = username)
	except:
		return render_template('customer_register.html',error = "Wrong Input")

@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
	query = "select name from airline"
	cursor = conn.cursor()
	cursor.execute(query)
	airline = cursor.fetchall()
	cursor.close()
	airlines = []
	for i in airline:
		airlines.append(i['name'])
		
	email = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']
	airlineName = request.form['airlineName']
	id = request.form['b_id']

	
	cursor = conn.cursor()
	query_email = "SELECT * FROM bookingagent WHERE email = '{}' "
	cursor.execute(query_email.format(email))
	data1 = cursor.fetchone()

	query_airline = "SELECT * FROM airline WHERE name = '{}'"
	cursor.execute(query_airline.format(airlineName))
	data2 = cursor.fetchone()

	query_id = "SELECT b_id FROM bookingagent WHERE b_id = '{}'"
	cursor.execute(query_id.format(id))
	data3 = cursor.fetchone()
	error = None

	if data1 != None:
		error = 'User already exists.'
		return render_template('agent_register.html', error = error)

	if data2 == None:
		error = 'Airline name does not exist in the database.'
		return render_template('agent_register.html', error = error)

	if data3 != None:
		error = 'ID already exists.'
		return render_template('agent_register.html', error = error)

	if password != password2:
		error = "Passwords do not match"
		return render_template('agent_register.html', error = error)
	
	else:
		password = generate_password_hash(password)
		ins1 = "INSERT INTO bookingagent VALUES('{}', '{}', '{}','{}')"
		cursor.execute(ins1.format(email, password, id, airlineName))
		
		conn.commit()
		cursor.close()
		return render_template('agent_register.html',id = id, airlines = airlines)

@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
	query = "select name from airline"
	cursor = conn.cursor()
	cursor.execute(query)
	airline = cursor.fetchall()
	cursor.close()
	airlines = []
	for i in airline:
		airlines.append(i['name'])

	username = request.form['email']
	password = request.form['password']
	password2 = request.form['password2']
	airlineName = request.form["airlineName"]

	cursor = conn.cursor()
	query = "SELECT * FROM airlinestaff WHERE username = '{}'"
	cursor.execute(query.format(username))
	data = cursor.fetchone()

	query_airline = "SELECT * FROM airline WHERE name = '{}'"
	cursor.execute(query_airline.format(airlineName))
	data2 = cursor.fetchone()

	error = None

	if data2 == None:
		error = 'Airline name does not exist in the database.'
		return render_template('staff_register.html', error = error,airlines = airlines)

	if password != password2:
		error = "Password does not match"
		return render_template('staff_register.html', error = error,airlines = airlines)

	if(data):
		error = "This user already exists"
		return render_template('staff_register.html', error = error,airlines = airlines)

	else:
		firstName = request.form["first_name"]
		lastName = request.form["last_name"]
		d_birth = request.form['date_of_birth']
		birthday = datetime.datetime.strptime(d_birth,'%Y-%m-%d')
		password = generate_password_hash(password)
		ins1 = 'INSERT INTO airlinestaff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins1, (username, airlineName, password, firstName, lastName, birthday))

		ins2 = 'INSERT INTO permission VALUES(%s, %s)'
		cursor.execute(ins2, (username,''))

		conn.commit()
		cursor.close()
		return render_template('staff_register.html',success = username,airlines = airlines)

###############################################################################################################
#                                                Customer                                                     #
###############################################################################################################

@app.route("/customer_home/<customer_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/customer_home/<customer_email>/<error>", methods=["GET", "POST"])
def customer_home(customer_email,error):
	month = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sep","Oct","Nov","Dec"]

	if session['username'] != customer_email:
		print("case1")
		return render_template("login.html", error="Bad Request")
	
	# default view my flights
	try:
		query = 'select * from flight where flight_status ="upcoming" and (flight_num) in (select flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s))'
		cursor = conn.cursor()
		cursor.execute(query,session['username'])
		data =  cursor.fetchall()
		# print('jiuming')
		cursor.close()

		# default spending  
		cur = datetime.date.today()
		year_ago  = cur - datetime.timedelta(days=365)
		query = 'select * from flight where (flight_num) in (select flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where customer_email = %s and p_date <= %s and p_date >= %s)) '
		cursor = conn.cursor()
		cursor.execute(query,(session['username'],cur,year_ago))
		money =  cursor.fetchall()
		cursor.close()

		year_money = 0
		for i in money:
			year_money += i['price']

		# print('here')
		# default draw an image
		query = """SELECT price, p_date 
			FROM ticket NATURAL JOIN purchases NATURAL JOIN flight 
			WHERE purchases.customer_email = '%s'"""
		cursor = conn.cursor()
		cursor.execute(query % session['username'])
		info = cursor.fetchall()
		cursor.close()

		half_ago = cur - datetime.timedelta(days=183)
		# print('half',half_ago)
		last_month = cur.month
		begin_month = last_month-6
		spent = [0 for i in range(6)]
		# print(cur)
		# print(half_ago)
		for record in info:
			# print(record['p_date'])
			if cur >= record['p_date'] >= half_ago:
				mon = record['p_date'].month
				# print(record['p_date'])
				if last_month >= mon:
					print('aaa',(5-last_month+mon)%6)
					spent[(5-last_month+mon)%6] += record['price']
				else:
					spent[(-12-last_month+mon)%6] += record['price']
					

		x_axis = [month[i] for i in range(begin_month,begin_month+6)]
		# print('aaa',spent)
		plt.clf()
		plt.bar(x_axis,spent,color=(0.2, 0.4, 0.6, 0.6))
		plt.title('Monthly spending')
		plt.xlabel('Month')
		plt.ylabel('Spending')
		for a,b in zip(x_axis,spent):
			plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)



		buffer = BytesIO()
		plt.savefig(buffer)
		plot_data = buffer.getvalue()
		imb = base64.b64encode(plot_data) 
		ims = imb.decode()
		image = "data:image/png;base64," + ims
		plt.close()

		# return the form of checking spending
		try:
			fromDate = request.form['begin_date']
			fromDate1 = datetime.datetime.date(datetime.datetime.strptime(fromDate, '%Y-%m-%d'))
			toDate = request.form['end_date']
			toDate1 = datetime.datetime.date(datetime.datetime.strptime(toDate, '%Y-%m-%d'))
			print(fromDate1)
			print(toDate1)
			if fromDate > toDate:
				error = 'Invalid Date''Choose an End Date Earlier Than Today'
				return render_template("customer_home.html", error=error)

			if toDate1 > datetime.date.today():
				error = 'Invalid Date'
				return render_template("customer_home.html", error=error)

			query = """SELECT price, p_date 
				FROM ticket NATURAL JOIN purchases NATURAL JOIN flight 
				WHERE customer_email = '{}'
				and p_date <= '{}'
				and p_date >= '{}'"""
			cursor = conn.cursor()
			print(query.format(session["username"], toDate, fromDate))
			cursor.execute(query.format(session["username"], toDate, fromDate))
			dataRange = cursor.fetchall()
			print('data',dataRange)
			cursor.close()

			thisMonth = (toDate1.year, toDate1.month)
			begin_month = (fromDate1.year, fromDate1.month)

			gap = toDate1.year - fromDate1.year

			p = {}
			curM = [begin_month[0], begin_month[1]]

			if gap > 0:
				while (curM[0] != thisMonth[0]) or ((curM[1] - 1) != thisMonth[1]):
					nameM = str(curM[0]) + '-' + str(curM[1])
					p[nameM] = p.get(nameM, 0)
					curM[1] += 1
					if curM[1] == 13:
						curM[0] += 1
						curM[1] = 1

			if gap == 0:
				while (curM[1] - 1) != thisMonth[1]:
					nameM = str(curM[0]) + '-' + str(curM[1])
					p[nameM] = p.get(nameM, 0)
					curM[1] += 1

			for record in dataRange:
				if toDate1 > record['p_date'] >= fromDate1:
					mon = record['p_date'].month

					thisMon = str(record['p_date'].year) + '-' + str(mon)
					p[thisMon] = p.get(thisMon, 0) + record['price']
					print(p)

			x_axis = list(p.keys())
			spent = []
			for i in x_axis:
				if i not in p.keys():
					spent.append(0)
				else:
					spent.append(p[i])

			plt.bar(x_axis, spent,color=(0.2, 0.4, 0.6, 0.6))
			plt.title('Report from ' + str(fromDate1) + ' to ' + str(toDate1))
			plt.xlabel('Month')
			plt.ylabel('Spending')
			for a, b in zip(x_axis, spent):
				plt.text(a, b, b, ha='center', va='bottom', fontsize=7)
			buffer = BytesIO()
			plt.savefig(buffer)

			plot_data = buffer.getvalue()
			imb = base64.b64encode(plot_data)
			ims = imb.decode()
			image = "data:image/png;base64," + ims
			plt.close()

			# return render_template("detailed_reports.html", lastMTotTkt=lastMTotTkt, image=image,lastYTotTkt=lastYTotTkt)
			return render_template("customer_home.html", search_flight = data, bar_chart = image,year_money = year_money)
		except:
			print('selected not rendered')

	except:
		print()

	#search my flight
	try:
		query = 'select * from flight where flight_status ="upcoming" and (flight_num) in (select flight_num from ticket where ticket_id in (select purchases.ticket_id from purchases where purchases.customer_email = %s)) '
		appendix = ""
		
		if request.form.get("departure_date", False):
			d_date = request.form['departure_date']
			print(111)
			d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
			add = "and '"+ str(d_start)[:10] +"' <= depart_time "
			appendix += add 
		if request.form.get("arrival_date", False):
			a_date = request.form['arrival_date']
			print(222)
			a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
			dd = "and '"+ str(a_start)[:10] +"' >= arrive_time"
			appendix += dd
		if request.form.get("flight", False) :
			flight_num = request.form['flight'] 
			appendix += "and flight_num = '"
			appendix += str(flight_num)
			appendix += "'"
		if request.form.get("departure_airport", False):
			d_airport = request.form['departure_airport']
			appendix += "and depart_name = '"
			appendix += d_airport
			appendix += "'"
		if request.form.get("arrival_airport", False) :
			a_airport = request.form['arrival_airport'] 
			appendix += "and arrive_name = '"
			appendix += a_airport
			appendix += "'"
		if request.form.get("departure_city", False):
			d_city = request.form['departure_city'] 
			add = "and depart_name in (select name from airport where city ='"+ d_city +"')"
			appendix += add
		if request.form.get("arrival_city", False):
			a_city = request.form['arrival_city'] 
			add = "and arrive_name in (select name from airport where city = '"+ a_city +"')"
			appendix += add
		
		query += appendix
		# print(query)
		cursor = conn.cursor()
		cursor.execute(query,session['username'])
		print("succesfully executed")
		data = cursor.fetchall()
		# print(data)
		cursor.close()
	except:
		print("Not form2 View my upcoming flights")
	
	return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart =image)
		
@app.route("/customer/flight_purchase/<customer_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def customer_purchase(customer_email,flight_num, airline_name):
	# try:
	print(session["username"],customer_email)
	if session['username'] != customer_email:
		print("case1")
		return render_template("upcoming_flight.html", error1="Bad Request: username does not match")


	# if I had already buy the ticket
	query = """select * from purchases, ticket, flight 
		where purchases.customer_email = %s 
		and purchases.ticket_id = ticket.ticket_id 
		and ticket.flight_num=flight.flight_num
		and ticket.flight_num = %s
		and flight.airline_name = %s """
	cursor = conn.cursor()
	cursor.execute(query,(session["username"],flight_num, airline_name))
	data =  cursor.fetchall()
	cursor.close()


	# if there is no seats left
	query = """select seats from airplane where airline_name = %s
	and ID in (select airplane_id from flight where airline_name = %s and flight_num = %s)"""
	cursor = conn.cursor()
	cursor.execute(query,(airline_name, airline_name, flight_num))
	totalSeats =  cursor.fetchone()
	totS = totalSeats['seats']
	cursor.close()
	print(totalSeats, totS)

	query = """SELECT count(*)
		FROM ticket,flight
		WHERE ticket.flight_num=flight.flight_num
		and flight.airline_name = %s
		and ticket.flight_num = %s"""
	cursor = conn.cursor()
	cursor.execute(query,(airline_name,flight_num))
	soldSeats =  cursor.fetchone()
	sldS = soldSeats['count(*)']
	cursor.close()

	if sldS == totS:
		print('NO SEATS: soldSeats == totalSeats')
		return render_template("back.html", status = 3)

	elif data:
		print("Now we are here Customer purchase")
		return render_template("back.html",status = 2)

	else: # if I haven't buy the ticket

		query = "select max(ticket_id) from purchases"
		cursor = conn.cursor()
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()

		# if this ticket id already exists
		if data[0]["max(ticket_id)"]:
			ticket_id = str(int(data[0]["max(ticket_id)"])+1)

		else:
			ticket_id = str(1)
		cursor = conn.cursor()
		query1 = "insert into ticket values( %s, %s)"
		cursor.execute(query1,(ticket_id,flight_num))
		query2 = "INSERT INTO purchases(ticket_id,customer_email,p_date) VALUES(%s,%s,%s)" 
		cursor.execute(query2, (ticket_id, session["username"], datetime.datetime.now().strftime('%Y-%m-%d')))
		cursor.close()
		conn.commit()
		return render_template("back.html",status = 1)


###############################################################################################################
#                                               Booking Agent                                                 #
###############################################################################################################

@app.route("/agent_home/<agent_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/agent_home/<agent_email>/<error>", methods=["GET", "POST"])
def agent_home(agent_email, error):
	month = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sep","Oct","Nov","Dec"]
	if session['username'] != agent_email:
			print("case1")
			return render_template("login.html", error="Bad Request")
		
	# default view my flights
	query = '''select flight.airline_name, flight.flight_num, 
		flight.depart_name, flight.depart_time, flight.arrive_name, flight.arrive_time,
		flight.price, flight.flight_status, flight.airplane_id, purchases.customer_email
		from flight join ticket join purchases
		where flight_status ="upcoming" 
		and ticket.flight_num = flight.flight_num
		AND ticket.ticket_id = purchases.ticket_id
		and (flight.airline_name, ticket.flight_num) in 
		(select flight.airline_name,ticket.flight_num from ticket join flight
		where ticket_id in 
		(select purchases.ticket_id from purchases where booking_agent_email = %s))'''
	cursor = conn.cursor()
	# print(cursor)
	cursor.execute(query,session['username'])
	data =  cursor.fetchall()
	cursor.close()
	

	# default commission  
	cur = datetime.date.today()
	month_ago  = cur - datetime.timedelta(days=30)
	# print(cur)
	# print(month_ago)

	query = '''select * from flight, ticket
		where flight.flight_num = ticket.flight_num
		and ticket.ticket_id in 
		(select purchases.ticket_id 
		from purchases 
		where p_date <= %s
		and p_date >= %s
		and booking_agent_email = %s )'''
	cursor = conn.cursor()
	cursor.execute(query,(cur, month_ago, session['username']))
	money =  cursor.fetchall()
	# print('mpn',len(money))
	tnum = len(money)
	cursor.close()
	month_money = 0
	for i in money:
		month_money += i['price']
	# print('month_money', month_money)

	session['month_money'] = str(month_money)
	session['tnum'] = str(tnum)

	# default draw an image
	#Top customers in past half-year: num of tickets
	half_ago = cur - datetime.timedelta(days=183)
	year_ago = cur - datetime.timedelta(days=365)
	query = """select count(flight.flight_num) AS 'totnum', purchases.customer_email
		from flight join purchases join ticket
		where flight.flight_num = ticket.flight_num
		AND purchases.ticket_id = ticket.ticket_id
		AND purchases.booking_agent_email = %s
		AND purchases.p_date >= %s
		AND purchases.p_date <= %s
		GROUP BY purchases.customer_email
		ORDER by totnum desc
		LIMIT 5"""
	cursor = conn.cursor()
	cursor.execute(query, (session['username'], half_ago, cur))
	halfdata = cursor.fetchall()
	cursor.close()
	# print('half', halfdata)
	name1 = []
	value1 = []
	for i in halfdata:
		name1.append(i['customer_email'])
		value1.append(i['totnum'])
		
	# print(name1,value1)
	plt.clf()
	plt.bar(name1, value1,color=(0.2, 0.4, 0.6, 0.6))
	plt.title('My Top 5 Customers (on Number of Tickets Bought)')
	plt.ylabel('Ticket number')
	plt.xticks(rotation=-15)
	for a,b in zip(name1, value1):
		plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
	
	
	buffer = BytesIO()
	plt.savefig(buffer)
	plot_data1 = buffer.getvalue()
	imb = base64.b64encode(plot_data1)
	ims = imb.decode()
	image1 = "data:image/png;base64," + ims


	#Top customers in past year: total commission
	query = """select sum(flight.price) AS 'totprice', purchases.customer_email
		from flight join purchases join ticket
		where flight.flight_num = ticket.flight_num
		AND purchases.ticket_id = ticket.ticket_id
		AND purchases.booking_agent_email = %s
		AND purchases.p_date >= %s
		AND purchases.p_date <= %s
		GROUP BY purchases.customer_email
		ORDER by totprice desc
		LIMIT 5"""
	cursor = conn.cursor()
	cursor.execute(query, (session['username'], year_ago, cur))
	yeardata = cursor.fetchall()
	cursor.close()
	for i in yeardata: 
		i['totprice'] = float(i['totprice'])
	# print('year', yeardata)
	name2 = []
	value2 = []
	for i in yeardata:
		name2.append(i['customer_email'])
		value2.append(i['totprice'])
	
	
	plt.clf()
	plt.bar(name2, value2,color=(0.2, 0.4, 0.6, 0.6))
	plt.title('Top 5 Customers (on Commissions Last Year)')
	plt.ylabel('Total commission')
	plt.xticks(rotation=-15)
	for a,b in zip(name2, value2):
		plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
	

	buffer2 = BytesIO()
	plt.savefig(buffer2)
	plot_data2 = buffer2.getvalue()
	imb2 = base64.b64encode(plot_data2)
	ims2 = imb2.decode()
	image2 = "data:image/png;base64," + ims2
	
	# print('kuailaia')
	# if user specify time span in View Commission
	try:
		end = datetime.date.today()
		begin = end-datetime.timedelta(days=30)
		# if request.form["begin_date"]:
		if request.form.get("begin_date", False):
		# if request.form["begin_date"]:
			# print(1)
			begin = request.form['begin_date']
			begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
			print(begin)
		# if request.form['end_date']:
		if request.form['end_date']:
		# if request.form.get("end_date", False):
			# print('2')
			end = request.form['end_date']
			end = datetime.datetime.strptime(end,'%Y-%m-%d')
			# print(end)
		

		query = '''select * from flight, ticket
			where flight.flight_num = ticket.flight_num
			and ticket.ticket_id in 
			(select purchases.ticket_id 
			from purchases 
			where p_date <= %s
			and p_date >= %s
			and booking_agent_email = %s )'''
		cursor = conn.cursor()
		cursor.execute(query,(end, begin, session['username']))
		# print(cursor)
		inputdata =  cursor.fetchall()
		# print(inputdata)
		inputnum = len(inputdata)
		cursor.close()
		inputmoney = 0
		for i in inputdata:
			inputmoney += i['price']
		print('inputmoney', inputmoney)

		if tnum == 0:
			average_com=0
		else:
			average_com = format(month_money/tnum, '.2f')
		return render_template("agent_home.html", search_flight = data, month_money = month_money, tnum = tnum, average_com = average_com,
		halfdata = halfdata, yeardata = yeardata, inputnum = inputnum, inputmoney=inputmoney,
		image1 = image1, image2 = image2)
	
	except:
		print("Not form View Commission or no start date")
		
	
	# show upcoming flights
	try:
		query = '''select flight.airline_name, flight.flight_num, 
		flight.depart_name, flight.depart_time, flight.arrive_name, flight.arrive_time,
		flight.price, flight.flight_status, flight.airplane_id, purchases.customer_email
		from flight, ticket, purchases
		where flight.flight_status ="upcoming" 
		and ticket.flight_num = flight.flight_num
		AND ticket.ticket_id = purchases.ticket_id
		and (flight.airline_name, flight.flight_num) in 
		(select flight.airline_name, ticket.flight_num from ticket, flight
		where flight.flight_num = ticket.flight_num and ticket.ticket_id in 
		(select purchases.ticket_id from purchases where booking_agent_email = '{}')) '''
		appendix = ""

		if request.form.get("departure_date", False):
			# print(1)
			d_date = request.form['departure_date']
			d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
			add = "and '"+ str(d_start)[:10] +"' <=flight.depart_time"
			appendix += add 
		if request.form.get("arrival_date", False):
			# print(2)
			a_date = request.form['arrival_date']
			a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
			dd = " and '"+ str(a_start)[:10] +"' >=flight.arrive_time"
			appendix += dd
		if request.form.get("flight", False):
			# print(11)
			flight_num = request.form['flight'] 
			appendix += "and flight.flight_num = '"
			appendix += str(flight_num)
			appendix += "'"
		if request.form.get("departure_airport", False):
			d_airport = request.form['departure_airport']
			appendix += "and flight.depart_name = '"
			appendix += d_airport
			appendix += "'"
		if request.form.get("arrival_airport", False):
			a_airport = request.form['arrival_airport'] 
			appendix += "and flight.arrive_name = '"
			appendix += a_airport
			appendix += "'"
		if request.form.get("departure_city", False):
			d_city = request.form['departure_city'] 
			add = "and depart_name in (select name from airport where city ='"+ d_city +"')"
			appendix += add
		if request.form.get("arrival_city", False):
			a_city = request.form['arrival_city'] 
			add = "and arrive_name in (select name from airport where city = '"+ a_city +"')"
			appendix += add

		query += appendix
		# print(query)
		cursor = conn.cursor()
		cursor.execute(query.format(session['username']))
		print("succesfully executed")
		data = cursor.fetchall()
		# print(data[flight_num])
		cursor.close()
		if tnum == 0:
			average_com=0
		else:
			average_com = format(month_money/tnum, '.2f')
		return render_template("agent_home.html",search_flight = data, month_money = month_money, tnum = tnum, average_com = average_com,
		halfdata = halfdata, yeardata = yeardata, image1 = image1, image2 = image2)
	except:
		print("Not form2 View my upcoming flights")
	if tnum == 0:
		average_com=0
	else:
		average_com = format(month_money/tnum, '.2f')
	return render_template("agent_home.html",search_flight = data, month_money = month_money, tnum = tnum, average_com = average_com,
	halfdata = halfdata, yeardata = yeardata, image1 = image1, image2 = image2)


		
@app.route("/agent/flight_purchase/<agent_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def agent_purchase(agent_email, flight_num, airline_name):
	# try:

		
	if session['username'] != agent_email:
		print("case1")
		return render_template("upcoming_flight.html", error1="Bad Request: username does not match")

	if airline_name not in session['company']:
		print('case2')
		return render_template("upcoming_flight.html", error1="Bad Request: You do not have permission to buy ticket from this company.")

	# get the customer email
	customer_email = request.form.get("customer_email", False)
	print('customer_email', customer_email)

	#check if it is valid
	query = """select email from customer WHERE email = %s"""
	cursor = conn.cursor()
	cursor.execute(query, (customer_email))
	fetchemail =  cursor.fetchone()

	if not (fetchemail):
		return render_template("upcoming_flight.html", error1="Bad Request: customer does not exist")


	query = """select * from purchases, ticket 
		where purchases.ticket_id = ticket.ticket_id 
		and ticket.flight_num = %s
		AND customer_email = %s"""
	cursor = conn.cursor()
	cursor.execute(query, (flight_num, customer_email))
	data =  cursor.fetchall()
	cursor.close()

	# if there is no seats left
	query = """select seats from airplane where airline_name = %s
	and ID in (select airplane_id from flight where airline_name = %s and flight_num = %s)"""
	cursor = conn.cursor()
	cursor.execute(query,(airline_name, airline_name, flight_num))
	totalSeats =  cursor.fetchone()
	totS = totalSeats['seats']
	cursor.close()

	query = """SELECT count(*)
		FROM ticket
		WHERE flight_num = %s"""
	cursor = conn.cursor()
	cursor.execute(query,(flight_num))
	soldSeats =  cursor.fetchall()
	print('soldSeats', soldSeats)
	sldS = soldSeats[0]['count(*)']
	cursor.close()

	if sldS == totS:
		print('NO SEATS: soldSeats == totalSeats')
		return render_template("back.html", status = 3)

	elif data:
		print("Now we are here 5")
		return render_template("back.html", status = 2)
	else:
		query = "select max(ticket_id) from purchases"
		cursor = conn.cursor()
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		if data:
			ticket_id = str(int(data[0]["max(ticket_id)"])+1)
		else:
			ticket_id = '1'
		cursor = conn.cursor()
		# print('aaa',ticket_id,flight_num)
		query1 = "insert into ticket values(%s, %s)"
		cursor.execute(query1,(ticket_id, flight_num))
		# print('bbb',agent_email)
		query2 = "INSERT INTO purchases(ticket_id,customer_email, booking_agent_email,p_date) VALUES(%s,%s,%s,%s)" 
		cursor.execute(query2, (ticket_id, customer_email, agent_email, datetime.datetime.now().strftime('%Y-%m-%d')))

		print('herehere')
		cursor.close()
		conn.commit()
		return render_template('back.html',status = 1)
    
####################################################################################################################################
#                                                          Staff                                                                   #
####################################################################################################################################
@app.route("/airline_staff/<staff_email>", defaults={'error': ''}, methods=["GET", "POST"])
@app.route("/airline_staff/<staff_email>/<error>", methods=["GET", "POST"])
def staff_home(staff_email, error):
	if session['username'] != staff_email:
		return render_template("login.html", error="Bad Request")
	cursor = conn.cursor()
	query = "select * from flight where airline_name = %s"
	cursor.execute(query, session['company'])
	flights = cursor.fetchall()
	cursor.close()

	# 1. VIEW FLIGHTS IN 30 DAYS OR UNDER SELECTED CONDITIONS
	query = "select * from flight where airline_name = %s "
	isdefault = True
	try:
		if request.form['start_date']:
			d_date = request.form['start_date']
			d_start = datetime.datetime.strptime(d_date, '%Y-%m-%d')
			add = "and '" + str(d_start)[:10] + "' <=depart_time "
			query += add
		if request.form['end_date']:
			a_date = request.form['end_date']
			a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
			add = "and '" + str(a_start)[:10] + "' >=arrive_time "
			query += add
		if request.form['flight']:
			flight_num = request.form['flight']
			query += "and flight_num = '" + flight_num + "' "
			default_add = ''
		if request.form['departure_airport']:
			d_airport = request.form['departure_airport']
			query += "and depart_name = '"+d_airport+""+"' "
		if request.form['arrival_airport']:
			a_airport = request.form['arrival_airport']
			query += "and arrive_name = '"+a_airport+"' "
		if request.form['departure_city']:
			d_city = request.form['departure_city']
			add = "and depart_name in (select name from airport where city ='" + d_city + "') "
			query += add
		if request.form['arrival_city']:
			a_city = request.form['arrival_city']
			add = "and arrive_name in (select name from airport where city = '" + a_city + "') "
			query += add
		cursor = conn.cursor()
		cursor.execute(query, session['company'])
		flights = cursor.fetchall()
		cursor.close()
		isdefault = False
	except:
		default_start = datetime.date.today()
		default_end = datetime.date.today()+datetime.timedelta(days=30)
		default_add = "and '" + str(default_start)[:10] + "' <=depart_time and '" + str(default_end)[:10] + "' >=arrive_time"
		query += default_add
		cursor = conn.cursor()
		cursor.execute(query, session['company'])
		flights = cursor.fetchall()
		cursor.close()

	# 6. VIEW TOP 5 BOOKING AGENTS
	cursor = conn.cursor()
	query = "select purchases.booking_agent_email from purchases where purchases.p_date <= %s  and purchases.p_date >= %s and purchases.booking_agent_email is NOT NULL and purchases.ticket_id in (select ticket_id from ticket NATURAL JOIN flight where airline_name = %s) group by purchases.booking_agent_email ORDER BY count(purchases.ticket_id) DESC LIMIT 5 "
	today = datetime.date.today()
	last_month = today - datetime.timedelta(days=31)
	last_year = today - datetime.timedelta(days=365)
	cursor.execute(query, (today, last_month, session['company']))
	lm_agent = cursor.fetchall()
	cursor.execute(query, (today, last_year, session['company']))
	ly_agent = cursor.fetchall()
	query = "select purchases.booking_agent_email from purchases, flight,ticket where flight.airline_name = %s and purchases.booking_agent_email is NOT NULL and ticket.flight_num = flight.flight_num and purchases.ticket_id =  ticket.ticket_id and purchases.p_date <= %s and purchases.p_date >= %s group by purchases.booking_agent_email ORDER BY sum(flight.price) DESC LIMIT 5"
	cursor.execute(query, (session['company'], today, last_year))
	c_agent = cursor.fetchall()
	cursor.close()

	# 7. VIEW TOP 10 FREQUENT CUSTOMERS
	query = """select purchases.customer_email,count(purchases.ticket_id) 
			from purchases, ticket, flight 
			where flight.flight_num = ticket.flight_num 
			and ticket.ticket_id = purchases.ticket_id 
			and flight.airline_name = %s 
			and purchases.p_date <= %s and %s <= purchases.p_date 
			GROUP BY purchases.customer_email 
			ORDER BY count(purchases.ticket_id) DESC LIMIT 10"""
	cursor = conn.cursor()
	cursor.execute(query, (session["company"], today, last_year))
	frequent_customer = cursor.fetchall()
	cursor.close()

	# 8. VIEW REPORTS
	query = "select COUNT(ticket.ticket_id) from purchases, ticket, flight where flight.flight_num = ticket.flight_num and flight.airline_name = %s and ticket.ticket_id  = purchases.ticket_id and purchases.p_date <= %s and %s <= purchases.p_date"
	cursor = conn.cursor()
	cursor.execute(query, (session['company'], today, last_month))
	lm_total_amount = cursor.fetchall()
	cursor.execute(query, (session['company'], today, last_year))
	ly_total_amount = cursor.fetchall()
	cursor.close()

	# 10. VIEW TOP 3 DESTINATIONS
	query = "select airport.city from airport, flight where flight.arrive_name = airport.name AND flight.depart_time <= %s and flight.depart_time >= %s GROUP BY airport.city ORDER BY count(flight.arrive_time) DESC LIMIT 3"
	cursor = conn.cursor()
	last_three_month = today - datetime.timedelta(days=92)
	cursor.execute(query, (today, last_three_month))
	m3des = cursor.fetchall()
	cursor.execute(query, (today, last_year))
	lydes = cursor.fetchall()
	cursor.close()

	# 9. COMPARISON OF REVENUE EARNED
	lastMonth = today - datetime.timedelta(days=30)
	lastYear = today - datetime.timedelta(days=365)
	# DIRECT SALE REVENUE
	query = """SELECT SUM(flight.price) AS 'totalprice'
		FROM flight, ticket, purchases
		WHERE flight.flight_num = ticket.flight_num
		AND ticket.ticket_id = purchases.ticket_id
		AND flight.airline_name = %s
		AND purchases.booking_agent_email is NULL
		AND purchases.p_date <= %s
		AND purchases.p_date >= %s"""
	cursor = conn.cursor()
	cursor.execute(query, (session['company'], today, lastMonth))
	revNoAMonth = cursor.fetchone()
	revNoAMonth = revNoAMonth['totalprice']
	cursor.execute(query, (session['company'], today, lastYear))
	revNoAYear = cursor.fetchone()
	revNoAYear = revNoAYear['totalprice']
	cursor.close()

	# INDIRECT SALE REVENUE
	query = """SELECT SUM(flight.price) AS 'totalprice'
		FROM flight, ticket, purchases
		WHERE flight.flight_num = ticket.flight_num
		AND ticket.ticket_id = purchases.ticket_id
		AND flight.airline_name = %s
		AND purchases.booking_agent_email is not NULL
		AND purchases.p_date <= %s
		AND purchases.p_date >= %s"""
	cursor = conn.cursor()
	cursor.execute(query, (session['company'], today, lastMonth))
	revAMonth = cursor.fetchone()
	revAMonth = revAMonth['totalprice']
	cursor.execute(query, (session['company'], today, lastYear))
	revAYear = cursor.fetchone()
	revAYear = revAYear['totalprice']
	cursor.close()

	# PIE CHART FOR LAST MONTH
	plt.clf()
	plt.figure(figsize=(6, 6))
	colors = ['#4F6272', '#B7C3F3']
	plt.title('Revenue Last Month')
	label = ['From Customer', 'Through Agent']
	explode = [0.01, 0.01]
	values = [revNoAMonth, revAMonth]
	for i in range(len(values)):
		if not values[i]:
			values[i] = 0

	plt.pie(values, explode=explode, labels=label,autopct='%1.1f%%',wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, colors = colors)
	plt.legend(loc='upper right')
	# SAVE AS BINARY
	buffer3 = BytesIO()
	plt.savefig(buffer3)
	plot_data3 = buffer3.getvalue()
	# TO HTML
	imb3 = base64.b64encode(plot_data3)
	ims3 = imb3.decode()
	image3 = "data:image/png;base64," + ims3
	plt.close()

	if revAMonth == None and revNoAMonth == None:
		image3 = None

	# PIE CHART FOR LAST YEAR
	plt.clf()
	plt.figure(figsize=(6, 6))
	plt.title('Revenue Last Year')
	label = ['From Customer', 'Through Agent']
	explode = [0.01, 0.01]
	values = [revNoAYear, revAYear]
	for i in range(len(values)):
		if not values[i]:
			values[i] = 0

	plt.pie(values, explode=explode, labels=label, autopct='%1.1f%%',wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' },colors = colors)
	plt.legend(loc='upper right')
	buffer4 = BytesIO()
	plt.savefig(buffer4)
	plot_data4 = buffer4.getvalue()

	imb4 = base64.b64encode(plot_data4)
	ims4 = imb4.decode()
	image4 = "data:image/png;base64," + ims4
	plt.close()

	if revAYear == None and revNoAYear == None:
		image4 = None

	return render_template("staff_home.html", all_flight=flights, lm_agent=lm_agent, ly_agent=ly_agent, c_agent=c_agent,
							m3des=m3des, lydes=lydes, lm_total_amount=lm_total_amount, ly_total_amount=ly_total_amount,
							frequent_customer=frequent_customer, image3=image3, image4=image4, isdefault = isdefault)

@app.route('/airline_staff/<staff_email>/create_new_flight', methods=["GET", "POST"])
# 2. CREATE NEW FLIGHT
def create_new_flight(staff_email):
	try:
		if session['username'] != staff_email or "Admin" not in session['status']:
			return render_template("login.html", error="Bad Request")
		cursor = conn.cursor()
		query = "select name from airport"
		cursor.execute(query)
		all_airports = cursor.fetchall()
		all = []
		for i in all_airports:
			all.append(i['name'])
		cursor.close()

		cursor = conn.cursor()
		query = "select ID from airplane where airline_name = %s"
		cursor.execute(query, session['company'])
		all_id = cursor.fetchall()
		all_ids = []
		cursor.close()
		for i in all_id:
			all_ids.append(i['ID'])
		try:
			d_airport = request.form['departure_airport']
			a_airport = request.form['arrival_airport']
			d_time = request.form['departure_time']
			a_time = request.form['arrival_time']
			price = request.form['price']
			status = request.form['Status']
			airplane_id = request.form['airplane_id']
			flight_num = request.form['flight_num']

			if d_airport == a_airport:
				return render_template("create_new_flight.html",
										error="Sorry, the departure and arrival aiport is the same ...", all=all,
										all_ids=all_ids)
			if a_time <= d_time:
				return render_template("create_new_flight.html", error="Sorry, wrong time input ...", all=all,
										all_ids=all_ids)
			cursor = conn.cursor()
			query1 = "INSERT into flight values (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
			cursor.execute(query1, (flight_num, session['company'], airplane_id, d_airport, a_airport, d_time, a_time, price, status))
			conn.commit()
			cursor.close()
			return render_template("create_new_flight.html", success="You have successfully created a new flight! ",
									flight_num=flight_num, all=all, all_ids=all_ids)
		except:
			return render_template("create_new_flight.html", all=all, all_ids=all_ids)
	except:
		return render_template("login.html", error="Error Creating Flight")

# 3. CHANGE STATUS OF FLIGHTS
@app.route('/airline_staff/change_flight_status/<airline_name>/<staff_email>', defaults={'flight_num': ''},methods=["GET", "POST"])
@app.route('/airline_staff/change_flight_status/<airline_name>/<staff_email>/<flight_num>', methods=["GET", "POST"])
def change_flight_status(airline_name, staff_email, flight_num):
	try:
		if session['username'] != staff_email or ("Operator" not in session['status']):
			return render_template("login.html", error="No Operator Permission")

		query = """SELECT * 
			FROM flight
			WHERE airline_name = %s"""
		cursor = conn.cursor()
		cursor.execute(query, (session['company']))
		data = cursor.fetchall()

		if flight_num:
			selectedS = request.form['selectedS']
			query = """SELECT * 
				FROM flight
				WHERE airline_name = %s
				AND flight_num = %s
				AND flight_status = %s"""
			cursor = conn.cursor()
			cursor.execute(query, (airline_name, flight_num, selectedS))
			already = cursor.fetchall()

			if already:
				status = 'The original status is ' + str(selectedS)
				return render_template('change_flight_status.html', status=status)

			query = """UPDATE flight
				SET flight_status = %s
				WHERE flight.airline_name = %s 
				AND flight.flight_num = %s"""
			cursor = conn.cursor()
			cursor.execute(query, (selectedS, airline_name, flight_num))
			conn.commit()
			cursor.close()
			status = 'You have successfully updated ' + str(airline_name) + ' ' + str(flight_num) + ' into ' + str(
				selectedS) + '! Please go back and reload this page to see the change.'
			return render_template('change_flight_status.html', status=status, data=data)
		return render_template('change_flight_status.html', data=data)
	except:
		return render_template("staff_home.html", error="Bad Request")

# 4. ADD AIRPLANE IN THE SYSTEM
@app.route('/airline_staff/<staff_email>/add_new_airplanes', methods=["GET", "POST"])
def add_new_airplanes(staff_email):
	try:
		if session['username'] != staff_email or "Admin" not in session['status']:
			return render_template("login.html", error="Bad Request")
		try:
			airplane_id = request.form["airplane_id"]
			seats = request.form["seats"]
			try:
				airplane_id = int(airplane_id)
				seats = int(seats)
				query = "select ID from airplane where airline_name = %s"
				cursor = conn.cursor()
				cursor.execute(query, (session['company']))
				cursor.close()
				all_id = cursor.fetchall()
				all_ids = []
				for i in all_id:
					all_ids.append(i["ID"])
				if airplane_id in all_ids:
					return render_template("add_new_airplanes.html", error="Input Airplane ID already exists ... ")
				else:
					query = "INSERT INTO airplane values (%s,%s,%s)"
					cursor = conn.cursor()
					cursor.execute(query, (session['company'], airplane_id, seats))
					cursor.close()
					conn.commit()

					# CONFIRM ALL PLANES THIS AIRLINE OWNS
					query = """SELECT * 
						FROM airplane
						WHERE airline_name = %s"""
					cursor = conn.cursor()
					cursor.execute(query, (session['company']))
					all_planes = cursor.fetchall()

					return render_template("add_new_airplanes.html", success="Success: ", airplane_id=airplane_id, all_planes=all_planes)
			except:
				return render_template("add_new_airplanes.html", error="Input Airplane ID or seats is not an integer ... ")
		except:
			return render_template("add_new_airplanes.html")
	except:
		return render_template("login.html", error="Bad Request")

# 5. ADD NEW AIRPORTS IN THE SYSTEM
@app.route('/airline_staff/<staff_email>/add_new_airports', methods=["GET", "POST"])
def add_new_airports(staff_email):
	try:
		if session['username'] != staff_email or "Admin" not in session['status']:
			return render_template("login.html", error="Bad Request")
		try:
			name = request.form['name']
			city = request.form['city']
			query = "select * from airport where name = %s "
			cursor = conn.cursor()
			cursor.execute(query, (name.upper()))
			data = cursor.fetchall()
			if data:
				return render_template("add_new_airports.html", error="Sorry, airport already exists ...")
			else:
				query = "INSERT INTO airport values (%s,%s)"
				cursor.execute(query, (name.upper(), city.upper()))
				conn.commit()
				cursor.close()
				return render_template("add_new_airports.html", success="Success: ", name=name.upper(), city=city.upper())
		except:
			return render_template("add_new_airports.html")
	except:
		return render_template("login.html", error="Bad Request")

# 11. GRANT PERMISSIONS OF OTHER STAFFS
@app.route('/airline_staff/grant_permission/<staff_email>', defaults={"collegue_email": ''}, methods=["GET", "POST"])
@app.route('/airline_staff/grant_permission/<staff_email>/<collegue_email>', methods=["GET", "POST"])
def grant_permission(staff_email, collegue_email):
	# print('collegue_email', collegue_email)
	try:
		if session['username'] != staff_email or ("Admin" not in session['status']):
			return render_template("login.html", error="No Admin Permission")

		query = """SELECT airlinestaff.username, permission.permission
			FROM permission, airlinestaff
			WHERE  airlinestaff.username = permission.username
			AND airlinestaff.airline_name = %s"""
		cursor = conn.cursor()
		cursor.execute(query, (session['company']))
		data = cursor.fetchall()
		cursor.close()

		if collegue_email:
			selectedP = request.form["selectedP"]
			query = """SELECT *
				FROM permission, airlinestaff
				WHERE permission.username = airlinestaff.username
				AND permission.permission = %s
				AND permission.username = %s"""
			cursor = conn.cursor()
			cursor.execute(query, (selectedP, collegue_email))
			attempt1 = cursor.fetchall()
			cursor.close()
			if attempt1:
				error = 'Permission Already Granted to Selected Staff'
				return render_template("grant_permission.html", data=data, error=error)

			else:
				query = """INSERT INTO permission VALUES (%s, %s)"""
				cursor = conn.cursor()
				cursor.execute(query, (collegue_email,selectedP))
				conn.commit()
				cursor.close()
				status = 'Succeeded Granting ' + str(collegue_email) + ' with ' + str(selectedP) + ' Permission!' + '\n' + 'Reopen to See Change.'
				try:
					query = """DELETE FROM permission WHERE permission.username = %s AND permission.permission = ''"""
					cursor = conn.cursor()
					cursor.execute(query, (collegue_email))
					conn.commit()
					cursor.close()
				except:
					print()

			return render_template("grant_permission.html", data = data, status = status)
		return render_template("grant_permission.html", data=data)
	except:
		return render_template("login.html", error="Bad Request")

# 12. ADD BOOKNG AGENTS TO THE STAFF'S AIRLINE
@app.route('/airline_staff/add_booking_agents/<staff_email>', methods=["GET", "POST"])
def add_booking_agents(staff_email):
	try:
		if session['username'] != staff_email or ("Admin" not in session['status']):
			return render_template("login.html", error="Incorrect Username or No Admin Permission")

		try:
			if request.form['agentEmail']:
				agentEmail = request.form['agentEmail']

				# NO SUCH AGENT
				query = """SELECT * 
					FROM bookingagent
					WHERE email = %s"""
				cursor = conn.cursor()
				cursor.execute(query, (agentEmail))
				noAgent = cursor.fetchone()

				if noAgent is None:
					return render_template("add_booking_agents.html",error='Cannot find this agent. Please make sure this agent is already in the system.')

				# SELECTED AGENT IS WORKING FOT THIS AIRLINE
				query = """SELECT * 
					FROM bookingagent
					WHERE email = %s
					AND airline_name = %s"""
				cursor = conn.cursor()
				cursor.execute(query, (agentEmail, session['company']))
				already = cursor.fetchone()

				if already:
					status = 'Agent ' + agentEmail + ' already works for the company ' + str(session['company']) + '.'
					return render_template("add_booking_agents.html", status=status)

				query = """UPDATE bookingagent
						SET airline_name = %s
						WHERE email = %s """
				cursor = conn.cursor()
				cursor.execute(query, (session['company'],agentEmail))
				conn.commit()
				cursor.close()
				status = 'Agent ' + agentEmail + ' has been added to the company ' + str(session['company']) + '.'

				return render_template("add_booking_agents.html", status=status)
		except:
			return render_template("add_booking_agents.html")

	except:
		return render_template("login.html", error="Bad Request")

# DETAILED REPORT
@app.route('/airline_staff/detailed_reports/<staff_email>', methods=["GET", "POST"])
def detailed_reports(staff_email):
	month = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
	error = None
	try:
		if session['username'] != staff_email:
			return render_template("login.html", error="Incorrect Username")

		today = datetime.date.today()
		lastMonth = today - datetime.timedelta(days=31)
		lastYear = today - datetime.timedelta(days=365)

		# TICKET NUMBER LAST MONTH
		query = """select COUNT(ticket.ticket_id) 
			from purchases, ticket, flight
			where ticket.flight_num = flight.flight_num
			and flight.airline_name = %s 
			and ticket.ticket_id  = purchases.ticket_id 
			and purchases.p_date <= %s 
			and %s <= purchases.p_date"""
		cursor = conn.cursor()
		cursor.execute(query, (session['company'], today, lastMonth))
		lastMTotTkt = cursor.fetchall()
		cursor.execute(query, (session['company'], today, lastYear))
		lastYTotTkt = cursor.fetchall()
		cursor.close()

		# TICKET NUMBER LAST YEAR
		query = """select ticket.ticket_id, purchases.p_date
			from purchases, ticket, flight
			where flight.airline_name = %s
			and ticket.flight_num = flight.flight_num
			and ticket.ticket_id  = purchases.ticket_id 
			and purchases.p_date <= %s 
			and %s <= purchases.p_date"""
		cursor = conn.cursor()
		cursor.execute(query, (session['company'], today, lastYear))
		info = cursor.fetchall()
		cursor.close()

		thisMonth = today.month
		begin_month = thisMonth - 12

		p = {}

		for record in info:
			if today >= record['p_date'] >= lastYear:
				mon = record['p_date'].month
				print(mon)

				thisMon = month[mon - 1]
				p[thisMon] = p.get(thisMon, 0) + 1

		x_axis = [month[i] for i in range(begin_month, begin_month + 12)]
		ticketNum = []
		for i in x_axis:
			if i not in p.keys():
				ticketNum.append(0)
			else:
				ticketNum.append(p[i])

		plt.bar(x_axis, ticketNum,color=(0.2, 0.4, 0.6, 0.6))
		plt.title('Report for Last Year')
		plt.xlabel('Month')
		plt.ylabel('# Tickets')
		for a, b in zip(x_axis, ticketNum):
			plt.text(a, b, b, ha='center', va='bottom', fontsize=7)
		buffer = BytesIO()
		plt.savefig(buffer)
		plot_data = buffer.getvalue()
		imb = base64.b64encode(plot_data)
		ims = imb.decode()
		image5 = "data:image/png;base64," + ims
		plt.close()

		try:
			fromDate = request.form['fromDate']
			fromDate1 = datetime.datetime.date(datetime.datetime.strptime(fromDate, '%Y-%m-%d'))
			toDate = request.form['toDate']
			toDate1 = datetime.datetime.date(datetime.datetime.strptime(toDate, '%Y-%m-%d'))

			if fromDate > toDate:
				error = 'Invalid Date'
				return render_template("detailed_reports.html", error=error)

			if toDate1 > datetime.date.today():
				error = 'Choose an End Date Earlier Than Today'
				return render_template("detailed_reports.html", error=error)

			query = """select ticket.ticket_id, purchases.p_date
				from purchases, ticket, flight
				where flight.airline_name = %s
				and ticket.flight_num = flight.flight_num
				and ticket.ticket_id  = purchases.ticket_id 
				and purchases.p_date <= %s 
				and %s <= purchases.p_date"""
			cursor = conn.cursor()
			cursor.execute(query, (session['company'], toDate, fromDate))
			dataRange = cursor.fetchall()
			cursor.close()

			thisMonth = (toDate1.year, toDate1.month)
			begin_month = (fromDate1.year, fromDate1.month)

			gap = toDate1.year - fromDate1.year

			p = {}
			curM = [begin_month[0], begin_month[1]]

			if gap > 0:
				while (curM[0] != thisMonth[0]) or ((curM[1] - 1) != thisMonth[1]):
					nameM = str(curM[0]) + '-' + str(curM[1])
					p[nameM] = p.get(nameM, 0)
					curM[1] += 1
					if curM[1] == 13:
						curM[0] += 1
						curM[1] = 1

			if gap == 0:
				while (curM[1] - 1) != thisMonth[1]:
					nameM = str(curM[0]) + '-' + str(curM[1])
					p[nameM] = p.get(nameM, 0)
					curM[1] += 1

			for record in dataRange:
				if toDate1 >= record['p_date'] >= fromDate1:
					mon = record['p_date'].month

					thisMon = str(record['p_date'].year) + '-' + str(mon)
					p[thisMon] = p.get(thisMon, 0) + 1

			x_axis = list(p.keys())
			ticketNum = []
			for i in x_axis:
				if i not in p.keys():
					ticketNum.append(0)
				else:
					ticketNum.append(p[i])

			plt.bar(x_axis, ticketNum, color=(0.2, 0.4, 0.6, 0.6))
			plt.title('Report from ' + str(fromDate1) + ' to ' + str(toDate1))
			plt.xlabel('Month')
			plt.ylabel('# Tickets')
			for a, b in zip(x_axis, ticketNum):
				plt.text(a, b, b, ha='center', va='bottom', fontsize=7)
			buffer = BytesIO()
			plt.savefig(buffer)

			plot_data = buffer.getvalue()
			imb = base64.b64encode(plot_data)
			ims = imb.decode()
			image6 = "data:image/png;base64," + ims
			plt.close()

			return render_template("detailed_reports.html", lastMTotTkt=lastMTotTkt, image5=image5,
									lastYTotTkt=lastYTotTkt, image6=image6)
		except:
			print('oops')

		return render_template("detailed_reports.html", lastMTotTkt=lastMTotTkt, image5=image5, lastYTotTkt=lastYTotTkt)
	except:
		print('oops2')
		return render_template("login.html", error="Bad Request")

@app.route('/airline_staff/view_freq_c/<staff_email>/<customer_email>', methods=["GET", "POST"])
def view_freq_c(staff_email, customer_email):
	try:

		if session['username'] != staff_email:
			return render_template("login.html", error="Incorrect Username")

		query = """SELECT flight.airline_name, flight.flight_num, flight.depart_name, 
			flight.depart_time, flight.arrive_name, flight.arrive_time,
			flight.price, flight.flight_status, flight.airplane_id,
			ticket.ticket_id, purchases.booking_agent_email, purchases.p_date
			FROM flight, ticket, purchases
			WHERE flight.flight_num = ticket.flight_num
			AND ticket.ticket_id = purchases.ticket_id
			AND flight.airline_name = %s
			AND purchases.customer_email = %s"""
		cursor = conn.cursor()
		cursor.execute(query, (session['company'], customer_email))
		data = cursor.fetchall()
		cursor.close()

		return render_template("view_freq_c.html", data=data, customer_email=customer_email)
	except:
		return render_template("login.html", error="Bad Request")


@app.route("/airline_staff/view_customer/<username>/<flight_num>/<airline_name>", methods=["GET", "POST"])
def view_customer(flight_num, airline_name, username):
	try:
		if session['username'] != username:
			return render_template("login.html", error1="Bad Request: username does not match")
		cursor = conn.cursor()
		query = """select purchases.customer_email 
			from ticket,purchases,flight
			where flight.airline_name = %s 
			and ticket.flight_num = flight.flight_num
			and ticket.flight_num  = %s 
			and purchases.ticket_id = ticket.ticket_id"""
		cursor.execute(query, (airline_name, flight_num))
		customer_lst = cursor.fetchall()
		cursor.close()
		return render_template("view_all_customer.html", airline_name=airline_name, flight_num=flight_num,
								customer=customer_lst)
	except:
		return render_template("login.html", error="Bad Request")


if __name__ == "__main__":
	app.secret_key = 'secret secret key'
	app.run('127.0.0.1', 5000, debug = True)
