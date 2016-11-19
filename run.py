from flask import Flask, request, redirect
import twilio.twiml
import config.py
from twilio.rest import TwilioRestClient 

app = Flask(__name__)

callers = set(["+12246221941"])

player_names = dict([('+19087272654',"Vincent")])
player_answers = dict([('+19087272654',"https://www.extension.umd.edu/sites/default/files/resize/_images/programs/viticulture/table-grapes-74344_640-498x291.jpg")])
player_scores = dict([('+19087272654',0)])
pics_received = 0
client = TwilioRestClient(ACCOUNT, TOKEN) 

master = "+19087272654"
host = "+16693421879"

topic = None

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    from_number = request.values.get('From', None)
    from_message = request.values.get('Body', '')
    numMedia = request.values.get('NumMedia',None)
    media = None
    if numMedia > 0:
        media = request.values.get('MediaUrl0',None)
    resp = twilio.twiml.Response()
    if from_number:
        print "Message from", from_number, "saying", from_message
        print player_names
        print player_answers
        print player_scores
        print pics_received
        print callers
        players
        if from_number not in callers:
            callers.add(from_number)
            player_names[from_number] = None
            player_answers[from_number] = None
            player_scores[from_number] = 0
            message = "You have entered the game. Message me back with your player name. Message me \'done\' at anytime to leave."
        if "done" in from_message.lower():
            callers.remove(from_number)
            message = "You have left the game. Message me anything if you want to join in"
            return ''
        if "master" in from_message.lower():
        	master = from_number
        	message = "You are now the game master. Message me again to set the topic"
        	return ''
        if from_number == master:
            topic = from_message
            message = ('Messaging all the players to find "'+from_message+'".')
            #message all the players what to find
            for player in player_names:
            	client.messages.create(to=player[0],from_=host,body=message)
            return ''
        if from_number in player_names and players[from_number] == None:
            players[from_number] = from_message
            message = ('Thanks "'+from_message+'"! I\'ll let you know what to find soon."')
        if numMedia > 0:
        	player_answers[from_number] = media
        	if topic == None:
        		message = "Sorry! Submissions are closed."
        	#return whether or not this is an accurate picture
        	accurate_picture = True
        	if accurate_picture:
        		player_scores[from_number] += 3-pics_received
        		pics_received = pics_received+1
        		points_received = str(3-pics_received)
        		current_points = str(player_scores[from_number])
        		message = ('Congrats this picture is a match! You have earned "'+points_received+'" points. You now have "'+current_points+'" points.')
        		if pics_received == 3:
        			pics_received = 0
        			Topic = None
        			#message the master to get a new topic
        			client.messages.create(to=master,from_=host,body="Please send me a new item for the participants to find.")
        			ls = ""
        			for item in player_scores:
        				ls += (player_names[item[0]]+" has "+str(item[1])+" points.\n")
        			broadcast = ('The new standings are:\n'+ls)
        resp.message(message)
        return str(resp)
    return ''

if __name__ == "__main__":
    app.run(debug=True)
