CREATE TABLE Airline(
	name varchar(20),
	PRIMARY KEY (name));

CREATE TABLE AirlineStaff(
    username varchar(20) NOT null,
    airline_name varchar(20),
    s_password varchar(256),
    first_name varchar(20),
    last_name varchar(20),
    date_of_birth date,
    PRIMARY KEY(username),
    FOREIGN KEY (airline_name) REFERENCES Airline(name));

CREATE TABLE Permission(
    username varchar(20) NOT null,
    permission varchar(20),
    FOREIGN KEY (username) REFERENCES AirlineStaff(username));

CREATE TABLE Airplane(
	airline_name varchar(20),
	ID varchar(20),
	seats numeric(5,0),
	PRIMARY KEY (ID),
	FOREIGN KEY (airline_name) REFERENCES Airline(name));
    
CREATE TABLE Airport(
    name varchar(20),
    city varchar(20),
    PRIMARY KEY (name));
    
CREATE TABLE Flight(
    flight_num varchar(20),
    airline_name varchar(20),
    airplane_id varchar(20),
    depart_name varchar(20),
    arrive_name varchar(20),
    depart_time datetime,
    arrive_time datetime,
    price numeric(10,2),
    flight_status varchar(20),
    PRIMARY KEY (flight_num),
    FOREIGN KEY (airline_name) REFERENCES Airline(name),
    FOREIGN KEY (airplane_id) REFERENCES Airplane(ID),
    FOREIGN KEY (depart_name) REFERENCES Airport(name),
    FOREIGN KEY (arrive_name) REFERENCES Airport(name));

CREATE TABLE Ticket(
    ticket_id varchar(20),
    flight_num varchar(20),
    PRIMARY KEY (ticket_id),
    FOREIGN KEY (flight_num) REFERENCES Flight(flight_num));

CREATE TABLE Customer(
    email varchar(20),
    name varchar(20),
    c_password varchar(256),
    building_number numeric(10,0),
    street varchar(20),
    city varchar(20),
    state varchar(20),
    phone_number numeric(20,0),
    passport_number varchar(20),
    passport_expiration date,
    passport_country varchar(20),
    date_of_birth date,
    PRIMARY KEY (email));
    
CREATE TABLE BookingAgent(
    email varchar(20),
    b_password varchar(256),
    b_id varchar(20),
    airline_name varchar(20),
    PRIMARY KEY (email),
    FOREIGN KEY (airline_name) REFERENCES airline(name));
    
CREATE TABLE purchases(
    ticket_id varchar(20),
    customer_email varchar(20),
    booking_agent_email varchar(20),
    p_date date,
    FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
    FOREIGN KEY (customer_email) REFERENCES Customer(email),
    FOREIGN KEY (booking_agent_email) REFERENCES BookingAgent(email));
