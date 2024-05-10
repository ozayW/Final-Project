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