﻿import abc
import datetime
import requests
import RPi.GPIO as GPIO

class Sensor(object):
	
	def __init__(self, identity, pin, sensor_type):
		self.identity = identity
		self.__pin = pin
		self.__sensor_type = sensor_type
		self.__last_state = -1
		self.__state_changed_on = datetime.datetime(1979, 1, 1, 0, 0, 0, 0)
		GPIO.setup(self.__pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	
	# reads the current state of sensor and returns indication whether it changed
	def read_state(self):
		new_state = 1 if GPIO.input(self.__pin) == False else 0
		if self.__last_state != new_state:
			self.__last_state = new_state
			self.__state_changed_on = datetime.datetime.utcnow()
			print("{0} State changed for pin [{1}] from {2} to {3}".format(
				self.__state_changed_on.strftime("%H:%M:%S"), self.__pin, self.__last_state, new_state))
			return True
		else:
			return False

	# reads and sends the current state of sensor
	def send_state(self, client_token, end_point):
		success = False
		payload = {"token": client_token, "sensorType": self.__sensor_type, "sensorId": self.identity, "state": self.__last_state}		
		log_message = "{0} Sending {1}:\t".format(
			datetime.datetime.utcnow().strftime("%H:%M:%S"), str({"pin": self.__pin, "state": self.__last_state}))
		
		try:
			r = requests.post(end_point, json=payload, timeout=0.5) # timeout after 1 second
			log_message += "{0} {1}".format(r.status_code, r.text)
			r.close()
			success = (r.status_code == 200)
		except requests.exceptions.ConnectionError as e:
			log_message += "connection error/timeout waiting for response"
		except requests.exceptions.ConnectTimeout as e:
			log_message += "timeout while connecting"
		except requests.exceptions.ReadTimeout as e:
			log_message += "timeout while getting response"
		except requests.exceptions.HTTPError as e:
			log_message += "HTTP error - {0}".format(e.message)
		except requests.exceptions.RequestException as e:
			log_message += "General error - {0}".format(e.message)
		
		print(log_message)
		return success