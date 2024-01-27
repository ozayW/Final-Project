import socket
import threading
import DBHandle

IP = "10.0.0.28"
SERVER_PORT = 6090

def init_server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((IP,SERVER_PORT))
    server_socket.listen()
    print(" waiting for clients")
    return server_socket

def login(data):
    user_login = DBHandle.user_login(data[0], data[1])
    if user_login != 'false':
        return 'login successful:'+user_login

    return "username or password incorrect"


def signup():
    pass

#Dictionary of actions that can be used by the data sent
def act(action, data, client_object):
    actions = {'login': login, 'signup': signup}

    output = actions[action](data)
    send = ":".join([action, output])
    print(send)
    client_object.send(send.encode())


def main():
    server_socket = init_server()
    while True:
        client_object, client_IP = server_socket.accept()
        data = client_object.recv(1024).decode()
        data = data.split(':')
        action = data[0]
        send = data[1:]
        client_th = threading.Thread(target=act, args=(action, send, client_object))
        client_th.start()



if __name__ == "__main__":
    main()