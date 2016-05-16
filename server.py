import logging, time, sys, glob, threading, queue, os, time, base64, atexit, json, pymysql
from enum import Enum

class Triggers():
	STARTUP = 0;
	SHUTDOWN = 1;
	USER = 2;
	CLIENT = 3;
class MessageType():
	PING = 0;
	PONG = 1;
	REQUEST = 2;
	RESPONSE = 3;
	TRIGGER_PUSH = 4;
from twisted.protocols import basic


def update_metadata(module, metadata):
	cur.execute("UPDATE `modules` SET `tables` = " + sql.escape(metadata[0]) + ", `smoothing` = " + sql.escape(metadata[1]) + ", `labels` = " + sql.escape(json.dumps(metadata[2])) + " WHERE `module` = " + sql.escape(module.provides) + ";")
def register(module, trigger, trigger_method = False, format = False):
	if not trigger_method:
		trigger_method = module.trigger_called;

	q = queue.Queue();
	h = threading.Thread(target = listener, args = (q, trigger, format, global_event_queue, module, trigger_method));

	listeners.append(h);
	listener_queues.append(q);
	
	h.start();

def event(module, trigger, payload = False):
	for q in listener_queues:
		if payload:
			q.put([module, trigger, payload[1], payload[0]]);
		else:
			q.put([module, trigger]);

def listener(q, trigger, format, p, module, trigger_done):
	print("Starting listener for module " + module.provides + " format: " + str(format) + " trigger: " + str(trigger))
	while True:
		temp = q.get();
		if temp[0] == module.provides:
			if trigger and temp[1] == trigger:
				p.put([module, False, trigger_done(temp[2])]);
			elif format and not temp[1]:
				p.put([module, True, module.format(temp[2]), temp[3]])
def global_queue_listener_function(p):
	while True:
		temp = p.get()
		if temp[1]:
			for f in temp[2]:
				log_data(temp[0], temp[3], *f)
		else:
			send_request(temp[0], temp[2])

def send_request(module, was_trigger, data, type=MessageType.REQUEST, connection = False): 
	message_object = {
		"module": module.provides,
		"version": module.version,
		"message_type": type,
		"payload": data,
		"auth_token": "",
		"timestamp": int(time.time())
	}
	if was_trigger:
		message_object["trigger"] = was_trigger
	data_to_write = json.dumps(message_object).encode("utf-8")
	if not connection:
		for client in factory.clients:
			client.sendLine(data_to_write);
	else:
		connection.sendLine(data_to_write)
	print("SEND: " + data_to_write.decode("utf-8"))

def handle(connection, line):
	if line["message_type"] == MessageType.PING:
		handle_ping(connection, line)
	elif line["message_type"] == MessageType.RESPONSE or line["message_type"] == MessageType.TRIGGER_PUSH:
		# the first element in the third argument is passed through, the module does not get to see or modify it. The second element in the third argument is passed to the module
		event(line["module"], False, [[connection, line["timestamp"]], line["payload"]])
def handle_ping(connection, line):
	message_object = {
		"message_type": MessageType.PONG,
		"payload": line["payload"],
		"auth_token": connection.auth_token,
		"timestamp": int(time.time())
	}
	# TODO
def log_data(module, passthrough_data, graph, color, data):
	connection, timestamp = passthrough_data
	cur.execute("INSERT INTO `logged_data` (module, module_graph, date, color, data, machine) VALUES (" + sql.escape(module.provides) + ", " + sql.escape(str(graph)) + ", "+sql.escape(str(timestamp))+", "+sql.escape(str(color))+", " + sql.escape(data) +", " + str(connection.machine_id) + ");")
	sql.commit()
machine_idx = 0
def query_thread(connection):
	while True:
		for module in modules:
			send_request(module, False, module.generate_request(connection.machine_id), connection = connection)
		time.sleep(10) # CHANGEME

class server(basic.LineOnlyReceiver):
	def connectionMade(self):
		global machine_idx
		self.factory.clients.append(self)
		self.auth_token = base64.b64encode(os.urandom(12)).decode("utf-8")
		self.machine_id = machine_idx
		machine_idx += 1
		self.thread = threading.Thread(target=query_thread,args=(self,))
		self.thread.start()

	def connectionLost(self, reason):
		self.factory.clients.remove(self)

	def lineReceived(self, line):
		print("RECV: " + line.decode("utf-8"))
		handle(self, json.loads(line.decode("utf-8")))


sql = pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", port=3306, user="manage", passwd="", db="manager")
cur = sql.cursor()


global_event_queue = queue.Queue();
listeners = []
listener_queues = []
sys.path.append("modules");
old_files = [f[len("modules") + 1:] for f in glob.glob("modules/*")];
files = []
for f in old_files:
	if f != "__pycache__":
		files.append(f[:-3]);

modules = [g.module(lambda a, b, c=False: register(a, b, c), Triggers) for g in map(__import__, files)];
# Start the thread that will redirect the results from querying the modules to the server
global_queue_listener = threading.Thread(target = global_queue_listener_function, args = (global_event_queue,));
global_queue_listener.start();

if len(modules) == 1:
	logging.info('Loaded 1 module.', );
else:
	logging.info('Loaded %s modules.', modules);

cur.execute("TRUNCATE `modules`;")
for module in modules:
	if module.provides is None:
		continue
	cur.execute("INSERT INTO `modules` (`module`, `tables`, `smoothing`) VALUES (" + sql.escape(module.provides) + ", 0, 0);")
	update_metadata(module, module.get_format())
	sql.commit()
	event(module, Triggers.STARTUP); # Send it the startup event
	register(module, False, False, True); # Sign it up for server requests in the event system
	atexit.register(event, module, Triggers.SHUTDOWN) # Send it the shutdown event on exit
	# Note that they will only receive the startup and shutdown events if they have specifically requested them in their constructor

	for thread in module.listeners: # Also start all of their listeners
		h = threading.Thread(target = thread, args = (module, lambda x, y: event(x,y,True),update_metadata)); # We used to give the listeners (module, thread) but then they would be able to send format events
		h.start();


from twisted.internet import protocol, reactor
from twisted.application import service, internet

factory = protocol.ServerFactory()
factory.protocol = server
factory.clients = []
reactor.listenTCP(5505,factory)
reactor.run()