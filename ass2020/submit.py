from BasePlayer import BasePlayer
import socket


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

submission = {
	"cmd": "ADD",
	"syn": "13",
	"name": "test_13",
	"data": str(BasePlayer())
} 


send_to_server(submission)