import random, sys, time, subprocess

from enum import Enum

class custom_triggers(Enum):
	OVERHEAT = 1024;

class module():

	provides = "temp";

	version = "0.0.1";
	
	def metadata_updater(self, event, update_metadata):
		while True:
			time.sleep(8);
			update_metadata(self,self.get_format())
			print(self.get_format())

	listeners = [metadata_updater];

	def __init__(self, register, triggers):
		register(self, triggers.STARTUP);
		self.graphs = 0

	def format(self, payload):
		color = 0x000000
		#if type(payload[0]) == type([]):
		#	color = 0xFF0000
		#	return [0, color, int(time.time()), payload[0]]
		self.graphs = max(len(payload), self.graphs)
		return [[x, color, payload[x]] for x in range(self.graphs)]

	def get_format(self):
		return [6, False, [["Degrees C", "Temperature"] for x in range(self.graphs)]]

	def server_request(self, server_request = None):
		pass

	def trigger_called(self, trigger):
		pass

	def generate_request(self, machine_id):
		return None