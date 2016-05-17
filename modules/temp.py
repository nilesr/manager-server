import random, sys, time, subprocess, json

from enum import Enum

class custom_triggers(Enum):
	OVERHEAT = 1024;

class module():

	provides = "temp";

	version = "0.0.1";
	def int_to_color(self, color):
		result = str(hex(color))[2:]
		while len(result) < 6:
			result = "0" + result
		return result
	def metadata_updater(self, event, update_metadata):
		while True:
			time.sleep(8);
			update_metadata(self,self.get_format())

	listeners = [metadata_updater];

	def __init__(self, register, triggers):
		register(self, triggers.STARTUP);
		self.graphs = 0

	def format(self, payload):
		self.graphs = max(len(payload), self.graphs)
		final = []
		for x in range(self.graphs):
			color = 0x000000
			if payload[x] > 56:
				color = 0xFF0000
			color = self.int_to_color(color)
			color = "point { size: 6; fill-color: #" + color + ";}"
			final.append([x, color, payload[x]])
		return final

	def get_format(self):
		#return [[[x], "pointsize: 6", ["degrees c", "temperature"]] for x in range(self.graphs)]
		#return [[[x for x in range(self.graphs)], "pointsize: 6", ["degrees c", "temperature"]]]
		return [[[0,1,2,3], "pointsize: 6, curveType:'function'", ["degrees c", "temperature"]],[[4,5], "pointsize: 6", ["degrees c", "temperature"]]]

	def server_request(self, server_request = None):
		pass

	def trigger_called(self, trigger):
		pass

	def generate_request(self, machine_id):
		return None