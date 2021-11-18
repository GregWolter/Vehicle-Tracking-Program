# CS 366 Final Project
# This vehicle tracking program takes the user inputs (starting point, speed, time, direction) and sends to the server.
# The the client receives the response (a variety of useful data including location, nearest gas station, nearby
# vehicles, all vehicles, distance traveled, direction traveling, and weather data) from the server, and then
# closes the connection. Handles some input validation.
# 8/2/2021
# By; Greg Wolter
#!/usr/bin/python3

# Socket client example in python

import socket	#for sockets
import sys	    #for exit

# create an INET(IPv4), STREAMing(TCP) socket
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
	print ('Failed to create socket')
	sys.exit()
	
print ('Socket Created')

host = '127.0.0.1';   # the IP address of the server to connect
port = 3660;            # the port number of the application

# Connect to remote server
s.connect((host , port))

print ('Socket Connected to IP' + host)

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

# Send some data to remote server
starting_point = input("Enter Vehicle Starting Location (x and y coordinate) -> ")
# Creates a list where index 0 is x coordinate, and index 1 is y coordinate.
coordinates = starting_point.split()
# Checks for appropriate number of inputs, but does not handle non-number input errors (server handles that).
while len(coordinates) != 2:
	print("You did not enter the correct amount of coordinates.")
	starting_point = input("Enter Vehicle Starting Location (x and y coordinate) -> ")
	coordinates = starting_point.split()
# Asks for more data from user
speed_message = input("Enter Speed of Vehicle (mph) -> ")
# Handles input validation for speed
while not is_positive_number(speed_message):
	print("You did not enter a valid speed.\n")
	speed_message = input("Enter Speed of Vehicle (mph) -> ")

time_message = input("Enter Time Spent Driving from Starting Location (hours) -> ")
# Handles input validation for time
while not is_positive_number(time_message):
	print("You did not enter a valid time.\n")
	time_message = input("Enter Time Spent Driving from Starting Location (hours) -> ")

# If the user types in an invalid input for direction, the server will send an error message.
direction_message = input("Enter Direction of Vehicle (N, E, S, W) -> ")

# The vehicle tuple is made to allow the svr.py to do input validation on the direction.
vehicle = (speed_message, direction_message)

speed_change = "input"

speed_change_input = input("If you are changing your speed enter the new speed (any input that is not a"\
						   " positive number will be considered no change) -> ")
# input validation, if the user does not type a positive number, the input will not be sent to the server.
if is_positive_number(speed_change_input):
	speed_change = speed_change_input

# Combines all user inputs into one string to be sent to server.
message = coordinates[0] + " " + coordinates[1] + " " + vehicle[0] + " " + vehicle[1].upper() + " " + time_message + \
		  " " + speed_change

try:
	#encode the string before sending
	s.sendall(message.encode())
except socket.error:
	# Send failed
	print('Send failed')
	sys.exit()

# receive data from server
reply = s.recv(4096)  # the maximum size of the data is 4096
print('Received from server, here is your location: ' + reply.decode("utf-8"))

# close the socket to free the resources used by the socket
s.close()
