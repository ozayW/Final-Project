import socket
from flask import Flask, render_template, request


IP = "10.0.0.28"
PORT = 6090
def send_socket_data(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.send(data.encode())
    return client_socket

app = Flask(__name__)
@app.route("/", methods = ["GET", "POST"])
def login_page():

    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        data = ":".join(['login', username, password])
        client_socket = send_socket_data(data)
        server_response = client_socket.recv(1024).decode()
        server_response = server_response.split(':')
        if server_response[0] != 'login':
            return render_template("LoginClient.html")

        if len(server_response) == 3:
            role = server_response[2]
            if role == 'Gym Manager':
                return render_template("GymManagerFlask.html")
            if role == 'Trainer':
                pass
            if role == 'Trainee':
                pass

        return render_template("LoginClient.html")

    return render_template("LoginClient.html")


if __name__ == '__main__':
    app.run(port=80, debug=True, host=IP)


#Gym Manager#

@app.route("/GymManager", methods = ["GET", "POST"])
def manager_mainpage():
    return render_template("GymManagerFlask.html")