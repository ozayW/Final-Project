import DBHandle

# Class to represent an update for a workout session
class Update:
    def __init__(self, trainee, date, pullups, one_arm_pullups, deadhang, spinning_bar_deadhang, lashe):
        self.trainee = trainee
        self.date = date
        self.pullups = pullups
        self.one_arm_pullups = one_arm_pullups
        self.deadhang = deadhang
        self.spinning_bar_deadhang = spinning_bar_deadhang
        self.lashe = lashe

    # Getter method for trainee
    def get_trainee(self):
        return self.trainee

    # Getter method for date
    def get_date(self):
        return self.date

    # Getter method for pullups
    def get_pullups(self):
        return self.pullups

    # Getter method for one-arm pullups
    def get_one_arm_pullups(self):
        return self.one_arm_pullups

    # Getter method for deadhang
    def get_deadhang(self):
        return self.deadhang

    # Getter method for spinning bar deadhang
    def get_spinning_bar_deadhang(self):
        return self.spinning_bar_deadhang

    # Getter method for lashe
    def get_lashe(self):
        return self.lashe

    # Method to add the update to the database
    def add_update(self):
        DBHandle.add_workout_update(self.trainee, self.date, self.pullups, self.one_arm_pullups, self.deadhang, self.spinning_bar_deadhang, self.lashe)
        return self.level()

    # Method to determine the level based on the performance metrics
    def level(self):
        if int(self.pullups) >= 20 and int(self.deadhang) >= 180 and int(self.lashe) >= 4 and int(self.spinning_bar_deadhang) >= 150 and int(self.one_arm_pullups) >= 3:
            return 'Ninja'

        if int(self.pullups) >= 20 and int(self.deadhang) >= 180 and int(self.lashe) >= 3.5 and int(self.spinning_bar_deadhang) >= 100 and int(self.one_arm_pullups) > 0:
            return 'Master'

        if int(self.pullups) >= 20 and int(self.deadhang) >= 180 and int(self.lashe) >= 3 and int(self.spinning_bar_deadhang) >= 0 and int(self.one_arm_pullups) >= 0:
            return 'Professional'

        if int(self.pullups) > 5 and int(self.deadhang) >= 60 and int(self.lashe) >= 2 and int(self.spinning_bar_deadhang) >= 0 and int(self.one_arm_pullups) >= 0:
            return 'Regular Trainee'

        return 'Beginner'
