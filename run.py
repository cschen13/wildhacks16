# import twilio.twiml
from game_tracker import GameTracker
import twilio.twiml
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "super secret key"

#GAME_TRACKER = GameTracker()

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    topic= session.get('topic', None)
    pics_received = session.get('pics_received', 0)
    players = session.get('players', {})
    GAME_TRACKER = GameTracker(topic, pics_received, players)
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
    print GAME_TRACKER.players
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
    session['topic'] = GAME_TRACKER.topic
    session['pics_received'] = GAME_TRACKER.pics_received
    session['players'] = GAME_TRACKER.players
    return resp

# if __name__ == "__main__":
#     app.secret_key = 'super secret key'
#     app.config['SESSION_TYPE'] = 'filesystem'

#     sess.init_app(app)

#     app.debug = True
#     app.run()
if __name__ == '__main__':
    app.debug = True
    app.run()