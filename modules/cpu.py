import random, sys, time, subprocess

from enum import Enum

class module():

	provides = "cpu";

	version = "0.0.1";
	
	listeners = [];

	def __init__(self, register, triggers):
		register(self, triggers.STARTUP);

	def format(self, payload):
		return [[0, 0x000000, payload]]

	def get_format(self):
		return [1, False, [["%", "CPU Percentage"]]]

	def server_request(self, server_request = None):
		pass

	def trigger_called(self, trigger):
		pass

	def generate_request(self, machine_id):
		return None
