from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

callers = set(["+12246221941"])

@app.route("/", methods=['GET', 'POST'])
def respond_to_message():
    from_number = request.values.get('From', None)
    from_message = request.values.get('Body', None)
    if from_number not in callers:
        callers.add(from_number)
    if from_message.lower() == "done":
        callers.remove(from_number)
    else:
        message = "Monkey, thanks for the message!"
        resp = twilio.twiml.Response()
        resp.message(message)
        return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
