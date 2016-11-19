import os

from player import Player
from twilio.rest import TwilioRestClient 

class GameTracker(object):
    def __init__(self,topic=None,pics_received=0,players={}):
        self.topic = topic
        self.pics_received = pics_received
        self.players = players
        self.twilio_client = TwilioClient()
        self.prizes_per_round = 3

    def add_player(self, phone_num):
        self.players[phone_num] = Player()
        msg = ("You have entered the game. Message me back with your "
               "player name. Message me \"done\" at anytime to leave.")
        self.send_message(phone_num, msg)
        return msg

    def remove_player(self, phone_num):
        del self.players[phone_num]
        msg = "You have left the game. Message me anything if you want to join in."
        self.send_message(phone_num, msg)
        return msg

    def set_player_name(self, phone_num, name):
        self.players[phone_num].name = name
        msg = "Thanks " + name + "! I'll let you know what to find soon."
        self.send_message(phone_num, msg)
        return msg

    def judge_picture(self, phone_num, picture_url):
        #return whether or not this is an accurate picture using clarifai api
        accurate_picture = True # TODO:
        if accurate_picture:
            return self.give_points(phone_num)
        return "Sorry that's not a picture of a " + self.topic + "."

    def give_points(self, phone_num):
        self.players[phone_num].score += (3 - self.pics_received)
        self.pics_received += 1
        points_received = str(3 - pics_received)
        message = ("Congrats this picture is a match! You have earned "
                   + points_received + " points. You now have "
                   + players[phone_num].score + " points.")
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
        for player in players:
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

