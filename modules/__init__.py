from flask_sqlalchemy import SQLAlchemy

from run import app
from modules.game_tracker import GameTracker

db = SQLAlchemy(app)
GAME_TRACKER = GameTracker()
db.session.add(GAME_TRACKER)
db.session.commit()
