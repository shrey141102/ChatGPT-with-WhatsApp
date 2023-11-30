from flask import Flask, request
import requests
import os
import json
from openai import OpenAI
client = OpenAI()

app = Flask(__name__)


VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def chat_ai(query):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": "You are my personal helpful assistant. Please answer my question precisely and to the point"},
    {"role": "user", "content": query},
    ]
  )

    return completion.choices[0].message.content

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.json

    print(json.dumps(body, indent=2))

    if body.get('object') == 'whatsapp_business_account':
        if (
            body.get('entry') and
            body['entry'][0].get('changes') and
            body['entry'][0]['changes'][0].get('value') and
            body['entry'][0]['changes'][0]['value'].get('messages') and
            body['entry'][0]['changes'][0]['value']['messages'][0]
        ):
            phone_number_id = body['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
            from_number = body['entry'][0]['changes'][0]['value']['messages'][0]['from']
            msg_body = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

            x = chat_ai(msg_body)

            send_message_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages?access_token={WHATSAPP_TOKEN}"
            response = requests.post(
                send_message_url,
                json={
                    "messaging_product": "whatsapp",
                    "to": from_number,
                    "text": {"body": f"Answer from AI -> {x}"}
                },
                headers={"Content-Type": "application/json"}
            )
        return '', 200
    else:
        return '', 404



@app.route('/')
def hello():
    return "Hello World!"
  
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return 'Invalid Verify Token', 403

if __name__ == '__main__':
    app.run(debug = True)
