import socket
def send_socket_data(data):
    IP = "127.0.0.1"
    PORT = 6090
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.send(data.encode())