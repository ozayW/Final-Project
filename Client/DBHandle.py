from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ozay:OZAY@cluster0.qjdp42h.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

#**Updates Database**#
# Adds a workout update for a trainee to the database
def add_workout_update(username, date, pullups, one_arm_pullups, deadhang, spinning_bar_deadhang, lashe):
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        if not workout_update_exists(username, date):
            updates.insert_one({'Username': username, 'Date': date, 'Pull-Ups': pullups,
                                'One Arm Pull-Ups': one_arm_pullups, 'Deadhang': deadhang,
                                'Spinning Bar Deadhang': spinning_bar_deadhang, 'Lashe': lashe})
            return True
        return False

# Retrieves a specific field from a workout update for a trainee
def get_from_workout_update(username, date, field):
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        update = updates.find_one({'Username': username, 'Date':date})
        return update.get(field)

# Checks if a workout update for a trainee exists in the database
def workout_update_exists(username, date):
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        if updates.find_one({'Username': username, 'Date': date}):
            return True
        return False

# Retrieves all workout updates for a trainee from the database
def get_trainee_updates(username):
    trainee_updates = []
    with MongoClient(uri) as cluster:
        updates = cluster['GYM']['Updates']
        for update in updates.find({'Username': username}):
            trainee_updates.append(update)
    return trainee_updates



#**Workouts Database**#

# Adds a workout to the database
def add_workout(date, day, timeslot, trainer, level, trainees, max_num_of_trainees, pending, in_current_week, default):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if not workout_exists(date, day, timeslot):
            workouts.insert_one({'Date': date, 'Day': day, 'Time-Slot':timeslot, 'Trainer': trainer, 'Level':level,
                                 'Trainees': trainees, 'Max Number Of Trainees': max_num_of_trainees, 'Pending': pending,
                                 'Current Week': in_current_week, 'Default': default})
            return True
        return False

# Deletes a workout from the database
def delete_workout(workout):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        workouts.delete_one(workout)

# Adds a trainee to a workout in the database
def add_trainee_to_workout(date, day, timeslot, username):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if workout_exists(date, day, timeslot):
            max_num_of_trainees = get_from_workout(date, timeslot, 'Max Number Of Trainees')
            trainees = get_from_workout(date, timeslot, 'Trainees')
            trainees.append(username)
            if len(trainees) < max_num_of_trainees:
                workouts.update_one({'Date': date, 'Time-Slot': timeslot}, {'$set': {'Trainees': trainees}})
                return True
        return False

# Retrieves a specific field from a workout in the database
def get_from_workout(date, timeslot, field):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        workout = workouts.find_one({'Date':date, 'Time-Slot':timeslot})
        return workout.get(field)

# Retrieves a specific field from a default workout in the database
def get_from_default(day, timeslot, field):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        workout = workouts.find_one({'Day': day, 'Default': True, 'Time-Slot': timeslot})
        return workout.get(field)

# Checks if a workout exists in the database
def workout_exists(date, day, timeslot):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if workouts.find_one({'Time-Slot': timeslot, 'Day': day, 'Date': date}):
            return True
        return False

# Updates a specific field in a workout in the database
def update_workout(date, day, timeslot, field, new_data):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if workout_exists(date, day, timeslot):
            workouts.update_one({'Time-Slot': timeslot, 'Day': day, 'Date': date}, {'$set': {field: new_data}})
            workout = workouts.find_one({'Time-Slot': timeslot, 'Date': date})
            if workout[field] == new_data:
                return True
            return False
        return False

# Retrieves all workouts for the current week from the database
def get_workouts_in_week():
    workouts_list = []
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        for workout in workouts.find({'Current Week': True}):
            workouts_list.append(workout)
    return workouts_list

# Replaces a workout in the database or adds it if it doesn't exist
def replace_workout(date, day, timeslot, trainer, level, trainees, max_num_of_trainees, pending, in_current_week, default):
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        if workout_exists(date, day, timeslot):
            workouts.update_one({'Time-Slot': timeslot, 'Date': date, 'Day': day},
                                {'$set': {'Trainer': trainer, 'Level':level, 'Trainees': trainees,
                                          'Max Number Of Trainees': max_num_of_trainees, 'Pending': pending,
                                          'Current Week': in_current_week, 'Default': default}})
        else:
            add_workout(date, day, timeslot, trainer, level, trainees, max_num_of_trainees, pending, in_current_week,
                        default)

# Retrieves all default workouts from the database
def get_default_workouts():
    default_schedule = []
    with MongoClient(uri) as cluster:
        workouts = cluster['GYM']['Workouts']
        for workout in workouts.find({'Default': True}):
            default_schedule.append((workout['Day'], workout['Time-Slot']))
    return default_schedule


#**Users Database**#

# Retrieves a list of users with a specified role from the database
def get_users(role):
    users_list = []
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']

        for user in users.find({'Role': role}):
            users_list.append(user['Username'])

    return users_list

# Updates a specific field for a user in the database
def update_user(username, field, new_data):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        users.update_one({'Username':username}, {'$set': {field: new_data}})
        user = users.find_one({'Username':username})
        if user[field] == new_data:
            return True
        return False
    return False

# Retrieves a specific field for a user from the database
def get_from_user(username, field):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        user = users.find_one({'Username':username})
        return user.get(field)

# Checks if a user exists in the database
def user_exists(username):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if users.find_one({'Username': username}):
            return True
        return False

# Adds a trainee to the database
def add_trainee(username, password, level):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if not user_exists(username):
            users.insert_one({'Username':username, 'Password':password, 'Role': 'Trainee', 'Level':level})
            return True
        return False

# Adds a trainer request to the database
def add_trainer(username, password, level):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if not user_exists(username):
            users.insert_one({'Username':username, 'Password':password, 'Role':'Trainer Request', 'Level':level})
            return True
        return False

# Checks user login credentials against the database
def user_login(username, password):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        if users.find_one({'Username': username, 'Password': password}):
            user = users.find_one({'Username': username, 'Password': password})
            return user.get('Role')
        return 'false'

# Deletes a user from the database
def delete_user(username):
    with MongoClient(uri) as cluster:
        users = cluster['GYM']['Users']
        users.delete_one({'Username': username})
