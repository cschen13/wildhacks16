from run import db

class Player(db.Model):
    phone_num = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(80))
    score = db.Column(db.Integer)

    def __init__(self, phone_num, name=None):
        self.phone_num = phone_num
        self.name = name
        self.score = 0
