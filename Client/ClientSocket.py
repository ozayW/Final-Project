import socket
from flask import Flask, render_template, request, flash, redirect, url_for
import datetime
import pytz
import updates, users
import pickle
import hashlib
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


IP = "10.0.0.10"
IP_server = '10.0.0.10'
PORT = 63123

# Encrypt the data and send it through a socket connection to the server
def send_socket_data(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP_server, PORT))
    encrypted = encrypt(data)
    client_socket.send(encrypted.encode())
    return client_socket

# Determine if the user type matches the specified role
def user_type(username, role):
    data = 'user_type$' + username
    client_socket = send_socket_data(data)
    type = client_socket.recv(1024).decode()
    type = decrypt(type)
    type = type.split('$')[1]
    if role == type:
        return True
    return False

# Shift the ASCII value of a character by a given space and return the new character
def move_char(char, space):
    ascii_value = ord(char)
    new_ascii_value = ascii_value + space
    new_char = chr(new_ascii_value)
    return new_char

# Encrypt the data by shifting ASCII values in a specific pattern
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

# Decrypt the data by reversing the ASCII value shifts done during encryption
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

# Validate if the password is between 6 and 20 characters long, contains at least one digit and one letter, and is alphanumeric
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

# Check if the level is 'Master' or 'Ninja', indicating the ability to train
def can_train(level):
    print(level)
    if level == 'Master' or level == 'Ninja':
        return True
    return False

# Provide a time-based greeting based on the current hour in a given timezone
def time_based_greeting(tz):
    current_hour = datetime.datetime.now(pytz.timezone(tz)).hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# Adjust the index to fit within the range of 0 to 6 (days of the week)
def day_i(i):
    while i > 6:
        i -= 6
    return i

# Calculate the timeslot index based on a 8-slot per day system
def timeslot_i(i):
    if i % 6 == 0:
        return int(i / 6)
    return (i // 6) + 1

app = Flask(__name__)

app.secret_key = os.urandom(32)
login_manager = LoginManager(app)

limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# Class to manage user login state
class UserLog(UserMixin):
    def __init__(self, id):
        self.id = id

# Function to load a user given the user_id
@login_manager.user_loader
def load_user(user_id):
    return UserLog(user_id)

# Route to open the home page and log out the user
@app.route("/", methods=["GET", "POST"])
def open_page():
    logout_user()
    return render_template("HomePage.html")

# Route to handle user login with rate limiting
@app.route("/Login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login_page():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        print(password)
        if valid_pass(password):
            hash_object = hashlib.sha256()
            hash_object.update(password.encode('utf-8'))
            password = hash_object.hexdigest()
            password = encrypt(password)
            print(password)
            data = "$".join(['login', username, password])
            client_socket = send_socket_data(data)
            server_response = client_socket.recv(1024).decode()
            server_response = decrypt(server_response)
            server_response = server_response.split('$')
            if server_response[0] != 'login':
                return render_template("Login.html")

            if len(server_response) == 3:
                role = server_response[2]
                user = UserLog(username)
                login_user(user)
                if role == 'Gym Manager':
                    return redirect(url_for("manager_mainpage", username=username))
                elif role == 'Trainer':
                    return redirect(url_for("trainer_mainpage", username=username))
                elif role == 'Trainee':
                    return redirect(url_for("trainee_mainpage", username=username))
                elif role == 'Trainer Request':
                    flash("Request wasn't approved yet")
                    return render_template("Login.html")

        flash("Wrong Username or Password")
        return render_template("Login.html")

    return render_template("Login.html")

# Route to render the level selection page
@app.route("/Level", methods=['GET', "POST"])
def level_page():
    return render_template("Level.html")

# Route to render the sign-up page
@app.route("/Signup", methods=["GET", "POST"])
def signup_page():
    return render_template("Signup.html")

# Route to handle trainer sign-up
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
                hash_object = hashlib.sha256()
                hash_object.update(password.encode('utf-8'))
                # Get the hexadecimal representation of the hash
                password = hash_object.hexdigest()
                password = encrypt(password)
                data = '$'.join(["signup_trainer", username, password, level])
                client_socket = send_socket_data(data)
                server_response = client_socket.recv(1024).decode()
                server_response = decrypt(server_response)
                server_response = server_response.split('$')

                if server_response[0] != 'signup_trainer':
                    pass

                if server_response[1] == 'User already exist':
                    flash("Username already in use")
                    return render_template("TrainerSignup.html")

                if server_response[1] == 'Request Sent':
                    flash("Request Sent")
                    return render_template("TrainerSignup.html")

            else:
                flash("Invalid Password")
                return render_template("TrainerSignup.html")

        flash("Some fields are missing")
        return render_template("TrainerSignup.html")
    return render_template("TrainerSignup.html")

# Route to handle trainee sign-up
@app.route("/Signup/Trainee", methods=["GET", "POST"])
def trainee_signup():
    if request.method == 'POST':
        username = request.form["Username"]
        password = request.form["Password"]
        level = request.form["Level"]
        if username and level != 'Choose Level' and password:
            if valid_pass(password):
                hash_object = hashlib.sha256()
                hash_object.update(password.encode('utf-8'))
                # Get the hexadecimal representation of the hash
                password = hash_object.hexdigest()
                password = encrypt(password)
                data = '$'.join(["signup_trainee", username, password, level])
                client_socket = send_socket_data(data)
                server_response = client_socket.recv(1024).decode()
                server_response = decrypt(server_response)
                server_response = server_response.split('$')

                if server_response[0] != 'signup_trainee':
                    pass

                if server_response[1] == 'User already exist':
                    flash("Username already in use")
                    return render_template("TraineeSignup.html")

                if server_response[1] == 'User Added':
                    flash("Trainee Added")
                    return render_template("TraineeSignup.html")

            else:
                flash("Invalid Password")
                return render_template("TraineeSignup.html")

        flash("Some fields are missing")
        return render_template("TraineeSignup.html")
    return render_template("TraineeSignup.html")


#Gym Manager#

# Route to display the gym manager's main page
@app.route("/GymManager/<username>", methods=["GET", "POST"])
@login_required
def manager_mainpage(username):
    if not user_type(username, 'Gym Manager'):
        return open_page()
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("GymManagerFlask.html", username=username)

# Route to handle trainer requests for the gym manager
@app.route("/GymManager/TrainersRequests/<username>", methods=["GET", "POST"])
@login_required
def trainer_requests(username):
    if not user_type(username, 'Gym Manager'):
        return open_page()
    if request.method == 'POST':
        trainer = request.form['trainer']
        if 'approve' in request.form:
            # Handle approve logic
            data = 'approve_request$' + trainer
            client_socket = send_socket_data(data)
            server_response = client_socket.recv(1024).decode()
            server_response = decrypt(server_response)
        elif 'deny' in request.form:
            data = 'deny_request$' + trainer
            client_socket = send_socket_data(data)
            server_response = client_socket.recv(1024).decode()

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    data = 'get_trainer_requests$' + username
    client_socket = send_socket_data(data)
    server_response = client_socket.recv(1024).decode()
    server_response = decrypt(server_response)
    server_response = server_response.split('$')
    if server_response[1:][0]:
        return render_template("TrainersRequests.html", username=username, requests=server_response[1:], not_pending=0)
    else:
        return render_template("TrainersRequests.html", username=username, requests=0, not_pending=1)

# Route to handle the gym's training schedule
@app.route("/GymManager/ManagerTrainingSchedule/<username>", methods=["GET", "POST"])
@login_required
def training_schedule(username):
    if not user_type(username, 'Gym Manager'):
        return open_page()
    data = 'get_training_week$' + username
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    training_week = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            training_week = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)

    if request.method == 'POST':
        clicked_button = request.form['button']
        button_number = int(clicked_button.replace('button', ''))
        training_week[button_number].cancel_workout()

    return render_template("ManagerTrainingSchedule.html", username=username, training_week=training_week)

# Route to update the default training schedule
@app.route("/GymManager/ManagerTrainingSchedule/DefaultTable/<username>", methods=["GET", "POST"])
@login_required
def update_table(username):
    if not user_type(username, 'Gym Manager'):
        return open_page()
    data = 'get_trainers$' + username
    client_socket = send_socket_data(data)
    trainers = client_socket.recv(1024).decode()
    trainers = decrypt(trainers)
    trainers = trainers.split('$')

    if request.method == 'POST':
        workouts = []
        for i in range(1, 49):
            try:
                trainer = trainers[int(request.form.get(f"Trainer{i}"))]
            except:
                trainer = None
            if trainer:
                level = request.form.get(f"Level{i}")
                trainee_amount = request.form.get(f"Trainees Amount{i}")
            else:
                level = None
                trainee_amount = None
            day = day_i(i)
            time_slot = timeslot_i(i)
            date = None
            trainees = []
            workout = str(date) + ":" + str(day) + ":" + str(time_slot) + ":" + str(trainer) + ":" + \
                      str(level) + ":" + str(trainees) + ":" + str(trainee_amount)
            workouts.append(workout)

        data = 'set_default_week$' + username + '$' + str(workouts)
        client_socket = send_socket_data(data)
        server_response = client_socket.recv(1024).decode()
        server_response = decrypt(server_response)
        server_response = server_response.split('$')

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("DefaultSchedule.html", username=username, trainers=trainers[1::])

# Route to handle viewing and managing user data by the gym manager
@app.route("/GymManager/UsersData/<username>", methods=["GET", "POST"])
@login_required
def users_data(username):
    if not user_type(username, 'Gym Manager'):
        return open_page()
    data = 'get_trainers$' + username
    client_socket = send_socket_data(data)
    trainers_names = client_socket.recv(1024).decode()
    trainers_names = decrypt(trainers_names)
    trainers_names = trainers_names.split('$')[1:]
    trainers = []
    for name in trainers_names:
        data = 'get_level$' + name
        client_socket = send_socket_data(data)
        level = client_socket.recv(1024).decode()
        level = decrypt(level)
        level = level.split('$')[1]
        trainer = users.User(name, level, 'Trainer')
        trainers.append(trainer)

    data = 'get_trainees$' + username
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    trainees = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            trainees = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    if request.method == 'POST':
        clicked_button = request.form['button']
        user = clicked_button.replace('button', '')
        is_trainee = False
        for trainee in trainees:
            if trainee.username == user:
                is_trainee = True
                break
        if is_trainee:
            return user_data(username, user)

        data = 'delete_trainer$' + username + '$' + user
        client_socket = send_socket_data(data)
        server_response = client_socket.recv(1024).decode()
        server_response = decrypt(server_response)

        data = 'get_trainers$' + username
        client_socket = send_socket_data(data)
        trainers_names = client_socket.recv(1024).decode()
        trainers_names = decrypt(trainers_names)
        trainers_names = trainers_names.split('$')[1:]
        trainers = []
        for name in trainers_names:
            data = 'get_level$' + name
            client_socket = send_socket_data(data)
            level = client_socket.recv(1024).decode()
            level = decrypt(level)
            level = level.split('$')[1]
            trainer = users.User(name, level, 'Trainer')
            trainers.append(trainer)

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)

    return render_template("UsersData.html", username=username, trainers=trainers, trainees=trainees)

# Route to view data of a specific user (trainee)
@app.route("/GymManager/UsersData/User/<username>", methods=["GET", "POST"])
@login_required
def user_data(username, user):
    if not user_type(username, 'Gym Manager'):
        return open_page()
    data = 'get_trainee_updates$' + user
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    trainee_updates = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            trainee_updates = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    data = 'get_level$' + user
    client_socket = send_socket_data(data)
    level = client_socket.recv(1024).decode()
    level = decrypt(level)
    level = level.split('$')[1]
    flash(level)

    return render_template('UserData.html', username=username, trainee_updates=trainee_updates, user=user)

#Trainee#

# Route to display the trainee's main page
@app.route("/Trainee/<username>", methods=["GET", "POST"])
@login_required
def trainee_mainpage(username):
    if not user_type(username, 'Trainee'):
        return open_page()
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("TraineeFlask.html", username=username)

# Route to display and manage the trainee's training schedule
@app.route("/Trainee/TraineeTrainingSchedule/<username>", methods=["GET", "POST"])
@login_required
def trainee_training_schedule(username):
    if not user_type(username, 'Trainee'):
        return open_page()
    data = 'get_training_week$' + username
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    training_week = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            training_week = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    data = 'get_level$'+username
    client_socket = send_socket_data(data)
    level = client_socket.recv(1024).decode()
    level = decrypt(level)
    level = level.split('$')[1]
    flash(level)

    if request.method == 'POST':
        clicked_button = request.form['button']
        button_number = int(clicked_button.replace('button', ''))
        training_week[button_number].add_trainee(username)

    return render_template("TraineeTrainingSchedule.html", username=username, training_week=training_week)

# Route to display the trainee's workout data
@app.route("/Trainee/TraineeWorkoutsData/<username>", methods=["GET", "POST"])
@login_required
def trainee_workouts_data(username):
    if not user_type(username, 'Trainee'):
        return open_page()

    data = 'get_trainee_updates$' + username
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    trainee_updates = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            trainee_updates = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    data = 'get_level$'+username
    client_socket = send_socket_data(data)
    level = client_socket.recv(1024).decode()
    level = decrypt(level)
    level = level.split('$')[1]
    flash(level)

    return render_template("TraineeWorkoutsData.html", username=username, trainee_updates=trainee_updates)

# Route to add a new update for the trainee's workouts
@app.route("/Trainee/TraineeWorkoutsData/AddUpdate/<username>", methods=["GET", "POST"])
@login_required
def add_update(username):
    if not user_type(username, 'Trainee'):
        return open_page()
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%B %d, %Y")
    if request.method == 'POST':
        trainee = username
        pullups = request.form['inputPullUps']
        one_arm_pullups = request.form['inputOneArmPullUps']
        deadhang = request.form['inputDeadhang']
        spinning_bar_deadhang = request.form['inputSpinningBarDeadhang']
        lashe = request.form['inputLashe']
        if (pullups.isalnum() and one_arm_pullups.isalnum() and deadhang.isalnum() and
            spinning_bar_deadhang.isalnum() and lashe.isalnum()):
            update = updates.Update(trainee, formatted_date, int(pullups), int(one_arm_pullups),
                                    int(deadhang), int(spinning_bar_deadhang), int(lashe))
            level = update.add_update()
            data = 'update_level$' + username + '$' + level
            client_socket = send_socket_data(data)
            server_response = client_socket.recv(1024).decode()
            server_response = decrypt(server_response)
            server_response = server_response.split('$')
            flash('Updated')
        else:
            flash('Wrong Data')
    return render_template("AddUpdate.html", username=username, date=formatted_date)

#Trainer#
# Route to display the trainer's main page
@app.route("/Trainer/<username>", methods=["GET", "POST"])
@login_required
def trainer_mainpage(username):
    if not user_type(username, 'Trainer'):
        return open_page()
    time = time_based_greeting('Israel')
    flash(time + ' ' + username)
    return render_template("TrainerFlask.html", username=username)

# Route to display and manage the trainer's training schedule
@app.route("/Trainer/TrainerTrainingSchedule/<username>", methods=["GET", "POST"])
@login_required
def trainer_training_schedule(username):
    if not user_type(username, 'Trainer'):
        return open_page()
    data = 'get_training_week$' + username
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    training_week = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            training_week = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    if request.method == 'POST':
        clicked_button = request.form['button']
        button_number = int(clicked_button.replace('button', ''))
        training_week[button_number].cancel_workout()

    return render_template("TrainerTrainingSchedule.html", username=username, training_week=training_week)

# Route to display the trainer's trainees' workout data
@app.route("/Trainer/TrainerWorkoutsData/<username>", methods=["GET", "POST"])
@login_required
def trainees_workouts_data(username):
    if not user_type(username, 'Trainer'):
        return open_page()
    data = 'get_trainees$' + username
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    trainees = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            trainees = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    if request.method == 'POST':
        clicked_button = request.form['button']
        user = clicked_button.replace('button', '')
        return trainee_workout_data(username, user)

    time = time_based_greeting('Israel')
    flash(time + ' ' + username)

    return render_template("TraineesData.html", username=username, trainees=trainees)

# Route to display a specific trainee's workout data
@app.route("/Trainer/TrainerWorkoutsData/<username>/<user>", methods=["GET", "POST"])
@login_required
def trainee_workout_data(username, user):
    if not user_type(username, 'Trainer'):
        return open_page()
    data = 'get_trainee_updates$' + user
    client_socket = send_socket_data(data)

    data_received = b''
    while True:
        chunk = client_socket.recv(8192)
        if chunk == b"done":
            break
        data_received += chunk

    trainee_updates = []
    if data_received:
        try:
            st_length = len('abc')
            if data_received[-st_length:] == b'abc':
                data_without_st = data_received[:-st_length]
            else:
                raise ValueError("Received data does not have the expected suffix 'abc'")

            original_data_bytes = data_without_st[::-1]

            trainee_updates = pickle.loads(original_data_bytes)

        except (pickle.UnpicklingError, ValueError) as e:
            print("Error unpickling data or unexpected data format:", e)
    else:
        pass

    data = 'get_level$' + user
    client_socket = send_socket_data(data)
    level = client_socket.recv(1024).decode()
    level = decrypt(level)
    level = level.split('$')[1]
    flash(level)

    return render_template("TraineeData.html", username=username, trainee_updates=trainee_updates, user=user)


if __name__ == '__main__':
    app.run(port=80, debug=True, host=IP)