-- View Public Info
-- information in the brackets should be grabbed from html
SELECT * FROM flight
WHERE {chosen start date} <= depart_time and {chosen end date} >= arrive_time
and depart_name = {} and arrive_name = {} and departure_city = {} and arrival_city = {}

-- Login
-- authentication
-- customer log in
SELECT * FROM customer WHERE email = '{}';
-- staff log in
SELECT * FROM airlineStaff WHERE username = '{}';
SELECT permission from permission where permission.username = '{}';
select airline_name from airlineStaff where airlineStaff.username = '{}';
-- booking agent log in
SELECT * FROM bookingagent WHERE email = '{}';
SELECT airline_name from bookingagent WHERE email = '{}'

-- Register
-- authentication
-- customer
SELECT * FROM customer WHERE email = '{}'
INSERT INTO customer VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
-- format(email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday)

-- agent
SELECT * FROM bookingagent WHERE email = '{}'
SELECT * FROM airline WHERE name = '{}'
SELECT b_id FROM bookingagent WHERE b_id = '{}'
INSERT INTO bookingagent VALUES('{}', '{}', '{}','{}')

-- staff
-- after checking staff not existed in db
INSERT INTO airlinestaff VALUES('{}', '{}', '{}','{}', '{}', '{}')
INSERT INTO permission VALUES('{}', '{}')



-- Customer
select * from flight 
where flight_status ="upcoming" 
and (flight_num) in 
(select flight_num from ticket where ticket_id in 
(select purchases.ticket_id from purchases where customer_email = {customer_email}))
-- find all the upcoming flight that the customer purchases
select * from flight 
where (flight_num) in 
(select flight_num from ticket where ticket_id in 
(select purchases.ticket_id from purchases where customer_email = %s and p_date <= %s and p_date >= %s))
-- find all the filght that the customer purchases in the period of time, in this case is one year, and calculate the spend of the customer
SELECT price, p_date 
FROM ticket NATURAL JOIN purchases NATURAL JOIN flight 
WHERE purchases.customer_email = '%s'
-- find the price and purchases date for that customer to find the each month's spent in the past 6 months
SELECT price, p_date 
FROM ticket NATURAL JOIN purchases NATURAL JOIN flight 
WHERE customer_email = '{}'
and p_date <= '{}'
and p_date >= '{}'
-- find the price and purchases date for that customer in the specific time range to find the each month's spent in that range
select * from flight 
where flight_status ="upcoming" and (flight_num) in 
(select flight_num from ticket where ticket_id in 
(select purchases.ticket_id from purchases where purchases.customer_email = %s))
-- find all the upcoming flight that the customer purchases and in this case it will append more condiction later to find the flights
select * from purchases, ticket, flight 
where purchases.customer_email = %s 
and purchases.ticket_id = ticket.ticket_id 
and ticket.flight_num=flight.flight_num
and ticket.flight_num = %s
and flight.airline_name = %s
-- find the ticket that the customer buy for the specific flight_num and airline_name to check if customer has already bought the ticket
select seats from airplane where airline_name = %s
and ID in (select airplane_id from flight where airline_name = %s and flight_num = %s)
-- find the number of seats of the specific flight_num and airline_name to check if there are no room to buy
SELECT count(*)
FROM ticket,flight
WHERE ticket.flight_num=flight.flight_num
and flight.airline_name = %s
and ticket.flight_num = %s
-- find the number of seats that have already sold of the specific flight_num and airline_name to check if there are no room to buy
select max(ticket_id) from purchases
-- find the biigest ticket_id to create a new ticket_id
insert into ticket values( %s, %s)
-- create new ticket
INSERT INTO purchases(ticket_id,customer_email,p_date) VALUES(%s,%s,%s)
-- create the purchases record


-- Booking Agent
select flight.airline_name, flight.flight_num, 
flight.depart_name, flight.depart_time, flight.arrive_name, flight.arrive_time,
flight.price, flight.flight_status, flight.airplane_id, purchases.customer_email
from flight join ticket join purchases
where flight_status ="upcoming" 
and ticket.flight_num = flight.flight_num
AND ticket.ticket_id = purchases.ticket_id
and (flight.airline_name, ticket.flight_num) in 
(select flight.airline_name,ticket.flight_num from ticket join flight
where ticket_id in 
(select purchases.ticket_id from purchases where booking_agent_email = %s))
-- find all the upcoming flight that the agent purchases
select * from flight, ticket
where flight.flight_num = ticket.flight_num
and ticket.ticket_id in 
(select purchases.ticket_id 
from purchases 
where p_date <= %s
and p_date >= %s
and booking_agent_email = %s )
-- find all the filght that the agent purchases in the period of time, in this case is one month, and calculate the commission of the agent
select count(flight.flight_num) AS 'totnum', purchases.customer_email
from flight join purchases join ticket
where flight.flight_num = ticket.flight_num
AND purchases.ticket_id = ticket.ticket_id
AND purchases.booking_agent_email = %s
AND purchases.p_date >= %s
AND purchases.p_date <= %s
GROUP BY purchases.customer_email
ORDER by totnum desc
LIMIT 5
-- find top 5 consuter that purchases the largest number of ticket from this agent in the period of time
select sum(flight.price) AS 'totprice', purchases.customer_email
from flight join purchases join ticket
where flight.flight_num = ticket.flight_num
AND purchases.ticket_id = ticket.ticket_id
AND purchases.booking_agent_email = %s
AND purchases.p_date >= %s
AND purchases.p_date <= %s
GROUP BY purchases.customer_email
ORDER by totprice desc
LIMIT 5
-- find top 5 consuter that purchases the largest amonut of money from this agent in the period of time
select * from flight, ticket
where flight.flight_num = ticket.flight_num
and ticket.ticket_id in 
(select purchases.ticket_id 
from purchases 
where p_date <= %s
and p_date >= %s
and booking_agent_email = %s )
-- find all the filght that the agent purchases in the period of time, and calculate the commission of the agent
select flight.airline_name, flight.flight_num, 
flight.depart_name, flight.depart_time, flight.arrive_name, flight.arrive_time,
flight.price, flight.flight_status, flight.airplane_id, purchases.customer_email
from flight, ticket, purchases
where flight.flight_status ="upcoming" 
and ticket.flight_num = flight.flight_num
AND ticket.ticket_id = purchases.ticket_id
and (flight.airline_name, flight.flight_num) in 
(select flight.airline_name, ticket.flight_num from ticket, flight
where flight.flight_num = ticket.flight_num and ticket.ticket_id in 
(select purchases.ticket_id from purchases where booking_agent_email = '{}'))
-- find all the upcoming flight that the agent purchases and in this case it will append more condiction later to find the flights
select email from customer WHERE email = %s
-- find all the customer email to check if the input email is valid
select * from purchases, ticket 
where purchases.ticket_id = ticket.ticket_id 
and ticket.flight_num = %s
AND customer_email = %s
-- find the ticket that the customer buy for the specific flight_num and airline_name to check if customer has already bought the ticket
select seats from airplane where airline_name = %s
and ID in (select airplane_id from flight where airline_name = %s and flight_num = %s)
-- find the number of seats of the specific flight_num and airline_name to check if there are no room to buy
SELECT count(*)FROM ticket WHERE flight_num = %s
-- find the number of seats that have already sold of the specific flight_num to check if there are no room to buy
select max(ticket_id) from purchases
-- find the biigest ticket_id to create a new ticket_id
insert into ticket values(%s, %s)
-- create new ticket
INSERT INTO purchases(ticket_id,customer_email, booking_agent_email,p_date) VALUES(%s,%s,%s,%s)
-- create the purchases record




-- Staff
-- search flight similar to public search only specifying
select * from flight where airline_name = '{}'
-- view top agents (last month or last year similarly)
select purchases.booking_agent_email
from purchases
where purchases.p_date <= %s  
and purchases.p_date >= %s 
and purchases.booking_agent_email is NOT NULL 
and purchases.ticket_id in (
    select ticket_id 
    from ticket NATURAL JOIN flight 
    where airline_name = %s) 
group by purchases.booking_agent_email 
ORDER BY count(purchases.ticket_id) DESC LIMIT 5
-- view top customers
select purchases.customer_email,count(purchases.ticket_id) 
from purchases, ticket, flight 
where flight.flight_num = ticket.flight_num 
	and ticket.ticket_id = purchases.ticket_id 
	and flight.airline_name = %s 
	and purchases.p_date <= %s and %s <= purchases.p_date 
GROUP BY purchases.customer_email 
ORDER BY count(purchases.ticket_id) DESC LIMIT 10;

-- view frequent customers
SELECT flight.airline_name, flight.flight_num, flight.depart_name, 
			flight.depart_time, flight.arrive_name, flight.arrive_time,
			flight.price, flight.flight_status, flight.airplane_id,
			ticket.ticket_id, purchases.booking_agent_email, purchases.p_date
FROM flight, ticket, purchases
WHERE flight.flight_num = ticket.flight_num
    AND ticket.ticket_id = purchases.ticket_id
    AND flight.airline_name = %s
    AND purchases.customer_email = %s;

-- view customers on a flight
select purchases.customer_email 
from ticket,purchases,flight
where flight.airline_name = %s 
    and ticket.flight_num = flight.flight_num
    and ticket.flight_num  = %s 
    and purchases.ticket_id = ticket.ticket_id

-- view top destinations
select airport.city 
from airport, flight 
where flight.arrive_name = airport.name 
    AND flight.depart_time <= %s 
    and flight.depart_time >= %s 
GROUP BY airport.city 
ORDER BY count(flight.arrive_time) DESC LIMIT 3
-- view report
select COUNT(ticket.ticket_id) 
from purchases, ticket, flight 
where flight.flight_num = ticket.flight_num 
    and flight.airline_name = %s 
    and ticket.ticket_id  = purchases.ticket_id 
    and purchases.p_date <= %s 
    and %s <= purchases.p_date
-- comparing direct and indirect revenue
-- directly from customer (where booking agent entry is null)
SELECT SUM(flight.price) AS 'totalprice'
FROM flight, ticket, purchases
WHERE flight.flight_num = ticket.flight_num
	AND ticket.ticket_id = purchases.ticket_id
	AND flight.airline_name = %s
	AND purchases.booking_agent_email is NULL
	AND purchases.p_date <= %s
	AND purchases.p_date >= %s
-- indirectly through agent
SELECT SUM(flight.price) AS 'totalprice'
FROM flight, ticket, purchases
WHERE flight.flight_num = ticket.flight_num
	AND ticket.ticket_id = purchases.ticket_id
	AND flight.airline_name = %s
	AND purchases.booking_agent_email is not NULL
	AND purchases.p_date <= %s
	AND purchases.p_date >= %s

-- create new flight
select name from airport; -- to gain a list of airports
select ID from airplane where airline_name = %s; -- specify staff's authority
INSERT into flight values (%s,%s,%s,%s,%s,%s,%s,%s,%s); -- flight_num, airline_name, airplane_id, d_airport, a_airport, d_time, a_time, price, status
-- add new plane
select ID from airplane where airline_name = %s;
INSERT INTO airplane values (%s,%s,%s); -- format: airline_name, airplane_id, seats
-- add new airports
select * from airport where name = %s;
INSERT INTO airport values (%s,%s); -- format: airport_name, city
-- grant permissions
SELECT airlinestaff.username, permission.permission
FROM permission, airlinestaff
WHERE  airlinestaff.username = permission.username
	AND airlinestaff.airline_name = %s;

SELECT * FROM permission, airlinestaff
WHERE permission.username = airlinestaff.username
	AND permission.permission = %s
	AND permission.username = %s; -- above are checking steps
-- inserting steps ↓
INSERT INTO permission VALUES (%s, %s); -- format: staff_email, permission

-- add booking agents
SELECT * FROM bookingagent WHERE email = %s; -- check if existed
SELECT *  FROM bookingagent WHERE email = %s AND airline_name = %s; -- check if already worked for this company
UPDATE bookingagent SET airline_name = %s WHERE email = %s; -- format:airline_name, agent_email

-- change status of flights
SELECT * FROM flight 
WHERE airline_name = %s
	AND flight_num = %s
	AND flight_status = %s;

UPDATE flight SET flight_status = %s
WHERE flight.airline_name = %s AND flight.flight_num = %s;

-- detailed report (number of tickets sold)
select COUNT(ticket.ticket_id) 
from purchases, ticket, flight
where ticket.flight_num = flight.flight_num
    and flight.airline_name = %s 
    and ticket.ticket_id  = purchases.ticket_id 
    and purchases.p_date <= %s 
    and %s <= purchases.p_date;

select ticket.ticket_id, purchases.p_date
from purchases, ticket, flight
where flight.airline_name = %s
    and ticket.flight_num = flight.flight_num
    and ticket.ticket_id  = purchases.ticket_id 
    and purchases.p_date <= %s 
    and %s <= purchases.p_date;