from modules.game_tracker import GameTracker
from modules import db

import os

from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    # app.register_blueprint(api)
    db.init_app(app)
    with app.app_context():
    # with app.test_request_context():
        from modules.game_tracker import GameTracker
        from modules.player import Player
        db.create_all()
    return app

app = create_app()
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# # db = SQLAlchemy(app)
# db.init_app(app)
# with app.test_request_context():
#     db.create_all()

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
        GAME_TRACKER.send_message(from_number, resp)
    return resp

if __name__ == '__main__':
    app.debug = True
    app.run()
