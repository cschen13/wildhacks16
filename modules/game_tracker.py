import os
from twilio.rest import TwilioRestClient

from modules.player import Player
from modules import db

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
        self.players[phone_num].name = name
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
        points_received = 3 - self.pics_received
        self.players[phone_num].score += points_received
        self.pics_received += 1
        msg = ("Congrats this picture is a match! You have earned "
               + str(points_received) + " points. You now have "
               + str(players[phone_num].score) + " points.")
        self.send_message(phone_num, msg)
        if self.pics_received == self.prizes_per_round:
            self.pics_received = 0
            self.send_leaderboard()
            self.change_topic()
        return msg

    def send_leaderboard(self):
        leaderboard = []
        for player in self.players.iteritems():
            leaderboard.append((player.name, player.score))
        leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
        ls = ""
        for player in leaderboard:
            ls += (player[0] + " has " + str(player[1]) + " points.\n")
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