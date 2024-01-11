from flask import Flask, render_template, request
import threading
import socket
import Server
import ClientSocket

app = Flask(__name__)

IP = "172.20.135.81"
@app.route("/", methods = ["GET", "POST"])
def login_page():

    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        data = ":".join(['login', username, password])

        ClientSocket.send_socket_data(data)

    return render_template("GymManagerFlask.html")


if __name__ == "__main__":
    app.run(port=80, debug=True,host=IP)