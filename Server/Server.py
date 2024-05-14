import socket
import threading
import DBHandle
import workouts
import pickle
import updates
import users

IP = "10.0.0.10"
SERVER_PORT = 63123

def move_char(char, space):
    # Get the ASCII value of the character
    ascii_value = ord(char)
    # Move one space back
    new_ascii_value = ascii_value + space
    # Get the new character
    new_char = chr(new_ascii_value)
    return new_char

def decrypt(data):
    i = 1
    encryption = ''
    for d in data:
        if (i - 1) % 3 == 0:
            new_char = move_char(d, 1)
        elif (i - 2) % 3 == 0:
            new_char = move_char(d, -2)
        else:
            new_char = move_char(d, 3)
        encryption += new_char
        i += 1
    return encryption

def encrypt(data):
    i = 1
    encryption = ''
    for d in data:
        if (i - 1) % 3 == 0:
            new_char = move_char(d, -1)
        elif (i - 2) % 3 == 0:
            new_char = move_char(d, 2)
        else:
            new_char = move_char(d, -3)
        encryption += new_char
        i += 1
    return encryption


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

def get_level(data):
    username = data[0]
    level = DBHandle.get_from_user(username, 'Level')
    return str(level)
def signup_trainee(data):
    username = data[0]
    password = data[1]
    level = data[2]
    if DBHandle.user_exists(username):
        return 'User already exist'
    DBHandle.add_trainee(username, password, level)
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
    DBHandle.update_user(data[0], 'Role', 'Trainer')
    return 'Approved'

def get_training_week(data):
    admin = DBHandle.get_users('Gym Manager')[0]
    username = data[0]
    current_week = DBHandle.get_workouts_in_week()
    current_workouts = []
    for current in current_week:
        if False:
            DBHandle.delete_workout(current)
        else:
            date = current['Date']
            day = current['Day']
            timeslot = current['Time-Slot']
            trainer = current['Trainer']
            level = current['Level']
            trainees = current['Trainees']
            max_trinees = current['Max Number Of Trainees']
            pending = current['Pending']
            in_current = current['Current Week']
            default = current['Default']
            workout = workouts.Workout(date, day, timeslot, trainer, level, trainees, max_trinees, pending, in_current, default)
            current_workouts.append(workout)

    updated_workouts = []
    if admin != username:
        return current_workouts

    if current_workouts:
        for workout in current_workouts:
            workout.update_data_base_current()
            workout.update_data_base_pending()

            if workout.get_in_current():
                updated_workouts.append(workout)

    if updated_workouts:
        return updated_workouts

    else:
        current_week = workouts.create_week_schedule()
        return current_week

def set_default_week(data):
    admin = DBHandle.get_users('Gym Manager')[0]
    if data[0] != admin:
        return 'Access Denied'
    default_schedule = data[1::]
    default_schedule = default_schedule[0]
    default_schedule = default_schedule.split(',')
    workouts_arr = []
    for default in default_schedule:
        temp = default
        temp = temp.split(':')
        if temp[3] != 'None' and temp[4] != 'None' and temp[6][:-1] != 'None':
            workout = workouts.Workout(temp[0][2::], int(temp[1]), int(temp[2]), temp[3], temp[4], [], int(temp[6][:-1]))
        else:
            workout = workouts.Workout('None', int(temp[1]), int(temp[2]), 'None', 'None', [], 0)
        workouts_arr.append(workout)
    print(workouts_arr)
    workouts.set_default_schedule(workouts_arr)
    current_week = DBHandle.get_workouts_in_week()
    for current in current_week:
        while True:
            try:
                DBHandle.delete_workout(current)
                break
            except:
                pass
    return 'success'
def get_trainers(data):
    admin = DBHandle.get_users('Gym Manager')[0]
    if data[0] != admin:
        return 'Access Denied'
    trainers = DBHandle.get_users('Trainer')
    trainers = "$".join(trainers)
    return trainers
def get_trainees(data):
    trainees = DBHandle.get_users('Trainee')
    trainees_users = []
    for trainee in trainees:
        level = DBHandle.get_from_user(trainee, 'Level')
        user = users.User(trainee, level, 'Trainee')
        trainees_users.append(user)
    return trainees_users


def get_trainee_updates(data):
    trainee_updates_db = DBHandle.get_trainee_updates(data[0])
    trainee_updates = []
    for trainee_update in trainee_updates_db:
        trainee = trainee_update['Username']
        date = trainee_update['Date']
        pullups = trainee_update['Pull-Ups']
        one_arm_pullups = trainee_update['One Arm Pull-Ups']
        deadhang = trainee_update['Deadhang']
        spinning_bar_deadhang = trainee_update['Spinning Bar Deadhang']
        lashe = trainee_update['Lashe']
        update = updates.Update(trainee, date, pullups, one_arm_pullups, deadhang, spinning_bar_deadhang, lashe)
        trainee_updates.append(update)

    return trainee_updates

def update_level(data):
    DBHandle.update_user(data[0], 'Level', data[1])
    return 'updated'

def delete_trainer(data):
    admin = DBHandle.get_users('Gym Manager')[0]
    if data[0] != admin:
        return 'Access Denied'
    DBHandle.delete_user(data[1])
    return 'Success'

#Dictionary of actions that can be used by the data sent
def act(action, data, client_object):
    actions = {'login': login, 'signup_trainee': signup_trainee, 'signup_trainer': signup_trainer,
               'get_trainer_requests': get_trainer_requests, 'deny_request': deny_request,
               'approve_request': approve_request, 'get_training_week': get_training_week, 'get_trainers': get_trainers,
               'set_default_week': set_default_week, 'get_level': get_level, 'get_trainee_updates': get_trainee_updates,
               'update_level': update_level, 'get_trainees': get_trainees, 'delete_trainer': delete_trainer}

    output = actions[action](data)
    if type(output) == str:
        send = "$".join([action, output])
        send = encrypt(send)
        print(send)
        client_object.send(send.encode())
    else:
        data = pickle.dumps(output)[::-1]
        st = 'abc'.encode()
        data = data+st
        client_object.send(data)
        client_object.send(b"done")


def main():
    server_socket = init_server()
    while True:
        client_object, client_IP = server_socket.accept()
        data = client_object.recv(2048).decode()
        data = decrypt(data)
        data = data.split('$')
        action = data[0]
        send = data[1:]
        client_th = threading.Thread(target=act, args=(action, send, client_object))
        client_th.start()



if __name__ == "__main__":
   # Workouts = workouts.get_default_schedule()
    #for workout in Workouts:
    #    print(str(workout))
    main()