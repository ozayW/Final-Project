import DBHandle
import datetime

def find_time(timeslot):
    return timeslot + 12
def is_pending(date, timeslot):
    time = find_time(timeslot)
    day, month, year = map(int, date.split('-'))
    given_datetime = datetime.datetime(year, month, day, time, 0, 0)

    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Check if the given date and hour have already passed
    return given_datetime > current_datetime

def is_in_current(date):
    year, month, day = map(int, date.split('-'))
    date = datetime.date(year, month, day)

    # Get the current date
    current_date = datetime.date.today()

    # Calculate the start and end dates of the current week
    current_week_start = current_date - datetime.timedelta(days=current_date.weekday())
    current_week_end = current_week_start + datetime.timedelta(days=6)

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
            self.in_current = is_in_current()
        else:
            self.in_current = current


    def add_to_dataBase(self):
        DBHandle.add_workout(self.date,self.day, self.timeslot, self.trainer, self.level, self.trainees, self.max_trainees,
                             self.pending, self.in_current, self.default)

    def update_data_base_pending(self):
        if self.pending:
            self.pending = is_pending(self.date, self.timeslot)

            if not self.pending:
                DBHandle.update_workout(self.date, self.timeslot, 'Pending', self.pending)

    def get_day(self):
        return self.day

    def get_timeslot(self):
        return self.timeslot
    def update_data_base_current(self):
        if self.in_current:
            self.in_current = is_in_current(self.date)

            if not self.in_current:
                DBHandle.update_workout(self.date, self.timeslot, 'Pending', self.pending)

    def add_trainees(self, trainees):
        if trainees.len() + self.trainees.len() > self.max_trainees:
            return False
        self.trainees.append(trainees)
        DBHandle.update_workout(self.date, self.timeslot, 'Trainees', self.trainees)
        return True

    def update_workout(self):
        DBHandle.replace_workout(self.date,self.day, self.timeslot, self.trainer, self.level, self.trainees,
                                self.max_trainees, self.pending, self.in_current, self.default)

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
        date = 'None'
        day = default[0]
        time_slot = default[1]
        trainer = DBHandle.get_from_default(day, time_slot, 'Trainer')
        level = DBHandle.get_from_default(day, time_slot, 'Level')
        trainees = DBHandle.get_from_default(day, time_slot, 'Trainees')
        max_num_of_trainees = DBHandle.get_from_default(day,time_slot, 'Max Number Of Trainees')
        pending = False
        current = False
        workout = Workout(date, day, time_slot, trainer, level, trainees, max_num_of_trainees, pending, current, True)
        workouts.append(workout)
    sort_by_timeslot(workouts)
    sort_by_day(workouts)

    return workouts

def set_default_schedule(workouts):
    for workout in workouts:
        print("updating:")
        print(workout)
        workout.update_workout()
