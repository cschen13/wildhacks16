import os

from twilio.rest import TwilioRestClient
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from recognizer import Recognizer

CLARIFAI_APP_ID = os.environ['CLARIFAI_ID']
CLARIFAI_APP_SECRET = os.environ['CLARIFAI_SECRET']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

## Database Tables
class Player(db.Model):
    phone_num = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(80))
    score = db.Column(db.Integer)

    def __init__(self, phone_num, name=None):
        self.phone_num = phone_num
        self.name = name
        self.score = 0

class Winners(db.Model):
    phone_num = db.Column(db.String(15), primary_key=True)

    def __init__(self, phone_num):
        self.phone_num = phone_num

class GameTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120))
    pics_received = db.Column(db.Integer)

    def __init__(self, topic=None, pics_received=0):
        if topic is None:
            r = Recognizer(CLARIFAI_APP_ID, CLARIFAI_APP_SECRET)
            topic = r.get_random_topic()
        self.topic = topic
        self.pics_received = pics_received

## Create tables
db.create_all()
db.session.commit()

class GameController(object):
    def __init__(self, state):
        self.topic = state.topic
        self.pics_received = state.pics_received
        self.twilio_client = TwilioClient()
        self.prizes_per_round = 3
        self.recognizer = Recognizer(CLARIFAI_APP_ID, CLARIFAI_APP_SECRET)

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

    def remove_all_players(self):
        for player in Player.query.all():
            db.session.delete(player)
            msg = "You have left the game. Message me anything if you want to join in."
            self.send_message(phone_num, msg)
        db.session.commit()
        return "All players removed."

    def set_player_name(self, phone_num, name):
        player = Player.query.get(phone_num)
        player.name = name
        db.session.commit()
        msg = "Thanks {0}! You're looking for a {1}.".format(name, self.topic)
        self.send_message(phone_num, msg)
        return msg

    def judge_picture(self, phone_num, picture_url):
        if Winners.query.get(phone_num) is not None:
            self.punish_cheater(phone_num)
        #return whether or not this is an accurate picture using clarifai api
        accurate_picture = self.recognizer.judge(self.topic, picture_url)
        if accurate_picture:
            return self.give_points(phone_num)
        else:
            msg = "Sorry, I don't recognize that as a picture of a {0}.".format(self.topic)
            self.send_message(phone_num, msg)
            return msg

    def give_points(self, phone_num):
        winner = Winners(phone_num)
        db.session.add(winner)
        db.session.commit()
        player = Player.query.get(phone_num)
        points_received = 3 - self.pics_received
        player.score += points_received
        db.session.commit()
        self.pics_received += 1
        msg = ("Congrats this picture is a match! You have earned "
               + str(points_received) + " points. You now have "
               + str(player.score) + " points.")
        self.send_message(phone_num, msg)
        if self.pics_received == self.prizes_per_round:
            self.pics_received = 0
            self.send_leaderboard()
            self.change_topic()
            self.reset_winners_table()
        return msg

    def punish_cheater(self, phone_num):
        player = Player.query.get(phone_num)
        player.score = 0
        db.session.commit()
        msg = ("You cheating scumbag. You already won this round, so since "
               "you're trying to cheat we have reset your score to ZERO.")
        self.send_message(phone_num, msg)
        return msg

    def send_leaderboard(self):
        leaderboard = []
        for player in Player.query.all():
            if player.name is not None:
                leaderboard.append((player.name, player.score))
        leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
        standings = ""
        for player in leaderboard:
            standings += ("{0}: {1} points\n".format(player[0], player[1]))
        msg = "The new standings are:\n{0}".format(standings)
        self.send_to_all_players(msg)

    def reset_winners_table(self):
        for winner in Winners.query.all():
            db.session.delete(winner)
        db.session.commit()

    def change_topic(self):
        self.topic = self.recognizer.get_random_topic()
        msg = "The new topic is {0}.".format(self.topic)
        self.send_to_all_players(msg)

    def send_to_all_players(self, msg):
        for player in Player.query.all():
            self.send_message(player.phone_num, msg)

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




def parse_message(msg):
    return (msg.get('From', None), msg.get('Body', ''), msg.get('MediaUrl0', None))

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    game_state = GameTracker.query.get(1)
    if game_state is None:
        game_state = GameTracker()
        db.session.add(game_state)
        db.session.commit()
    game_controller = GameController(game_state)
    from_number, body, pic_url = parse_message(request.values)

    if from_number is None:
        print "WARNING: from number not found."
        return ''
    print "Message from", from_number, "saying", body
    if Player.query.get(from_number) is None:
        resp = game_controller.add_player(from_number)
    elif "done" in body.lower():
        resp = game_controller.remove_player(from_number)
    elif "reset" in body.lower():
        resp = game_controller.remove_all_players()
    elif Player.query.get(from_number).name is None:
        resp = game_controller.set_player_name(from_number, body)
    elif pic_url:
        print "Picture message with url:", pic_url
        resp = game_controller.judge_picture(from_number, pic_url)
    else:
        resp = "You're supposed to send a picture of a {0}, idiot.".format(game_controller.topic)
        game_controller.send_message(from_number, resp)

    game_state.topic = game_controller.topic
    game_state.pics_received = game_controller.pics_received
    db.session.commit()
    return resp

if __name__ == '__main__':
    app.debug = True
    app.run()