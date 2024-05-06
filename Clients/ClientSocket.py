import socket
from flask import Flask, render_template, request, flash
import os
import datetime
import pytz
import workouts
import pickle

IP = "10.0.0.10"
IP_server = '10.0.0.10'
PORT = 6090
def send_socket_data(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP_server, PORT))
    client_socket.send(data.encode())
    return client_socket

def valid_pass(password):
    if len(password) < 6 or len(password) > 20:
        return False
    digit = False
    letter = False
    for char in password:
        if not char.isalnum():
            return False
        if char.isalpha():
            letter = True
        if char.isdigit():
            digit = True
    if digit and letter:
        return True
    return False

def can_train(level):
    print(level)
    if level == 'Master' or level == 'Ninja':
        return True
    return False

def time_based_greeting(tz):
    current_hour = datetime.datetime.now(pytz.timezone(tz)).hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def day_i(i):
    while i > 6:
        i -= 6
    return i

def timeslot_i(i):
    if i % 6 == 0:
        return int(i / 6)

    return (i // 6) + 1


app = Flask(__name__)

app.secret_key = os.urandom(32)

@app.route("/", methods = ["Get", "Post"])
def open_page():
    return render_template("HomePage.html")

@app.route("/Login", methods = ["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        data = "$".join(['login', username, password])
        client_socket = send_socket_data(data)
        server_response = client_socket.recv(1024).decode()
        server_response = server_response.split('$')
        if server_response[0] != 'login':
            return render_template("Login.html")

        if len(server_response) == 3:
            role = server_response[2]
            if role == 'Gym Manager':
                return manager_mainpage(username)
            if role == 'Trainer':
                return render_template("TrainerFlask.html")
            if role == 'Trainee':
                return trainee_mainpage(username)
            if role == 'Trainer Request':
                flash("Request wasn't approved yet")
                return render_template("Login.html")

        flash("Wrong Username or Password")
        return render_template("Login.html")

    return render_template("Login.html")

@app.route("/Level", methods=['GET', "POST"])
def level_page():
    return render_template("Level.html")

#*sign ups*#
@app.route("/Signup", methods=["GET", "POST"])
def signup_page():
    return render_template("Signup.html")

@app.route("/Signup/Trainer", methods=["GET", "POST"])
def trainer_signup():
    if request.method == 'POST':
        username = request.form["Username"]
        password = request.form["Password"]
        level = request.form["Level"]
        if username and level != 'Choose Level' and password:
            if not can_train(level):
                flash("Not qualified to train")
                return render_template("TrainerSignup.html")

            if valid_pass(password):
                data = '$'.join(["signup_trainer", username, password, level])
                client_socket = send_socket_data(data)
                server_response = client_socket.recv(1024).decode()
                server_response = server_response.split('$')

                if server_response[0] != 'signup_trainer':
                    pass

                if server_response[1] == 'User already exist':
                    flash("Username already in use")
                    render_template("TrainerSignup.html")

                if server_response[1] == 'Request Sent':
                    flash("Request Sent")
                    render_template("TrainerSignup.html")

            else:
                flash("Invalid Password")
                return render_template("TrainerSignup.html")

        flash("Some fields are missing")
        return render_template("TrainerSignup.html")
    return render_template("TrainerSignup.html")

@app.route("/Signup/Trainee", methods=["GET", "POST"])
def trainee_signup():
    if request.method == 'POST':
        username = request.form["Username"]
        password = request.form["Password"]
        level = request.form["Level"]
        if username and level != 'Choose Level' and password:
            if valid_pass(password):
                data = '$'.join(["signup_trainee", username, password, level])
                client_socket = send_socket_data(data)
                server_response = client_socket.recv(1024).decode()
                server_response = server_response.split('$')

                if server_response[0] != 'signup_trainee':
                    pass

                if server_response[1] == 'User already exist':
                    flash("Username already in use")
                    render_template("TraineeSignup.html")

                if server_response[1] == 'User Added':
                    flash("Trainee Added")
                    render_template("TraineeSignup.html")

            else:
                flash("Invalid Password")
                return render_template("TraineeSignup.html")

        flash("Some fields are missing")
        return render_template("TraineeSignup.html")
    return render_template("TraineeSignup.html")

#Gym Manager#

@app.route("/GymManager/<username>", methods=["GET", "POST"])
def manager_mainpage(username):
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("GymManagerFlask.html", username=username)

@app.route("/GymManager/TrainersRequests/<username>", methods=["GET", "POST"])
def trainer_requests(username):
    print(request.method)
    if request.method == 'POST':
        print("post")
        trainer = request.form['trainer']
        if 'approve' in request.form:
            # Handle approve logic
            data = 'approve_request$' + trainer
            client_socket = send_socket_data(data)
            server_response = client_socket.recv(1024).decode()
            print(server_response)

        elif 'deny' in request.form:
            # Handle deny logic
            data = 'deny_request$' + trainer
            client_socket = send_socket_data(data)
            server_response = client_socket.recv(1024).decode()
            print(server_response)

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    data = 'get_trainer_requests$' + username
    client_socket = send_socket_data(data)
    server_response = client_socket.recv(1024).decode()
    server_response = server_response.split('$')
    if server_response[1:][0]:
        return render_template("TrainersRequests.html", username=username, requests=server_response[1:], not_pending=0)
    else:
        return render_template("TrainersRequests.html", username=username, requests=0, not_pending=1)
@app.route("/GymManager/ManagerTrainingSchedule/<username>", methods=["GET", "POST"])
def training_schedule(username):

    data = 'get_training_week$' + username
    client_socket = send_socket_data(data)


    # Assuming client_socket is your socket object
    data_received = b''
    while True:
        chunk = client_socket.recv(4096)  # Receive larger chunks of data
        if chunk == b"done":
            break  # If no more data is received, break the loop
        data_received += chunk
    training_week = []
    if data_received:
        try:
            training_week = pickle.loads(data_received)
            # Use training_week as needed
        except pickle.UnpicklingError as e:
            print("Error unpickling data:", e)
    else:
        print("No data received.")
    i = 1
    for t in training_week:
        print(t)
        i+=1
    print(i)

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("ManagerTrainingSchedule.html", username=username, training_week=training_week)

@app.route("/GymManager/UsersData/<username>", methods=["GET", "POST"])
def users_data(username):
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("UsersData.html", username=username)

@app.route("/GymManager/ManagerTrainingSchedule/DefaultTable/<username>", methods=["GET", "POST"])
def update_table(username):

    data = 'get_trainers$' + username
    client_socket = send_socket_data(data)
    trainers = client_socket.recv(1024).decode()
    trainers = trainers.split('$')

    if request.method == 'POST':
        workouts = []
        for i in range(1, 49):
            print(i)
            try:
                trainer = trainers[int(request.form.get(f"Trainer{i}"))]
            except:
                trainer = None
            print(trainer)
            if trainer:
                level = request.form.get(f"Level{i}")
                trainee_amount = request.form.get(f"Trainees Amount{i}")
            else:
                level = None
                trainee_amount = None
            print(level)
            day = day_i(i)
            time_slot = timeslot_i(i)
            date = None
            trainees = []
            workout = str(date) + ":" + str(day) + ":" + str(time_slot) + ":" + str(trainer) + ":" + \
                      str(level) + ":" + str(trainees) + ":" + str(trainee_amount)
            workouts.append(workout)

        print(str(workouts))
        data = 'set_default_week$' + username + '$' + str(workouts)
        print(data)
        client_socket = send_socket_data(data)
        server_response = client_socket.recv(1024).decode()
        server_response = server_response.split('$')

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("DefaultSchedule.html", username=username, trainers=trainers[1::])

#Trainee#

@app.route("/Trainee/<username>", methods=["GET", "POST"])
def trainee_mainpage(username):
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("TraineeFlask.html", username=username)

@app.route("/Trainee/TraineeTrainingSchedule/<username>", methods=["GET", "POST"])
def trainee_training_schedule(username):

    if request.method == 'POST':
        clicked_button = request.form['button']
        button_number = int(clicked_button.replace('button', ''))
        print(button_number)
    data = 'get_training_week$' + username
    client_socket = send_socket_data(data)

    # Assuming client_socket is your socket object
    data_received = b''
    while True:
        chunk = client_socket.recv(4096)  # Receive larger chunks of data
        if chunk == b"done":
            break  # If no more data is received, break the loop
        data_received += chunk
    training_week = []
    if data_received:
        try:
            training_week = pickle.loads(data_received)
            # Use training_week as needed
        except pickle.UnpicklingError as e:
            print("Error unpickling data:", e)
    else:
        print("No data received.")

    data = 'get_level$'+username
    client_socket = send_socket_data(data)
    level = client_socket.recv(1024).decode()
    level = level.split('$')[1]
    flash(level)

    return render_template("TraineeTrainingSchedule.html", username=username, training_week=training_week)

@app.route("/Trainee/TraineeWorkoutsData/<username>", methods=["GET", "POST"])
def trainee_workouts_data(username):
    return render_template("TraineeWorkoutsData.html", username=username)

if __name__ == '__main__':
    app.run(port=80, debug=True, host=IP)