# Python libraries that we need to import for our bot
import random
from flask import Flask, request, session
from pymessenger.bot import Bot
from chatbot import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

ACCESS_TOKEN = 'EAAHufIMwjsABACmNBWqFd0BfSedVWDovdCgeytImjznKJHZCWptBESBq3S27bxQNWB2rd0JRcZClPMMNM1r03z6MnO4oIyzjAE4b8D5w8H16UFKOWeHAIo5kj9UUkeY5F35rPXMwRJWOLU0ZCg7SibWnaR2irhHKZCZA8yfu2u9VIAZCYosWj2'
VERIFY_TOKEN = 'VERIFY_TOKEN_FB'
bot = Bot(ACCESS_TOKEN)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        chat_log = session.get('chat_log')
        if chat_log is None:
            chat_log = start_chat_log
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    incoming_msg_text = message['message'].get('text')
                    print(incoming_msg_text)
                    if incoming_msg_text:
                        response_sent_text = ask(incoming_msg_text, chat_log)
                        session['chat_log'] = append_interaction_to_chat_log(incoming_msg_text, response_sent_text, chat_log)
                        print(chat_log)
                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = 'Sorry, I cannot read those type of attachements right now!'
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# chooses a random message to send to the user
#def get_message(incoming_msg, chat_log):
    #sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!",
    #                   "We're greatful to know you :)"]
    # return selected item to the user
    #return random.choice(sample_responses)




# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run(debug=True)
