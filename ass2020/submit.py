import socket
import json
"""
   Submits player object converted to a string to the competition server
"""

def send_to_server(js):
	"""Open socket and send the json string js to server with EOM appended, and wait
	   for \n terminated reply.
	   js - json object to send to server
	"""
	clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientsocket.connect(('128.250.106.25', 5002))

	clientsocket.send("""{}EOM""".format(js).encode('utf-8'))

	data = ''
	while data == '' or data[-1] != "\n":
		data += clientsocket.recv(1024).decode('utf-8')
	print(data)


	clientsocket.close()

def submit_class(name, filename, cmd = "ADD", syn = 7):
    f = open(filename)
    object_dict = {"cmd": cmd, "syn": syn, "name":name, "data":f.read()}
    f.close()
    return json.dumps(object_dict)

#from inspect import getsource
#my_code = getsource(Player)
submission = submit_class("BernieSanders", "./BernieSanders.py", cmd = "DEL", syn =13)

send_to_server(submission)

