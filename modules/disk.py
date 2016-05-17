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
		color = self.convert(math.floor(0xFF * payload[1]/payload[0]))
		return [[0, "point { fill-color: "+color+"}", payload[0]],
		[1, "point { fill-color: "+color+";}", 100*payload[1]/payload[0]]]


	def get_format(self):
		return [[[0], "pointSize: 6, colors: ['black'], dataOpacity: 0.3,", ["Gb", "Disk Usage"]], [[1], "pointSize: 6, vAxis: { viewWindow: { min: 0, max: 100 } }, dataOpacity: 0.3,", ["%", "Disk Usage by Percentage"]]]

	def server_request(self, server_request = None):
		pass

	def trigger_called(self, trigger):
		pass

	def generate_request(self, machine_id):
		return None
