import DBHandle

class Update:
    def __init__(self, trainee, date, pullups, one_arm_pullups, deadhang, spinning_bar_deadhang, lashe):
        self.trainee = trainee
        self.date = date
        self.pullups = pullups
        self.one_arm_pullups = one_arm_pullups
        self.deadhang = deadhang
        self.spinning_bar_deadhang = spinning_bar_deadhang
        self.lashe = lashe

    def get_trainee(self):
        return self.trainee

    def get_date(self):
        return self.date

    def get_pullups(self):
        return self.pullups

    def get_one_arm_pullups(self):
        return self.one_arm_pullups

    def get_deadhang(self):
        return self.deadhang

    def get_spinning_bar_deadhang(self):
        return self.spinning_bar_deadhang

    def get_lashe(self):
        return self.lashe

    def add_update(self):
        DBHandle.add_workout_update(self.trainee, self.date, self.pullups, self.one_arm_pullups, self.deadhang, self.spinning_bar_deadhang, self.lashe)
        return self.level()

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