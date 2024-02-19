import socket
import threading
import DBHandle
import workouts

IP = "172.20.133.250"
SERVER_PORT = 6090

def init_server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((IP, SERVER_PORT))
    server_socket.listen()
    print(" waiting for clients")
    return server_socket

def login(data):
    user_login = DBHandle.user_login(data[0], data[1])
    if user_login != 'false':
        return 'login successful$'+user_login

    return "username or password incorrect"


def signup_trainee(data):
    username = data[0]
    password = data[1]
    workouts = data[2]
    level = data[3]
    if DBHandle.user_exists(username):
        return 'User already exist'
    DBHandle.add_trainee(username, password, workouts, level)
    return 'User Added'

def signup_trainer(data):
    username = data[0]
    password = data[1]
    level = data[2]
    if DBHandle.user_exists(username):
        return 'User already exist'
    DBHandle.add_trainer(username, password, level)
    return 'Request Sent'

def get_trainer_requests(data):
    admin = DBHandle.get_users('Gym Manager')[0]
    if data[0] != admin:
        return 'Access Denied'
    trainers = DBHandle.get_users('Trainer Request')
    potential_trainers = []
    for trainer in trainers:
        trainer = trainer + ":" + DBHandle.get_from_user(trainer, 'Level')
        potential_trainers.append(trainer)
    potential_trainers = "$".join(potential_trainers)
    return potential_trainers

def deny_request(data):
    print(data[0])
    DBHandle.delete_user(data[0])
    return 'Dined'
def approve_request(data):
    print(data[0])
    DBHandle.upadte_user(data[0], 'Role', 'Trainer')
    return 'Approved'

def get_training_week(data):
    training_week = DBHandle.get

#Dictionary of actions that can be used by the data sent
def act(action, data, client_object):
    actions = {'login': login, 'signup_trainee': signup_trainee, 'signup_trainer': signup_trainer,
               'get_trainer_requests':get_trainer_requests, 'deny_request':deny_request,
               'approve_request':approve_request, 'get_training_week':get_training_week}

    output = actions[action](data)
    send = "$".join([action, output])
    print(send)
    client_object.send(send.encode())


def main():
    server_socket = init_server()
    while True:
        client_object, client_IP = server_socket.accept()
        data = client_object.recv(1024).decode()
        data = data.split('$')
        action = data[0]
        send = data[1:]
        client_th = threading.Thread(target=act, args=(action, send, client_object))
        client_th.start()



if __name__ == "__main__":
    main()