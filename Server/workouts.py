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
    def __init__(self, date, timeslot, trainer, level, trainees, max_trainees):
        self.date = date
        self.timeslot = timeslot
        self.trainer = trainer
        self.level = level
        self.trainees = trainees
        self.max_trainees = max_trainees
        self.pending = is_pending(self.date, self.timeslot)
        self.in_current = is_in_current(self.date)
    def add_to_dataBase(self):
        DBHandle.add_workout(self.date, self.timeslot, self.trainer, self.level, self.trainees, self.max_trainees,
                             self.pending, self.in_current)

    def update_data_base_pending(self):
        if self.pending:
            self.pending = is_pending(self.date, self.timeslot)

            if not self.pending:
                DBHandle.update_workout(self.date, self.timeslot, 'Pending', self.pending)

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