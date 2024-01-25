from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ozay:OZAY@cluster0.qjdp42h.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

#**Updates Database**#
def add_workout_update(username, date, pullups, one_arm_pullups, deadhang, spinning_bar_deadhang, lashe):
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        if not workout_update_exists(username, date):
            updates.insert_one({'Username': username, 'Date': date, 'Pull-Ups': pullups,
                                'One Arm Pull-Ups': one_arm_pullups, 'Deadhang': deadhang,
                                'Spinning Bar Deadhang': spinning_bar_deadhang, 'Lashe': lashe})
            return True
        return False
def get_from_workout_update(username, date, field):
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        update = updates.find_one({'Username': username, 'Date':date})
        return update.get(field)

def workout_update_exists(username, date):
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        if updates.find_one({'Username': username, 'Date': date}):
            return True
        return False



#**Workouts Database**#

def add_workout(date, timeslot, trainer, level, trainees, max_num_of_trainees, pending):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if not workout_exists(date, timeslot):
            workouts.insert_one({'Date': date, 'Time-slot':timeslot, 'Trainer':trainer, 'Level':level, 'Trainees':trainees,
                             'Max Number Of Trainees': max_num_of_trainees, 'pending': pending})
            return True
        return False

def add_trainee(date, timeslot, username):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if workout_exists(date, timeslot):
            max_num_of_trainees = get_from_workout(date, timeslot, 'Max Number Of Trainees')
            trainees = get_from_workout(date, timeslot, 'Trainees')
            trainees.append(username)
            if len(trainees) < max_num_of_trainees:
                workouts.update_one({'Date': date, 'Time-slot': timeslot}, {'$set': {'Trainees': trainees}})
                return True
        return False
def get_from_workout(date, timeslot, field):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        workout = workouts.find_one({'Date':date, 'Time-Slot':timeslot})
        return workout.get(field)

def workout_exists(date, timeslot):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if workouts.find_one({'Time-Slot': timeslot, 'Date': date}):
            return True
        return False



#***Users Database**#
def add_user(username,role, password, level, max_workouts):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if not users.exists(username):
            users.insert_one({'Username':username, 'Password':password, 'Role':role,
                                'Level':level, 'MaxWorkouts':max_workouts})
            return True
        return False

def upadte_user(username, field, new_data):
    try:
        with MongoClient(uri) as cluster:
            users = cluster['GYM']['Users']
            users.update_one({'Username':username}, {'$set': {field, new_data}})
            user = users.find_one({'Username':username})
            if user[field] == new_data:
                return True
            return False
    except:
        return False

def get_from_user(username, field):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        user = users.find_one({'Username':username})
        return user.get(field)

def user_exists(username):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if users.find_one({'Username': username}):
            return True
        return False

def user_login(username, password):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if users.find_one({'Username': username, 'Password': password}):
            user = users.find_one({'Username': username, 'Password': password})
            return user.get('Role')
        return 'false'