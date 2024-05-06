import DBHandle
from datetime import timedelta

def find_date_in_current_week(day_of_week):
    # Get the current date
    today = datetime.now() + timedelta(days=0)
    # Adjust the current day of the week (1 for Monday, 2 for Tuesday, ..., 7 for Sunday)
    current_day = (today.isoweekday() + 1) % 7
    if current_day == 0:
        current_day = 7

    # Calculate the difference in days between the current day and the desired day of the week
    days_until_target_day = (day_of_week - current_day)
    print(days_until_target_day)
    # Calculate the target date by subtracting the difference from the current date
    target_date = today + timedelta(days=days_until_target_day)
    return target_date


def find_time(timeslot):
    return timeslot + 12
from datetime import datetime

def is_pending(date, timeslot):
    time = find_time(timeslot)

    if isinstance(date, str):
        # Convert the input date string to a datetime.datetime object
        day, month, year = map(int, date.split('-'))
        given_datetime = datetime(year, month, day, time, 0, 0)
    elif isinstance(date, datetime):
        # Use the input datetime object directly
        given_datetime = date
    else:
        raise ValueError("Invalid input type for date")

    # Get the current date and time
    current_datetime = datetime.now()

    # Check if the given date and hour have already passed
    return given_datetime > current_datetime


def is_in_current(date):
    if isinstance(date, str):
        # Convert the input date string to a datetime.date object
        day, month, year = map(int, date.split('-'))
        date = datetime(year, month, day).date()
    elif isinstance(date, datetime):
        # Extract the date component from the datetime object
        date = date.date()

    # Get the current date
    current_date = datetime.now().date()
    # Calculate the start and end dates of the current week
    current_day = (current_date.isoweekday() + 1) % 7
    if current_day == 0:
        current_day = 7

    current_week_start = current_date - timedelta(days=current_day - 1)
    current_week_end = current_week_start + timedelta(days=6)
    # Check if the given date is within the current week
    return current_week_start <= date <= current_week_end



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

    def add_to_dataBase(self):
        DBHandle.add_workout(self.date, self.day, self.timeslot, self.trainer, self.level, self.trainees, self.max_trainees,
                             self.pending, self.in_current, self.default)

    def update_data_base_pending(self):
        if self.pending:
            self.pending = is_pending(self.date, self.timeslot)

            if not self.pending:
                DBHandle.update_workout(self.date, self.day, self.timeslot, 'Pending', self.pending)

    def get_day(self):
        return self.day

    def get_timeslot(self):
        return self.timeslot

    def get_in_current(self):
        return self.in_current

    def get_trainer(self):
        return self.trainer

    def get_level(self):
        return self.level

    def get_date(self):
        return self.date.strftime("%d-%m-%Y")

    def get_max_trainees(self):
        return self.max_trainees

    def get_trainees(self):
        return self.trainees

    def get_trainees_list(self):
        trainees = ""
        for trainee in self.trainees:
            trainees += trainee
        if not trainees:
            return "None"
        return trainees
    def get_pending(self):
        return self.pending

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

    def add_trainees(self, trainees):
        if trainees.len() + self.trainees.len() > self.max_trainees:
            return False
        self.trainees.append(trainees)
        DBHandle.update_workout(self.date, self.day, self.timeslot, 'Trainees', self.trainees)
        return True

    def update_workout(self):
        while True:
            try:
                DBHandle.replace_workout(self.date, self.day, self.timeslot, self.trainer, self.level, self.trainees,
                                         self.max_trainees, self.pending, self.in_current, self.default)
                break
            except:
                pass
    def __str__(self):
        return f'{self.date,self.day, self.timeslot, self.trainer, self.level, self.trainees, self.max_trainees, self.pending, self.in_current, self.default}'


def sort_by_day(workouts):
    n = len(workouts)
    for i in range(n):
        for j in range(0, n - i - 1):
            day1 = workouts[j].get_day()
            day2 = workouts[j+1].get_day()
            if day1 > day2:
                workouts[j], workouts[j + 1] = workouts[j + 1], workouts[j]
    return workouts

def sort_by_timeslot(workouts):
    n = len(workouts)
    for i in range(n):
        for j in range(0, n - i - 1):
            day1 = workouts[j].get_timeslot()
            day2 = workouts[j + 1].get_timeslot()
            if day1 > day2:
                workouts[j], workouts[j + 1] = workouts[j + 1], workouts[j]
    return workouts

def get_default_schedule():
    defaults = DBHandle.get_default_workouts()
    workouts = []
    for default in defaults:
        while True:
            try:
                print(default)
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

def set_default_schedule(workouts):
    for workout in workouts:
        print("updating:")
        print(workout)
        workout.update_workout()

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
                print('building workout')
                DBHandle.add_workout(date, day, timeslot, trainer, level, trainees, max_num_of_trainees, pending, True, False)
                break
            except:
                pass
    return defaults
