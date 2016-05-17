import random, sys, time, subprocess, math

from enum import Enum

class module():

	provides = "disk";

	version = "0.0.1";
	
	listeners = [];
	def convert(self, color):
		result = str(hex(color))[2:]
		while len(result) < 6:
			result = "0" + result
		return result

	def __init__(self, register, triggers):
		register(self, triggers.STARTUP);

	def format(self, payload):
		color = self.convert(math.floor(0xFF * payload[0]/payload[1]))
		return [[0, "point { fill-color: "+color+"}", payload[0]],
		[1, "point { fill-color: "+color+";}", 100*payload[0]/payload[1]]]


	def get_format(self):
		return [[[0], "pointSize: 6, colors: ['black']", ["Gb", "Disk Usage"]], [[1], "pointSize: 6, haxis: { viewWindow: { min: 0, max: 100 } }", ["%", "Disk Usage by Percentage"]]]

	def server_request(self, server_request = None):
		pass

	def trigger_called(self, trigger):
		pass

	def generate_request(self, machine_id):
		return None
