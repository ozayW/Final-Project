import DBHandle
from datetime import timedelta
from datetime import datetime
# Function to find the date of the current week based on the given day_of_week
def find_date_in_current_week(day_of_week):
    today = datetime.now() + timedelta(days=0)
    current_day = (today.isoweekday() + 1) % 7
    if current_day == 0:
        current_day = 7

    days_until_target_day = (day_of_week - current_day)
    target_date = today + timedelta(days=days_until_target_day)
    return target_date

# Function to find the time based on the given timeslot
def find_time(timeslot):
    return timeslot + 12

# Function to check if a workout with the given date and timeslot is pending
def is_pending(date, timeslot):
    time = find_time(timeslot)

    if isinstance(date, str):
        day, month, year = map(int, date.split('-'))
        given_datetime = datetime(year, month, day, time, 0, 0)
    elif isinstance(date, datetime):
        given_datetime = date.replace(hour=time)
    else:
        raise ValueError("Invalid input type for date")

    current_datetime = datetime.now()

    return given_datetime > current_datetime

# Function to check if a given date is within the current week
def is_in_current(date):
    if isinstance(date, str):
        day, month, year = map(int, date.split('-'))
        date = datetime(year, month, day).date()
    elif isinstance(date, datetime):
        date = date.date()

    current_date = datetime.now().date()
    current_day = (current_date.isoweekday() + 1) % 7
    if current_day == 0:
        current_day = 7

    current_week_start = current_date - timedelta(days=current_day - 1)
    current_week_end = current_week_start + timedelta(days=6)
    return current_week_start <= date <= current_week_end



# Class representing a Workout instance
class Workout:
    def __init__(self, date, day, timeslot, trainer, level, trainees, max_trainees, pending=False, current=False,
                 default=False):
        self.date = date
        self.day = day
        self.timeslot = timeslot
        self.trainer = trainer
        self.level = level
        self.trainees = trainees
        self.max_trainees = max_trainees
        self.default = default
        if date == 'None':
            self.default = True

        if not pending and not self.default:
            self.pending = is_pending(self.date, self.timeslot)
        else:
            self.pending = pending

        if not current and not self.default:
            self.in_current = is_in_current(self.date)
        else:
            self.in_current = current

    # Getters and setters
    def get_day(self):
        return self.day

    def set_date(self, d):
        self.date = d

    def set_default(self, d):
        self.default = d

    def set_current(self):
        self.in_current = is_in_current(self.date)

    def set_pending(self):
        self.in_current = is_pending(self.date, self.timeslot)

    # Add Workout to the database
    def add_to_dataBase(self):
        DBHandle.add_workout(self.date, self.day, self.timeslot, self.trainer, self.level, self.trainees, self.max_trainees,
                             self.pending, self.in_current, self.default)

    # Update database for pending workouts
    def update_data_base_pending(self):
        if self.pending:
            self.pending = is_pending(self.date, self.timeslot)

            if not self.pending:
                DBHandle.update_workout(self.date, self.day, self.timeslot, 'Pending', self.pending)

    # Get day of the workout
    def get_day(self):
        return self.day

    # Get timeslot of the workout
    def get_timeslot(self):
        return self.timeslot

    # Check if the workout is in the current week
    def get_in_current(self):
        return self.in_current

    # Get trainer of the workout
    def get_trainer(self):
        return self.trainer

    # Get level of the workout
    def get_level(self):
        return self.level

    # Get formatted date of the workout
    def get_date(self):
        return self.date.strftime("%d-%m-%Y")

    # Get maximum number of trainees for the workout
    def get_max_trainees(self):
        return self.max_trainees

    # Get list of trainees for the workout
    def get_trainees(self):
        return self.trainees

    # Get trainees list as a string
    def get_trainees_list(self):
        trainees = ""
        if not self.trainees:
            return "None"
        for trainee in self.trainees:
            trainees += trainee
        return trainees

    # Get pending status of the workout
    def get_pending(self):
        return self.pending

    # Update database for workouts in the current week
    def update_data_base_current(self):
        if self.in_current:
            self.in_current = is_in_current(self.date)

            if not self.in_current:
                while True:
                    try:
                        DBHandle.update_workout(self.date, self.day, self.timeslot, 'Current Week', self.pending)
                        break
                    except:
                        pass

    # Add trainees to the workout
    def add_trainees(self, trainees):
        if trainees.len() + self.trainees.len() > self.max_trainees:
            return False
        self.trainees.append(trainees)
        DBHandle.update_workout(self.date, self.day, self.timeslot, 'Trainees', self.trainees)
        return True

    # Add a single trainee to the workout
    def add_trainee(self, trainee):
        if not self.full():
            self.trainees.append(trainee)
            DBHandle.add_trainee_to_workout(self.date, self.day, self.timeslot, trainee)

    # Update workout in the database
    def update_workout(self):
        while True:
            try:
                DBHandle.replace_workout(self.date, self.day, self.timeslot, self.trainer, self.level, self.trainees,
                                         self.max_trainees, self.pending, self.in_current, self.default)
                break
            except:
                pass

    # Check if the workout is full
    def full(self):
        if self.max_trainees == len(self.trainees):
            return True
        return False

    # Check if a user is among the trainees
    def user_in_trainees(self, username):
        for trainee in self.trainees:
            if trainee == username:
                return True
        return False

    # Cancel the workout
    def cancel_workout(self):
        self.trainer = 'None'
        self.level = None
        self.trainees = None
        self.max_trainees = 0
        self.update_workout()

    # String representation of the workout object
    def __str__(self):
        return f'{self.date,self.day, self.timeslot, self.trainer, self.level, self.trainees, self.max_trainees, self.pending, self.in_current, self.default}'

# Function to sort workouts by day
def sort_by_day(workouts):
    n = len(workouts)
    for i in range(n):
        for j in range(0, n - i - 1):
            day1 = workouts[j].get_day()
            day2 = workouts[j+1].get_day()
            if day1 > day2:
                workouts[j], workouts[j + 1] = workouts[j + 1], workouts[j]
    return workouts

# Function to sort workouts by timeslot
def sort_by_timeslot(workouts):
    n = len(workouts)
    for i in range(n):
        for j in range(0, n - i - 1):
            day1 = workouts[j].get_timeslot()
            day2 = workouts[j + 1].get_timeslot()
            if day1 > day2:
                workouts[j], workouts[j + 1] = workouts[j + 1], workouts[j]
    return workouts

# Function to get the default schedule of workouts
def get_default_schedule():
    defaults = DBHandle.get_default_workouts()
    workouts = []
    for default in defaults:
        while True:
            try:
                date = 'None'
                day = default[0]
                time_slot = default[1]
                trainer = DBHandle.get_from_default(day, time_slot, 'Trainer')
                level = DBHandle.get_from_default(day, time_slot, 'Level')
                trainees = DBHandle.get_from_default(day, time_slot, 'Trainees')
                max_num_of_trainees = DBHandle.get_from_default(day, time_slot, 'Max Number Of Trainees')
                pending = False
                current = False
                workout = Workout(date, day, time_slot, trainer, level, trainees, max_num_of_trainees, pending, current, True)
                workouts.append(workout)
                break
            except:
                pass
    sort_by_timeslot(workouts)
    sort_by_day(workouts)

    return workouts

# Function to set the default schedule of workouts
def set_default_schedule(workouts):
    for workout in workouts:
        workout.update_workout()

# Function to create a schedule for the current week
def create_week_schedule():
    defaults = get_default_schedule()
    for default in defaults:
        while True:
            try:
                date = find_date_in_current_week(default.get_day())
                default.set_date(date)
                default.set_current()
                default.set_pending()
                default.set_default(False)
                day = default.get_day()
                timeslot = default.get_timeslot()
                trainer = default.get_trainer()
                level = default.get_level()
                trainees = default.get_trainees()
                max_num_of_trainees = default.get_max_trainees()
                pending = default.get_pending()
                DBHandle.add_workout(date, day, timeslot, trainer, level, trainees, max_num_of_trainees, pending, True, False)
                break
            except:
                pass
    return defaults
