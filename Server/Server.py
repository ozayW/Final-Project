import socket
import threading
import DBHandle

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6090
clients_objects = []

def init_server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP,SERVER_PORT))
    server_socket.listen()
    print(" waiting for clients")
    return server_socket

def login(data):
    if DBHandle.user_login(data[0], data[1]):
        return 'login successful'
    if DBHandle.user_exists(data[0]):
        return 'wrong password'
    return "username doesn't exist"


def signup():
    pass

def act(action, data):
    actions = {'login': login, 'signup': signup}
    print(actions[action](data))

def main():
    server_socket = init_server()
    while True:
        client_object, client_IP = server_socket.accept()
        clients_objects.append(client_object)
        data = client_object.recv(1024).decode()
        data = data.split(':')
        action = data[0]
        send = data[1:]
        client_th = threading.Thread(target=act, args=(action, send))
        client_th.start()



if __name__ == "__main__":
    main()