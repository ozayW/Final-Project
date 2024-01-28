import socket
from flask import Flask, render_template, request, flash
import os
import datetime
import pytz


IP = "10.0.0.28"
PORT = 6090
def send_socket_data(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.send(data.encode())
    return client_socket

def valid_pass(password):
    if len(password) < 6 or len(password) > 20:
        return False

    for char in password:
        if not char.isalnum():
            return False
    return True
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

def manager_mainpage():
  pass

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
                return render_template("TraineeFlask.html")
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
        workout_amount = request.form["Workouts"]
        level = request.form["Level"]
        if username and workout_amount.isdigit() and level != 'Choose Level' and password:
            if valid_pass(password):
                data = '$'.join(["signup_trainee",username, password, level, workout_amount])
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
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    data = 'get_trainer_requests$' + username
    client_socket = send_socket_data(data)
    server_response = client_socket.recv(1024).decode()
    server_response = server_response.split('$')
    print(server_response[1:])
    return render_template("TrainersRequests.html", username=username, requests=server_response[1:])

@app.route("/GymManager/TrainingSchedule/<username>", methods=["GET", "POST"])
def training_schedule(username):
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("TrainingSchedule.html", username=username)

@app.route("/GymManager/UsersData/<username>", methods=["GET", "POST"])
def users_data(username):
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("UsersData.html", username=username)

if __name__ == '__main__':
    app.run(port=80, debug=True, host=IP)