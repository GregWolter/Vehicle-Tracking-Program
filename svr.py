# CS 366 Final Project
# This program takes the inputs sent by the client and returns to the client a variety of useful data
# including location, nearest gas station, nearby vehicles, all vehicles, distance traveled, direction traveling,
# weather data, and then closes the connection. Handles input validation.
# 8/1/2021
# By; Greg Wolter
#!/usr/bin/python3

import socket
import sys
import math
import os
import _thread as thread

HOST = '127.0.0.1'	# the listening IP
PORT = 3660	            # the listening port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
# Binds address (hostname and port number pair) to socket
	s.bind((HOST, PORT))
except socket.error:
	print('Bind failed.')
	sys.exit()

print('Socket bind complete')

# Start listening on socket, the size of queue is 10
s.listen(10)
print('Socket now listening')

# A list of coordinates of gas stations.
gas_stations = [(50, 50), (50, 100), (100, 50), (100, 100), (150, 50), (150, 100)]

# The center point of a severe weather storm.
severe_weather = (10, 10)

# Returns the coordinates of the vehicle's location and the distance traveled
def get_location(x, y, speed, direction, time_driving):
	# Initialize the return variable
	location = (0, 0, 0)
	location_list = list(location)
	# Calculates Location with given direction, speed, time, and starting point.
	if direction == 'N':
		distance = float(speed) * float(time_driving)
		north_change = float(y) + distance
		location_list[0] = float(x)
		location_list[1] = north_change
		location_list[2] = distance
		return location_list
	if direction == 'S':
		distance = float(speed) * float(time_driving)
		south_change = float(y) - distance
		location_list[0] = float(x)
		location_list[1] = south_change
		location_list[2] = distance
		return location_list
	if direction == 'E':
		distance = float(speed) * float(time_driving)
		east_change = float(x) + distance
		location_list[0] = east_change
		location_list[1] = float(y)
		location_list[2] = distance
		return location_list
	if direction == 'W':
		distance = float(speed) * float(time_driving)
		west_change = float(x) - distance
		location_list[0] = west_change
		location_list[1] = float(y)
		location_list[2] = distance
		return location_list

# If the client's vehicle location is in a severe weather storm returns true, else false.
# Parameters are the coordinates of the client's vehicle location.
def in_severe_weather(current_x, current_y):
	x_distance_squared = abs(severe_weather[0] - current_x) ** 2
	y_distance_squared = abs(severe_weather[1] - current_y) ** 2
	distance = math.sqrt(x_distance_squared + y_distance_squared)
	# The average weather storm has a 15 mile diameter so we will check the distance from the severe weather center
	if distance < 7.5:
		return True
	else:
		return False

# Returns the coordinates of the nearest gas station based on the client's vehicle coordinates as parameters.
def get_nearest_gas_station(current_x, current_y):
	# Initial index is first index in list
	closest_index = 0
	# Loops through each gas station and uses pythagorean theorem to calculate distance
	for each in gas_stations:
		x_distance_squared = abs(each[0] - current_x) ** 2
		y_distance_squared = abs(each[1] - current_y) ** 2
		distance = math.sqrt(x_distance_squared + y_distance_squared)
		# Checks if it is the first index of the loop.
		if gas_stations.index(each) > 0:
			# If it is not the first index, it determines if the distance calculated is the new smallest distance
			if distance < previous_distance:
				closest_index = gas_stations.index(each)
		# If it is the first index in the loop store it as previous distance.
		else:
			previous_distance = distance
	return gas_stations[closest_index]

# Initializes an empty list of vehicle locations
vehicle_locations = []
vehicles_within_fifty_miles = []

# Returns a list of all vehicle locations, direction, and speed and adds the vehicle's information passed
# as parameters to the list of all vehicles.
def add_location(current_x, current_y, speed, direction):
	vehicle_locations.append((current_x, current_y, direction, speed))
	return vehicle_locations

# Returns a list of all vehicles locations within a 50 mile radius of the client based on coordinates as parameters.
def vehicles_nearby(current_x, current_y):
	# Clears the old list (which would be for a previous client if any)
	vehicles_within_fifty_miles.clear()
	# Loops through each other vehicle to check if it is within a 50 mile radius
	for each in vehicle_locations:
		x_distance_squared = abs(each[0] - current_x) ** 2
		y_distance_squared = abs(each[1] - current_y) ** 2
		distance = math.sqrt(x_distance_squared + y_distance_squared)
		# Checks if distance is less than 50, and won't add the client's own vehicle to the list.
		if distance < 50 and distance != 0:
			vehicles_within_fifty_miles.append(each)
	return vehicles_within_fifty_miles

# Checks if string is a positive number
# https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
def is_positive_number(n):
	try:
		float(n)
		if float(n) > 0:
			return True
		else:
			return False
	except ValueError:
		return False

# Function for handling connections. This will be used to create threads
def clientthread(conn):
	#infinite loop so that function do not terminate and thread do not end.
	while True:
		
		# Receiving from client
		data = conn.recv(1024)
		if not data: 
			break
		# Creates a string object of the message sent from the client
		information = data.decode("utf-8")

		# Handles client input validation
		try:
			# Splits the message into an array
			array = information.split()

			# Determines location of vehicle by calling get_location and stores it as new_location
			new_location = get_location(array[0], array[1], array[2], array[3], array[4])

			# Handles null pointer
			if new_location is not None:
				# Determines nearest gas station by method call and stores as nearest_gas_station
				nearest_gas_station = get_nearest_gas_station(new_location[0], new_location[1])

				# Adds the vehicle to the server's list of vehicles
				# Checks if the client's speed changed
				if is_positive_number(array[5]):
					new_vehicle_locations = add_location(new_location[0], new_location[1], array[5], array[3])
				else:
					new_vehicle_locations = add_location(new_location[0], new_location[1], array[2], array[3])

				# Determines the vehicles within fifty miles
				nearby_vehicles = vehicles_nearby(new_location[0], new_location[1])

				# Checks if vehicle is in severe weather
				if in_severe_weather(new_location[0], new_location[1]):
					partial_reply = "are"
				else:
					partial_reply = "are not"

				reply = "(" + str(new_location[0]) + ", " + str(new_location[1]) + "). " \
						"\nYou " + partial_reply + " in a severe weather storm."\
						"\nYou are traveling " + array[3] + " and have traveled " + str(new_location[2]) + " miles."\
						"\nThe nearest gas station is located at: " + str(nearest_gas_station) + \
						". \nHere is a list of vehicle locations along with their traveling" \
						" speed and direction (the one you just entered is included): \n" + str(new_vehicle_locations) +\
						"\nThere are " + str(len(nearby_vehicles)) + " vehicles within a 50 mile radius of you."\
						"\nHere is a list of vehicle locations, direction, and speed within a 50 mile radius of you.\n" +\
						str(nearby_vehicles)
			else:
				reply = 'You did not enter valid coordinates or direction'
		except ValueError:
			reply = 'You did not enter valid coordinates or direction'
		print('Welcome to the Server. This is the location of your vehicle: ' + reply)

		conn.sendall(reply.encode())
		# force flush for nohup
		sys.stdout.flush()

	# came out of loop if there is no data from the client
	conn.close()

# now keep talking with the client
while True:
    # wait to accept a connection - blocking call
    # it will wait/hang until a connection request is coming
	conn, addr = s.accept()
	print('Connected with ' + addr[0] + ':' + str(addr[1]))
	
	# start new thread takes 1st argument as a function name to be run,
    # second is the tuple of arguments to the function.
	thread.start_new_thread(clientthread, (conn,))

s.close()
