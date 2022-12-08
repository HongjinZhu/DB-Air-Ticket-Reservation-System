-- a. One Airline name "China Eastern".
INSERT INTO airline VALUES ('China Eastern');

-- b. At least Two airports named "JFK" in NYC and "PVG" in Shanghai.
INSERT INTO airport VALUES ('JFK', 'NYC');
INSERT INTO airport VALUES ('PVG', 'Shanghai');
INSERT INTO airport VALUES ('TFU', 'Chengdu');

-- c. Insert at least two customers with appropriate names and other attributes.
-- Insert one booking agent with appropriate name and other attributes.
INSERT INTO customer VALUES ('ws1587@nyu.edu','Karen Shi','ksisabeautifulwoman','895','Pusan Road','Shanghai','Shanghai','13785785757','EA5000000','2028-6-6','China','1960-11-24');
INSERT INTO customer VALUES ('traderjoes@gmail.com','Trader Joes','wholefoodsbadbad','142','E 14th St','NYC','NY','1008610000','E40088208','2030-10-22','The United States','1988-2-19');
INSERT INTO BookingAgent VALUES ('leilee@ythx.com','seeyouinmioin11','E30598','China Eastern');

-- d. Insert at least two airplanes.
INSERT INTO airplane VALUES ('China Eastern','109',300);
INSERT INTO airplane VALUES ('China Eastern','2290',278);

-- e. Insert At least One airline Staff working for China Eastern.
INSERT INTO airlinestaff VALUES ('EchoZhang','China Eastern','ihateyqsbking588','Echo','Zhang','1994-6-24');
INSERT INTO permission VALUES ('EchoZhang','Admin');
INSERT INTO airlinestaff VALUES ('JYP','China Eastern','idontlikeyg','J','YP','1981-11-11');
INSERT INTO permission VALUES ('JYP','Operator');

-- f. Insert several flights with upcoming, in-progress, delayed statuses.
INSERT INTO flight VALUES ('MU5406','China Eastern','2290','TFU','PVG','2022-10-26 09:30','2022-10-26 12:00',485.00, 'in-progress');
INSERT INTO flight VALUES ('MU2220','China Eastern','109','TFU','PVG','2022-10-27 07:55','2022-10-27 10:40',497.00, 'upcoming');
INSERT INTO flight VALUES ('MU588','China Eastern','2290','JFK','PVG','2022-11-7 15:25','2022-11-8 19:15',40722.00, 'delayed');

-- g. Insert some tickets for corresponding flights.
-- One customer buy ticket directly and one customer buy ticket using a booking agent.
INSERT INTO ticket VALUES ('99930456888','MU5406');
INSERT INTO purchases VALUES ('99930456888','ws1587@nyu.edu', null,'2022-10-23');
INSERT INTO ticket VALUES ('99930456877','MU5406');
INSERT INTO purchases VALUES ('99930456877','traderjoes@gmail.com','leilee@ythx.com','2022-10-23');