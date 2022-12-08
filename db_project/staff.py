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

@app.route("/airline_staff/<staff_email>", defaults={'error': ''}, methods=["GET", "POST"])
@app.route("/airline_staff/<staff_email>/<error>", methods=["GET", "POST"])
def staff_home(staff_email, error):
    # try:
    if session['username'] != staff_email:
        print("case1")
        return render_template("login.html", error="Bad Request")
    cursor = conn.cursor()
    query = "select * from flight where airline_name = %s"
    print(session['company'])
    cursor.execute(query, session['company'])
    flights = cursor.fetchall()
    cursor.close()

    # ## view flights in that airline for next 30 days
    # cursor = conn.cursor()
    # query = "SELECT * FROM flight WHERE airline_name = '{}' AND status = 'upcoming'  and depart_date <= datetime.date.today()+datetime.timedelta(days=30)"
    # cursor.execute(query)
    # fl_30 = cursor.fetchall()
    # cursor.close()

    # if request.form['next30days']:
    #     render_template("staff_home.html", all_flight=fl_30)

    # view all the booking agent
    cursor = conn.cursor()
    # top 5 booking agents during last month/year
    query = "SELECT purchases.booking_agent_email FROM purchases where purchases.p_date <= %s  and purchases.p_date >= %s and purchases.booking_agent_email is NOT NULL and purchases.ticket_id in (select ticket_id from ticket where airline_name = %s) group by purchases.booking_agent_email ORDER BY count(purchases.ticket_id) DESC LIMIT 5 "
    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=31)
    last_year = today - datetime.timedelta(days=365)
    cursor.execute(query, (today, last_month, session['company']))
    lm_agent = cursor.fetchall()
    cursor.execute(query, (today, last_year, session['company']))
    ly_agent = cursor.fetchall()
    query = "select purchases.booking_agent_email from purchases, flight,ticket where ticket.airline_name = %s and purchases.booking_agent_email is NOT NULL and (ticket.airline_name, ticket.flight_num) = (flight.airline_name,flight.flight_num) and purchases.ticket_id =  ticket.ticket_id and purchases.p_date <= %s and purchases.p_date >= %s group by purchases.booking_agent_email ORDER BY sum(flight.price) DESC LIMIT 5"
    cursor.execute(query, (session['company'], today, last_year))
    c_agent = cursor.fetchall()
    cursor.close()

    # view frequent customer
    query = "select purchases.customer_email,count(purchases.ticket_id) from purchases, ticket where ticket.ticket_id = purchases.ticket_id and ticket.airline_name = %s and purchases.p_date <= %s and %s <= purchases.p_date GROUP BY purchases.customer_email ORDER BY count(purchases.ticket_id) LIMIT 10"
    cursor = conn.cursor()
    cursor.execute(query, (session["company"], today, last_year))
    frequent_customer = cursor.fetchall()
    cursor.close()

    # view reports
    query = "select COUNT(ticket.ticket_id) from purchases, ticket where ticket.airline_name = %s and ticket.ticket_id  = purchases.ticket_id and purchases.purchase_date <= %s and %s <= purchases.p_date"
    cursor = conn.cursor()
    cursor.execute(query, (session['company'], today, last_month))
    lm_total_amount = cursor.fetchall()
    cursor.execute(query, (session['company'], today, last_year))
    ly_total_amount = cursor.fetchall()
    cursor.close()

    # view destination
    query = "select airport.airport_city from airport, flight where flight.arrival_airport = airport.airport_name AND flight.depart_time <= %s and flight.departure_time >= %s GROUP BY airport_city ORDER BY count(flight.arrival_time) DESC LIMIT 3"
    cursor = conn.cursor()
    last_three_month = today - datetime.timedelta(days=92)
    cursor.execute(query, (today, last_three_month))
    m3des = cursor.fetchall()
    cursor.execute(query, (today, last_year))
    lydes = cursor.fetchall()
    cursor.close()

    # view revenue of last month and last year
    lastMonth = today - datetime.timedelta(days=30)
    lastYear = today - datetime.timedelta(days=365)
    # data without agent
    query = """SELECT SUM(flight.price) AS 'totalprice'
		FROM flight, ticket, purchases
        WHERE flight.airline_name = ticket.airline_name
        AND flight.flight_num = ticket.flight_num
        AND ticket.ticket_id = purchases.ticket_id
        AND ticket.airline_name = %s
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
    # print('revNoAMonth', revNoAMonth)

    # data with agent
    query = """SELECT SUM(flight.price) AS 'totalprice'
	    FROM flight, ticket, purchases
        WHERE flight.airline_name = ticket.airline_name
        AND flight.flight_num = ticket.flight_num
        AND ticket.ticket_id = purchases.ticket_id
        AND ticket.airline_name = %s
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

    # draw a pie chart for last month

    plt.clf()
    plt.figure(figsize=(6, 6))
    plt.title('Total amount of revenue earned in the last month')
    label = ['Direct Sales', 'Indirect Sales']
    explode = [0.01, 0.01]
    values = [revNoAMonth, revAMonth]
    for i in range(len(values)):
        if not values[i]:
            values[i] = 0
        # print('Month value', revNoAMonth, revAMonth)

    # print("Hello here: ", values,explode,label)
    plt.pie(values, explode=explode, labels=label, autopct='%1.1f%%')
    plt.legend(loc='upper right')
    # save as binary file
    buffer3 = BytesIO()
    plt.savefig(buffer3)
    plot_data3 = buffer3.getvalue()
    # 将matplotlib图片转换为HTML
    imb3 = base64.b64encode(plot_data3)  # 对plot_data进行编码
    ims3 = imb3.decode()
    image3 = "data:image/png;base64," + ims3
    plt.close()

    if revAMonth == None and revNoAMonth == None:
        image3 = None

    # draw a pie chart for last year
    plt.clf()
    plt.figure(figsize=(6, 6))
    plt.title('Total amount of revenue earned in the last year')
    label = ['Direct Sales', 'Indirect Sales']
    explode = [0.01, 0.01]
    values = [revNoAYear, revAYear]
    for i in range(len(values)):
        if not values[i]:
            values[i] = 0

    plt.pie(values, explode=explode, labels=label, autopct='%1.1f%%')
    plt.legend(loc='upper right')
    # save as binary file
    buffer4 = BytesIO()
    plt.savefig(buffer4)
    plot_data4 = buffer4.getvalue()
    # 将matplotlib图片转换为HTML
    imb4 = base64.b64encode(plot_data4)  # 对plot_data进行编码
    ims4 = imb4.decode()
    image4 = "data:image/png;base64," + ims4
    plt.close()

    if revAYear == None and revNoAYear == None:
        image4 = None

    # view session
    try:
        query = "select * from flight where airline_name = %s"
        if request.form['departure_date']:
            print("emmm2")
            d_date = request.form['departure_date']
            d_start = datetime.datetime.strptime(d_date, '%Y-%m-%d')
            add = "and '" + str(d_start)[:10] + "' <=departure_time"
            query += add
        if request.form['arrival_date']:
            print("emmm3")
            a_date = request.form['arrival_date']
            a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
            add = "and '" + str(a_start)[:10] + "' >=arrival_time"
            query += add
        if request.form['flight']:
            print("emmm1")
            flight_num = request.form['flight']
            query += "and flight_num = "
            query += flight_num
        if request.form['departure_airport']:
            print("emmm4")
            d_airport = request.form['departure_airport']
            query += "and departure_airport = '"
            query += d_airport
            query += "'"
        if request.form['arrival_airport']:
            print("emmm5")
            a_airport = request.form['arrival_airport']
            query += "and arrival_airport = '"
            query += a_airport
            query += "'"
        if request.form['departure_city']:
            print("emmm6")
            d_city = request.form['departure_city']
            add = "and departure_airport in (select airport_name from airport where airport_city ='" + d_city + "')"
            query += add
        if request.form['arrival_city']:
            print("emmm7")
            a_city = request.form['arrival_city']
            add = "and arrival_airport in (select airport_name from airport where airport_city = '" + a_city + "')"
            query += add
        cursor = conn.cursor()
        cursor.execute(query, session['company'])
        flights = cursor.fetchall()
        cursor.close()
        print(flights)
    except:
        print("Not the form of view upcoming flights")
    return render_template("staff_home.html", all_flight=flights, lm_agent=lm_agent, ly_agent=ly_agent, c_agent=c_agent,
                           m3des=m3des, lydes=lydes, lm_total_amount=lm_total_amount, ly_total_amount=ly_total_amount,
                           frequent_customer=frequent_customer, image3=image3, image4=image4)


# except:
# 	print("case 2")
# 	return render_template("login.html",error = "Bad Request")

@app.route('/airline_staff/<staff_email>/create_new_flight', methods=["GET", "POST"])
def create_new_flight(staff_email):
    try:
        if session['username'] != staff_email or "Admin" not in session['status']:
            return render_template("login.html", error="Bad Request")
        print("come1")
        cursor = conn.cursor()
        query = "select airport_name from airport"
        cursor.execute(query)
        all_airports = cursor.fetchall()
        all = []
        print("come2")
        for i in all_airports:
            all.append(i['airport_name'])
        cursor.close()
        print(all)

        cursor = conn.cursor()
        query = "select airplane_id from airplane where airline_name = %s"
        cursor.execute(query, session['company'])
        all_id = cursor.fetchall()
        all_ids = []
        cursor.close()
        for i in all_id:
            all_ids.append(i['airplane_id'])
        print("come3")
        try:
            d_airport = request.form['departure_airport']
            a_airport = request.form['arrival_airport']
            print(d_airport)
            print(a_airport)
            d_time = request.form['departure_time']
            a_time = request.form['arrival_time']
            price = request.form['price']
            status = request.form['Status']
            airplane_id = request.form['airplane_id']
            print("here1")

            # check whether airport is the same
            print("here3")
            if d_airport == a_airport:
                return render_template("create_new_flight.html",
                                       error="Sorry, the departure and arrival aiport is the same ...", all=all,
                                       all_ids=all_ids)

            # check if the arrival time is later than departure time
            if a_time <= d_time:
                return render_template("create_new_flight.html", error="Sorry, wrong time input ...", all=all,
                                       all_ids=all_ids)

            # get the flight num
            cursor = conn.cursor()
            print("try1")
            query = "select max(flight_num) from flight where airline_name = %s"
            cursor.execute(query, session['company'])
            print("try2")
            flight_num = cursor.fetchone()
            print(flight_num)
            if flight_num['max(flight_num)']:
                flight_num = flight_num['max(flight_num)'] + 1
            else:
                flight_num = 1
            cursor.close()
            print(flight_num)
            print("try")

            cursor = conn.cursor()
            query1 = "INSERT into flight values (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            cursor.execute(query1, (
            session['company'], flight_num, d_airport, d_time, a_airport, a_time, price, status, airplane_id))
            print("excecute")
            conn.commit()
            cursor.close()
            print("before render")
            return render_template("create_new_flight.html", success="You have successfully created a new flight! ",
                                   flight_num=flight_num, all=all, all_ids=all_ids)
        except:
            return render_template("create_new_flight.html", all=all, all_ids=all_ids)
    except:
        print("except2")
        return render_template("login.html", error="Bad Request")


@app.route('/airline_staff/<staff_email>/add_new_airplanes', methods=["GET", "POST"])
def add_new_airplanes(staff_email):
    try:
        if session['username'] != staff_email or "Admin" not in session['status']:
            return render_template("login.html", error="Bad Request")
        try:
            airplane_id = request.form["airplane_id"]
            seats = request.form["seats"]
            print(airplane_id, seats)
            print(type(airplane_id))
            try:
                airplane_id = int(airplane_id)
                print("here1")
                seats = int(seats)
                print("here2")
                query = "select airplane_id from airplane where airline_name = %s"
                cursor = conn.cursor()
                cursor.execute(query, (session['company']))
                cursor.close()
                print("here3")
                all_id = cursor.fetchall()
                all_ids = []
                print("here4")
                for i in all_id:
                    all_ids.append(i["airplane_id"])
                print(all_ids)
                if airplane_id in all_ids:
                    return render_template("add_new_airplanes.html", error="Input Airplane ID already exists ... ")
                else:
                    query = "INSERT INTO airplane values (%s,%s,%s)"
                    cursor = conn.cursor()
                    print("here6")
                    print(query, session['company'], airplane_id, seats)
                    cursor.execute(query, (session['company'], airplane_id, seats))
                    print("here7")
                    cursor.close()
                    conn.commit()
                    print("here8")
                    return render_template("add_new_airplanes.html", success="Success: ", airplane_id=airplane_id)
            except:
                return render_template("add_new_airplanes.html",
                                       error="Input Airplane ID or seats is not an integer ... ")
        except:
            return render_template("add_new_airplanes.html")
    except:
        return render_template("login.html", error="Bad Request")


@app.route('/airline_staff/<staff_email>/add_new_airports', methods=["GET", "POST"])
def add_new_airports(staff_email):
    try:
        if session['username'] != staff_email or "Admin" not in session['status']:
            return render_template("login.html", error="Bad Request")
        # if I get the form
        try:
            name = request.form['name']
            city = request.form['city']
            print(name, city)
            query = "select * from airport where airport_name = %s "
            cursor = conn.cursor()
            cursor.execute(query, (name.upper()))
            data = cursor.fetchall()
            if data:
                return render_template("add_new_airports.html", error="Sorry, airport already exists ...")
            else:
                print("here2")
                print(name.upper(), city.upper())
                query = "INSERT INTO airport values (%s,%s)"
                cursor.execute(query, (name.upper(), city.upper()))
                print("here3")
                conn.commit()
                cursor.close()
                return render_template("add_new_airports.html", success="Success: ", name=name.upper(),
                                       city=city.upper())
        except:
            return render_template("add_new_airports.html")
    except:
        return render_template("login.html", error="Bad Request")


@app.route('/airline_staff/grant_permission/<staff_email>', defaults={"collegue_email": ''}, methods=["GET", "POST"])
@app.route('/airline_staff/grant_permission/<staff_email>/<collegue_email>', methods=["GET", "POST"])
def grant_permission(staff_email, collegue_email):
    # print('collegue_email', collegue_email)
    try:

        if session['username'] != staff_email or ("Admin" not in session['status']):
            print('case 1')
            return render_template("login.html", error="Incorrect Username or No Admin Permission")

        query = """SELECT airline_staff.username, permission.permission_type
            FROM permission, airline_staff
            WHERE  airline_staff.username = permission.username
            AND airline_staff.airline_name = %s"""
        cursor = conn.cursor()
        cursor.execute(query, (session['company']))
        data = cursor.fetchall()
        # print(session['company'])
        cursor.close()
        print(data)
        # print('case here')
        # print('collegue_email', collegue_email)
        if collegue_email:
            # print('case1')
            selectedP = request.form["selectedP"]
            # print('selectedP', selectedP)
            query = """SELECT *
                FROM permission, airline_staff
                WHERE permission.username = airline_staff.username
                AND permission.permission_type = %s
                AND permission.username = %s"""
            cursor = conn.cursor()
            cursor.execute(query, (selectedP, collegue_email))
            attempt1 = cursor.fetchall()
            cursor.close()
            # print('case2')
            if attempt1:
                error = 'This staff already have this type of permission!'
                # print('case3')
                return render_template("grant_permission.html", data=data, error=error)

            else:
                query = """INSERT INTO permission VALUES (%s, %s)"""
                cursor = conn.cursor()
                cursor.execute(query, (collegue_email, selectedP))
                print('Insert Permission Successfully!')
                conn.commit()
                cursor.close()
                status = 'You have successfully granted ' + str(collegue_email) + ' with ' + str(
                    selectedP) + ' permission!' + '\n' + 'Please go back and reload this page to see the change.'
                try:
                    query = """DELETE FROM permission WHERE permission.username = %s AND permission.permission_type = ''"""
                    cursor = conn.cursor()
                    cursor.execute(query, (collegue_email))
                    print('Delete Blank Permission Successfully!')
                    conn.commit()
                    cursor.close()
                except:
                    print('This person does not have blank permission.')

            return render_template("grant_permission.html", data=data, status=status)
        return render_template("grant_permission.html", data=data)
    except:
        print('Agent Permission Here!')
        return render_template("login.html", error="Bad Request")


@app.route('/airline_staff/add_booking_agents/<staff_email>', methods=["GET", "POST"])
def add_booking_agents(staff_email):
    try:
        if session['username'] != staff_email or ("Admin" not in session['status']):
            print('Incorrect Username or No Admin Permission.')
            return render_template("login.html", error="Incorrect Username or No Admin Permission")

        try:  # if there is input
            if request.form['agentEmail']:
                agentEmail = request.form['agentEmail']

                # Agent not exist
                query = """SELECT * 
                    FROM booking_agent
                    WHERE email = %s"""
                cursor = conn.cursor()
                cursor.execute(query, (agentEmail))
                noAgent = cursor.fetchone()

                if noAgent is None:
                    # print('Cannot find this agent.')
                    return render_template("add_booking_agents.html",
                                           error='Cannot find this agent. Please make sure this agent is already in the system.')

                # Agent already works for company
                query = """SELECT * 
                    FROM booking_agent_work_for
                    WHERE booking_agent_work_for.email = %s
                    AND booking_agent_work_for.airline_name = %s"""
                cursor = conn.cursor()
                cursor.execute(query, (agentEmail, session['company']))
                already = cursor.fetchone()

                if already:
                    # print('This agent already works for the company.')
                    status = 'Agent ' + agentEmail + ' already works for the company ' + str(session['company']) + '.'
                    return render_template("add_booking_agents.html", status=status)

                query = """INSERT INTO booking_agent_work_for VALUES (%s, %s)"""
                cursor = conn.cursor()
                cursor.execute(query, (agentEmail, session['company']))
                print('Add Agent Successfully!')
                conn.commit()
                cursor.close()
                status = 'Agent ' + agentEmail + ' has been added to the company ' + str(session['company']) + '.'

                return render_template("add_booking_agents.html", status=status)
        except:
            # print('There is no input in adding agent.')
            return render_template("add_booking_agents.html")

    except:
        print('Add agent last except here.')
        return render_template("login.html", error="Bad Request")


@app.route('/airline_staff/change_flight_status/<airline_name>/<staff_email>', defaults={'flight_num': ''},
           methods=["GET", "POST"])
@app.route('/airline_staff/change_flight_status/<airline_name>/<staff_email>/<flight_num>', methods=["GET", "POST"])
def change_flight_status(airline_name, staff_email, flight_num):
    # return render_template('change_flight_status.html')
    # For 1 user Airline Name is not changing. It should be the user's company.
    try:
        if session['username'] != staff_email or ("Operator" not in session['status']):
            print('Incorrect Username or No Admin Permission.')
            return render_template("login.html", error="Incorrect Username or No Operator Permission")

        query = """SELECT * 
            FROM flight
            WHERE airline_name = %s"""
        cursor = conn.cursor()
        cursor.execute(query, (session['company']))
        data = cursor.fetchall()
        print('here1')

        if flight_num:  # if there is input
            selectedS = request.form['selectedS']
            flight_num = int(flight_num)
            query = """SELECT * 
                FROM flight
                WHERE airline_name = %s
                AND flight_num = %s
                AND status = %s"""
            cursor = conn.cursor()
            cursor.execute(query, (airline_name, flight_num, selectedS))
            already = cursor.fetchall()

            if already:
                status = 'This flight is already ' + str(selectedS)
                return render_template('change_flight_status.html', status=status)

            query = """UPDATE `flight` 
                SET `status` = %s
                WHERE `flight`.`airline_name` = %s 
                AND `flight`.`flight_num` = %s"""
            cursor = conn.cursor()
            cursor.execute(query, (selectedS, airline_name, flight_num))
            print('Flight Status Updated')
            conn.commit()
            cursor.close()
            status = 'You have successfully updated ' + str(airline_name) + ' ' + str(flight_num) + ' into ' + str(
                selectedS) + '! Please go back and reload this page to see the change.'
            return render_template('change_flight_status.html', status=status, data=data)
        return render_template('change_flight_status.html', data=data)
    except:
        print('change flight status last except here.')
        return render_template("login.html", error="Bad Request")


# 有问题超过gap>1只能显示第一年============
@app.route('/airline_staff/detailed_reports/<staff_email>', methods=["GET", "POST"])
def detailed_reports(staff_email):
    month = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    error = None
    try:

        if session['username'] != staff_email:
            print('Incorrect Username')
            return render_template("login.html", error="Incorrect Username")

        # set date names
        today = datetime.date.today()
        lastMonth = today - datetime.timedelta(days=31)
        lastYear = today - datetime.timedelta(days=365)
        # print(type(today.year), type(lastYear.year))

        # get the num of tkt last month
        query = """select COUNT(ticket.ticket_id) 
            from purchases, ticket 
            where ticket.airline_name = %s 
            and ticket.ticket_id  = purchases.ticket_id 
            and purchases.p_date <= %s 
            and %s <= purchases.p_date"""
        cursor = conn.cursor()
        cursor.execute(query, (session['company'], today, lastMonth))
        lastMTotTkt = cursor.fetchall()
        cursor.execute(query, (session['company'], today, lastYear))
        lastYTotTkt = cursor.fetchall()
        cursor.close()

        # get the num of tkt last year

        query = """select ticket.ticket_id, purchases.p_date
            from purchases, ticket 
            where ticket.airline_name = %s
            and ticket.ticket_id  = purchases.ticket_id 
            and purchases.p_date <= %s 
            and %s <= purchases.p_date"""
        cursor = conn.cursor()
        cursor.execute(query, (session['company'], today, lastYear))
        info = cursor.fetchall()
        cursor.close()

        thisMonth = today.month  # last_month
        begin_month = thisMonth - 12  # begin_month
        # print(type(today.year))

        pairs = {}

        for record in info:
            if today > record['p_date'] >= lastYear:
                # print("1")
                mon = record['p_date'].month
                print(mon)

                thisMon = month[mon - 1]
                pairs[thisMon] = pairs.get(thisMon, 0) + 1

                # if thisMonth >= mon:
                #     ticketNum[(5-thisMonth+mon)%12] += 1
                # else:
                #     ticketNum[(-12-thisMonth+mon)%12] += 1

        x_axis = [month[i] for i in range(begin_month, begin_month + 12)]
        ticketNum = []
        for i in x_axis:
            if i not in pairs.keys():
                ticketNum.append(0)
            else:
                ticketNum.append(pairs[i])

        plt.bar(x_axis, ticketNum)
        plt.title('Month-wise Num of Tkt Sold in Last Year')
        plt.xlabel('Month')
        plt.ylabel('Ticket Number')
        for a, b in zip(x_axis, ticketNum):
            plt.text(a, b, b, ha='center', va='bottom', fontsize=7)
        # save as binary file
        buffer = BytesIO()
        plt.savefig(buffer)
        plot_data = buffer.getvalue()

        # 将matplotlib图片转换为HTML
        imb = base64.b64encode(plot_data)  # 对plot_data进行编码
        ims = imb.decode()
        image5 = "data:image/png;base64," + ims
        plt.close()

        try:
            fromDate = request.form['fromDate']
            fromDate1 = datetime.datetime.date(datetime.datetime.strptime(fromDate, '%Y-%m-%d'))
            toDate = request.form['toDate']
            toDate1 = datetime.datetime.date(datetime.datetime.strptime(toDate, '%Y-%m-%d'))

            if fromDate > toDate:
                error = 'invalid date input'
                return render_template("detailed_reports.html", error=error)

            query = """select ticket.ticket_id, purchases.p_date
                from purchases, ticket 
                where ticket.airline_name = %s
                and ticket.ticket_id  = purchases.ticket_id 
                and purchases.p_date <= %s 
                and %s <= purchases.p_date"""
            cursor = conn.cursor()
            cursor.execute(query, (session['company'], toDate, fromDate))
            dataRange = cursor.fetchall()
            cursor.close()

            # print(toDate, fromDate)
            # print(fromDate1.year, toDate1.year)
            thisMonth = (toDate1.year, toDate1.month)  # last_month
            begin_month = (fromDate1.year, fromDate1.month)  # begin_month

            gap = toDate1.year - fromDate1.year

            pairs = {}

            # print(type(begin_month[0]), type(begin_month[1]))
            curM = [begin_month[0], begin_month[1]]
            # print('here4')

            if gap > 0:
                while (curM[0] != thisMonth[0]) or ((curM[1] - 1) != thisMonth[1]):
                    # print('curM[0], thisMonth[0], curM[1], thisMonth[1]',curM[0], thisMonth[0], curM[1], thisMonth[1] )
                    nameM = str(curM[0]) + '-' + str(curM[1])
                    pairs[nameM] = pairs.get(nameM, 0)
                    curM[1] += 1
                    if curM[1] == 13:
                        curM[0] += 1
                        curM[1] = 1

            # print('here5')
            if gap == 0:
                # print('here1')
                print(curM[1] != thisMonth[1])
                while (curM[1] - 1) != thisMonth[1]:
                    nameM = str(curM[0]) + '-' + str(curM[1])
                    pairs[nameM] = pairs.get(nameM, 0)
                    curM[1] += 1

            # print('pairs', pairs)
            # print('gap', gap)

            for record in dataRange:

                # print(type(toDate1),type(record['purchase_date']),type(fromDate1))
                # print(toDate1 > record['purchase_date'])
                if toDate1 > record['p_date'] >= fromDate1:
                    # print("1")
                    mon = record['p_date'].month
                    # print('month', mon)

                    thisMon = str(record['p_date'].year) + '-' + str(mon)
                    # print(record['p_date'].year)
                    pairs[thisMon] = pairs.get(thisMon, 0) + 1
                    # print('here1')

            # print('here7')
            x_axis = list(pairs.keys())
            ticketNum = []
            for i in x_axis:
                if i not in pairs.keys():
                    ticketNum.append(0)
                else:
                    ticketNum.append(pairs[i])

            # print('here8')
            plt.bar(x_axis, ticketNum)
            plt.title('Month-wise Num of Tkt Sold from ' + str(fromDate1) + ' to ' + str(toDate1))
            plt.xlabel('Month')
            plt.ylabel('Ticket Number')
            for a, b in zip(x_axis, ticketNum):
                plt.text(a, b, b, ha='center', va='bottom', fontsize=7)
            # save as binary file
            buffer = BytesIO()
            plt.savefig(buffer)

            plot_data = buffer.getvalue()

            # 将matplotlib图片转换为HTML
            imb = base64.b64encode(plot_data)  # 对plot_data进行编码
            ims = imb.decode()
            image6 = "data:image/png;base64," + ims
            plt.close()

            return render_template("detailed_reports.html", lastMTotTkt=lastMTotTkt, image5=image5,
                                   lastYTotTkt=lastYTotTkt, image6=image6)
        except:
            print('No user input in Detailed Report.')

        return render_template("detailed_reports.html", lastMTotTkt=lastMTotTkt, image5=image5, lastYTotTkt=lastYTotTkt)
    except:
        print('In router detailed report.')
        return render_template("login.html", error="Bad Request")


@app.route('/airline_staff/view_freq_c/<staff_email>/<customer_email>', methods=["GET", "POST"])
def view_freq_c(staff_email, customer_email):
    try:

        if session['username'] != staff_email:
            print('Incorrect Username')
            return render_template("login.html", error="Incorrect Username")

        query = """SELECT flight.flight_num, flight.departure_airport, 
            flight.departure_time, flight.arrival_airport, flight.arrival_time,
            flight.price, flight.status, flight.airplane_id,
            ticket.ticket_id, purchases.booking_agent_email, purchases.p_date
            FROM flight, ticket, purchases
            WHERE flight.airline_name = ticket.airline_name
            AND flight.flight_num = ticket.flight_num
            AND ticket.ticket_id = purchases.ticket_id
            AND flight.airline_name = %s
            AND purchases.customer_email = %s"""
        cursor = conn.cursor()
        cursor.execute(query, (session['company'], customer_email))
        data = cursor.fetchall()
        cursor.close()

        return render_template("view_freq_c.html", data=data, customer_email=customer_email)
    except:
        print('Fail in view_freq_c')
        return render_template("login.html", error="Bad Request")


@app.route("/airline_staff/view_customer/<username>/<flight_num>/<airline_name>", methods=["GET", "POST"])
def view_customer(flight_num, airline_name, username):
    try:
        if session['username'] != username:
            print("case1")
            return render_template("login.html", error1="Bad Request: username does not match")
        cursor = conn.cursor()
        query = "select purchases.customer_email from ticket,purchases where ticket.airline_name = %s and ticket.flight_num  = %s and purchases.ticket_id = ticket.ticket_id"
        cursor.execute(query, (airline_name, flight_num))
        customer_lst = cursor.fetchall()
        cursor.close()
        print(customer_lst)
        return render_template("view_all_customer.html", airline_name=airline_name, flight_num=flight_num,
                               customer=customer_lst)
    except:
        return render_template("login.html", error="Bad Request")


# general
@app.route('/upcoming_flight/search', methods=['GET', 'POST'])
def upcoming_flight_search():
    query = "SELECT * from flight where"
    appendix = ""
    if request.form['departure_date']:
        d_date = request.form['departure_date']
        d_start = datetime.datetime.strptime(d_date, '%Y-%m-%d')
        d_end = d_start + datetime.timedelta(days=1)
        add = "and '" + str(d_start)[:10] + "' <=departure_time  and departure_time <='" + str(d_end)[:10] + "'"
        appendix += add
    if request.form['arrival_date']:
        a_date = request.form['arrival_date']
        a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
        a_end = a_start + datetime.timedelta(days=1)
        dd = "and '" + str(a_start)[:10] + "' <=arrival_time  and arrival_time <='" + str(a_end)[:10] + "'"
        appendix += query
    if request.form['flight']:
        flight_num = request.form['flight']
        appendix += "and flight_num = "
        appendix += flight_num
    if request.form['departure_airport']:
        d_airport = request.form['departure_airport']
        appendix += "and departure_airport = '"
        appendix += d_airport
        appendix += "'"
    if request.form['arrival_airport']:
        a_airport = request.form['arrival_airport']
        appendix += "and arrival_airport = '"
        appendix += a_airport
        appendix += "'"
    if request.form['departure_city']:
        d_city = request.form['departure_city']
        add = "and departure_airport in (select airport_name from airport where airport_city ='" + d_city + "')"
        appendix += add
    if request.form['arrival_city']:
        a_city = request.form['arrival_city']
        add = "and arrival_airport in (select airport_name from airport where airport_city = '" + a_city + "')"
        appendix += add
    if appendix == "":
        query = "SELECT * from flight"
    else:
        query += appendix[3:]
    print(query)
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    cursor.execute(query)
    # stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    error = None
    print(data)
    if (data):
        # creates a session for the the user
        # session is a built in
        return render_template('upcoming_flight.html', upcoming_flight=data)
    else:
        return render_template('upcoming_flight.html',
                               error1="Sorry, no flights are found. Please check your input again.")


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)