import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from memory_manager import MemoryManager
from prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Required environment variables
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
MEM0_API_KEY = os.getenv('MEM0_API_KEY', '')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize services
app = Flask(__name__)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
memory = MemoryManager(MEM0_API_KEY)

def extract_message_data(body):
    """Extract message data from WhatsApp webhook."""
    try:
        if (body.get('object') == 'whatsapp_business_account' and
            body.get('entry') and
            body['entry'][0].get('changes') and
            body['entry'][0]['changes'][0].get('value') and
            body['entry'][0]['changes'][0]['value'].get('messages')):
            
            value = body['entry'][0]['changes'][0]['value']
            message = value['messages'][0]
            
            if message.get('type') == 'text':
                return {
                    'phone_number_id': value['metadata']['phone_number_id'],
                    'from_number': message['from'],
                    'message_body': message['text']['body'],
                    'message_id': message.get('id')
                }
    except Exception as e:
        logger.error(f"Error extracting message: {e}")
    return None

def chat_with_ai(user_id, user_message):
    """Generate AI response with memory context."""
    try:
        logger.info(f"📩 User {user_id}: {user_message}")
        
        # Get user context from memory
        context = memory.get_user_context(user_id)
        logger.info(f"🧠 Retrieved context for {user_id}: {context[:100]}..." if context else f"🧠 No context found for {user_id}")
        
        # Prepare messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if context:
            messages.append({"role": "system", "content": f"Previous context: {context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Good for normal chats, cost-effective
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"🤖 AI Response to {user_id}: {ai_response}")
        
        # Store in memory
        memory_stored = memory.store_conversation(user_id, user_message, ai_response)
        logger.info(f"💾 Memory stored for {user_id}: {memory_stored}")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"❌ Error in chat_with_ai: {e}")
        return "Sorry, I'm having trouble right now. Please try again."

def send_whatsapp_message(phone_number_id, to_number, message):
    """Send message via WhatsApp API."""
    try:
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "text": {"body": message}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info(f"📤 Message sent to {to_number}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages."""
    try:
        body = request.json
        logger.info(f"📨 Webhook received: {json.dumps(body, indent=2)}")
        
        message_data = extract_message_data(body)
        if not message_data:
            return '', 200
        
        user_id = message_data['from_number']
        user_message = message_data['message_body']
        
        # Generate AI response
        ai_response = chat_with_ai(user_id, user_message)
        
        # Send response
        send_whatsapp_message(
            message_data['phone_number_id'],
            user_id,
            ai_response
        )
        
        return '', 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return '', 500

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp setup."""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == VERIFY_TOKEN:
        logger.info("✅ Webhook verified successfully")
        return challenge, 200
    else:
        logger.warning("❌ Invalid verify token")
        return 'Invalid Verify Token', 403

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "WhatsApp AI Bot",
        "memory": "Mem0"
    })

if __name__ == '__main__':
    # Validate required environment variables
    required_vars = [VERIFY_TOKEN, WHATSAPP_TOKEN, OPENAI_API_KEY, MEM0_API_KEY]
    if not all(required_vars):
        logger.error("❌ Missing required environment variables")
        exit(1)
    
    logger.info("🚀 Starting WhatsApp AI Bot...")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))