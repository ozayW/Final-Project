
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ozay:Oz_0586618917@cluster0.qjdp42h.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def update_amount(username):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if(not users.find_one({'Username' : username})):
            user = users.find_one({'Username':username})
            i = 1
            field = 'Workout Update ' + str(i)
            while  user.get(field) is not None:
                i+=1
                field = 'Workout Update ' + str(i)
            return i
        return 0
def add_user(username, password, level, max_workouts, workout_update, role='None'):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if(not users.find_one({'Username': username})):
            users.insert_one({'Username':username, 'Password':password, 'Role':role})
            return True
        return False

def upadte_user(username, field, new_data):
    try:
        with MongoClient(uri) as cluster:
            users = cluster['GYM']['Users']
            users.update_one({'Username':username}, {'$set':{field, new_data}})
            user = users.find_one({'Username':username})
            if(user[field] == new_data)
                return True
            return False
    except:
        return False

