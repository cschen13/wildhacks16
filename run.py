from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

callers = set(["+12246221941"])

players = dict([('+19087272654',"Vincent")])

master = "+19087272654"

topic = None

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    from_number = request.values.get('From', None)
    from_message = request.values.get('Body', '')
    media = request.values.get('MediaUrl0','')
    resp = twilio.twiml.Response()
    if from_number:
        print "Message from", from_number, "saying", from_message

        message = media
        resp.message(message)
        return str(resp)

        # print callers
        # if from_number not in callers:
        #     callers.add(from_number)
        #     players[from_number] = 'placeholder'
        #     message = "You have entered the game. Message me back with your player name."
        # if "done" in from_message.lower():
        #     callers.remove(from_number)
        #     message = "You have left the game. Message me back if you want to join in"
        # if from_number == master:
        # 	topic = from_message
        # 	message = ('Messaging all the players to find "'+from_message+'".')
        # 	#message all the players what to find
        # if from_number in players and players[from_number] == 'placeholder':
        # 	players[from_number] = from_message
        # 	message = ('Thanks "'+from_message+'"! I\'ll let you know what to find soon.")

        #     resp.message(message)
        #     return str(resp)
    return ''

if __name__ == "__main__":
    app.run(debug=True)
