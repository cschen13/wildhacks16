import os

from twilio.rest import TwilioRestClient
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)



class GameTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120))
    pics_received = db.Column(db.Integer)

    def __init__(self, topic=None, pics_received=0):
        if not topic:
            topic = "chair"
        self.topic = topic
        self.pics_received = pics_received
        self.twilio_client = TwilioClient()
        self.prizes_per_round = 3

    def add_player(self, phone_num):
        player = Player(phone_num)
        db.session.add(player)
        db.session.commit()
        msg = ("You have entered the game. Message me back with your "
               "player name. Message me \"done\" at anytime to leave.")
        self.send_message(phone_num, msg)
        return msg

    def remove_player(self, phone_num):
        player = Player.query.get(phone_num)
        db.session.delete(player)
        db.session.commit()
        msg = "You have left the game. Message me anything if you want to join in."
        self.send_message(phone_num, msg)
        return msg

    def set_player_name(self, phone_num, name):
        player = Player.query.get(phone_num)
        player.name = name
        db.session.commmit()
        msg = "Thanks " + name + "! You're looking for a " + self.topic
        self.send_message(phone_num, msg)
        return msg

    def judge_picture(self, phone_num, picture_url):
        #return whether or not this is an accurate picture using clarifai api
        accurate_picture = True # TODO:
        if accurate_picture:
            return self.give_points(phone_num)
        return "Sorry that's not a picture of a " + self.topic + "."

    def give_points(self, phone_num):
        player = Player.query.get(phone_num)
        points_received = 3 - self.pics_received
        player.score += points_received
        db.session.commit()
        self.pics_received += 1
        msg = ("Congrats this picture is a match! You have earned "
               + str(points_received) + " points. You now have "
               + str(players[phone_num].score) + " points.")
        self.send_message(phone_num, msg)
        if self.pics_received == self.prizes_per_round:
            self.pics_received = 0
            self.send_leaderboard()
            self.change_topic()
        db.session.commit()
        return msg

    def send_leaderboard(self):
        leaderboard = []
        for player in Player.query.all():
            leaderboard.append((player.name, player.score))
        leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
        standings = ""
        for player in leaderboard:
            standings += (player[0] + " has " + str(player[1]) + " points.\n")
        self.send_to_all_players("The new standings are:\n" + ls)

    def change_topic(self):
        msg = "The new topic is chair." # TODO:
        self.send_to_all_players(msg)

    def send_to_all_players(self, msg):
        for player in Player.query.all():
            self.twilio_client.send_message(player, msg)

    def send_message(self, to, msg):
        self.twilio_client.send_message(to, msg)


class TwilioClient(object):
    def __init__(self):
        ACCOUNT = os.environ['ACCOUNT']
        TOKEN = os.environ['TOKEN']
        self.client = TwilioRestClient(ACCOUNT, TOKEN)
        self.phone_num = "+16693421879"

    def send_message(self, to, msg):
        self.client.messages.create(to=to, from_=self.phone_num, body=msg)

class Player(db.Model):
    phone_num = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(80))
    score = db.Column(db.Integer)

    def __init__(self, phone_num, name=None):
        self.phone_num = phone_num
        self.name = name
        self.score = 0






GAME_TRACKER = GameTracker()
db.session.add(GAME_TRACKER)
db.session.commit()

def parse_message(msg):
    return (msg.get('From', None), msg.get('Body', ''), msg.get('MediaUrl0', None))

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    # topic= None
    # pics_received = 0
    # players = None
    # GAME_TRACKER = GameTracker(topic, pics_received, players)
    from_number, body, pic_url = parse_message(request.values)
    # numMedia = request.values.get('NumMedia', 0)
    # pic_url = None
    # if numMedia > 0:
        # pic_url = request.values.get('MediaUrl0', None)
    if not from_number:
        print "WARNING: from number not found."
        return ''
    print "Message from", from_number, "saying", body
    # if from_number not in Player.query.all():
    if not Player.query.get(from_number):
        resp = GAME_TRACKER.add_player(from_number)
    elif "done" in body.lower():
        resp = GAME_TRACKER.remove_player(from_number)
    elif not Player.query.get(from_number).name:
        resp = GAME_TRACKER.set_player_name(from_number, body)
    # elif not GAME_TRACKER.topic:
    #     resp = "Sorry! Submissions are closed."
    #     GAME_TRACKER.send_message(from_number, resp)
    # if numMedia > 0:
    elif pic_url:
        print "Picture message with url:", pic_url
        resp = GAME_TRACKER.judge_picture(from_number, pic_url)
    else:
        resp = "You're supposed to send a picture, idiot"
        GAME_TRACKER.send_message(from_number, resp)
    return resp

if __name__ == '__main__':
    app.debug = True
    app.run()












