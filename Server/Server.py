import socket
import threading

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6090
clients_objects = []

def init_server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP,SERVER_PORT))
    server_socket.listen()
    print(" waiting for clients")
    return server_socket


def act(action, client):
    pass

def main():
    server_socket = init_server()
    while True:
        client_object, client_IP = server_socket.accept()
        clients_objects.append(client_object)
        action = client_object.recv(1024).decode
        client_th = threading.Thread(target=act, args=('action',client_object))
        client_th.start()



if __name__ == "__main__":
    main()