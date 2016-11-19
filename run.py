from game_tracker import GameTracker
# import twilio.twiml
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "super secret key"

# GAME_TRACKER = GameTracker()

def parse_message(msg):
    return (msg.get('From', None), msg.get('Body', ''), msg.get('MediaUrl0', None))

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    topic= session.get('topic', None)
    pics_received = session.get('pics_received', 0)
    players = session.get('players', None)
    GAME_TRACKER = GameTracker(topic, pics_received, players)
    from_number, body, pic_url = parse_message(request.values)
    # numMedia = request.values.get('NumMedia', 0)
    # pic_url = None
    # if numMedia > 0:
        # pic_url = request.values.get('MediaUrl0', None)
    if not from_number:
        print "WARNING: from number not found."
        return ''
    print "Message from", from_number, "saying", body
    print GAME_TRACKER.players
    if from_number not in GAME_TRACKER.players:
        resp = GAME_TRACKER.add_player(from_number)
    elif "done" in body.lower():
        resp = GAME_TRACKER.remove_player(from_number)
    # elif not GAME_TRACKER.players[from_number].name:
    elif not GAME_TRACKER.players[from_number][0]:
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
    session['topic'] = GAME_TRACKER.topic
    session['pics_received'] = GAME_TRACKER.pics_received
    session['players'] = GAME_TRACKER.players
    return resp

if __name__ == '__main__':
    app.debug = True
    app.run()
