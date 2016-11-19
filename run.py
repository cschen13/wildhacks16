import os
# import twilio.twiml
from game_tracker import GameTracker

from flask import Flask, request, redirect

app = Flask(__name__)

GAME_TRACKER = GameTracker()

players = {"+19087272654": Player("Vincent")}

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    from_number = request.values.get('From', None)
    from_message = request.values.get('Body', '')
    picture_url = request.values.get('MediaUrl0', None)
    # numMedia = request.values.get('NumMedia', 0)
    # picture_url = None
    # if numMedia > 0:
        # picture_url = request.values.get('MediaUrl0', None)
    # resp = twilio.twiml.Response()
    if not from_number:
        print "WARNING: from number not found."
        return ''
    print "Message from", from_number, "saying", from_message
    if from_number not in GAME_TRACKER.players:
        resp = GAME_TRACKER.add_player(from_number)
    elif "done" in from_message.lower():
        resp = GAME_TRACKER.remove_player(from_number)
    elif not GAME_TRACKER.players[from_number].name:
        resp = GAME_TRACKER.set_player_name(from_number, from_message)
    elif not GAME_TRACKER.topic:
        resp = "Sorry! Submissions are closed."
    # if numMedia > 0:
    elif picture_url:
        resp = GAME_TRACKER.judge_picture(from_number, picture_url)
    else:
        resp = "You're supposed to send a picture, idiot"
    # resp.message(message)
    return resp

if __name__ == "__main__":
    app.run(debug=True)
