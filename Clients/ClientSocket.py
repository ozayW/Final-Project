import socket
from flask import Flask, render_template, request


IP = "10.0.0.28"
PORT = 6090
def send_socket_data(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.send(data.encode())
    return client_socket

def manager_mainpage():
  pass

app = Flask(__name__)

@app.route("/", methods = ["Get", "Post"])
def open_page():
    return render_template("HomePage.html")

@app.route("/Login", methods = ["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        data = ":".join(['login', username, password])
        client_socket = send_socket_data(data)
        server_response = client_socket.recv(1024).decode()
        server_response = server_response.split(':')
        if server_response[0] != 'login':
            return render_template("Login.html")

        if len(server_response) == 3:
            role = server_response[2]
            if role == 'Gym Manager':
                return manager_mainpage()
            if role == 'Trainer':
                return render_template("TrainerFlask.html")
            if role == 'Trainee':
                return render_template("TraineeFlask.html")

        return render_template("WrongLogin.html")

    return render_template("Login.html")

@app.route("/Signup", methods=["GET", "POST"])
def signup_page():
    return render_template("Signup.html")

@app.route("/Signup/Trainer", methods=["GET", "POST"])
def trainer_signup():
    return render_template("TrainerSignup.html")

@app.route("/Signup/Trainee", methods=["GET", "POST"])
def trainee_signup():
    if request.method == 'POST':
        print('HI')
    return render_template("TraineeSignup.html")

@app.route("/Signup/Trainee/Level", methods=['GET', "POST"])
def level_page():
    return render_template("Level.html")

#Gym Manager#

@app.route("/GymManager", methods=["GET", "POST"])
def manager_mainpage():
    return render_template("GymManagerFlask.html")


if __name__ == '__main__':
    app.run(port=80, debug=True, host=IP)