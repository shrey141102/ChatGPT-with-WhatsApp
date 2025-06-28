import os
import json
import logging
import requests
import base64
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from memory_manager import MemoryManager
from prompts import SYSTEM_PROMPT, IMAGE_PROMPT

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
            
            base_data = {
                'phone_number_id': value['metadata']['phone_number_id'],
                'from_number': message['from'],
                'message_id': message.get('id'),
                'message_type': message.get('type')
            }
            
            if message.get('type') == 'text':
                base_data['message_body'] = message['text']['body']
                return base_data
            
            elif message.get('type') == 'image':
                base_data['image_id'] = message['image']['id']
                base_data['image_caption'] = message['image'].get('caption', '')
                return base_data
                
    except Exception as e:
        logger.error(f"Error extracting message: {e}")
    return None

def download_whatsapp_image(image_id):
    """Download image from WhatsApp and convert to base64."""
    try:
        # Get image URL
        url = f"https://graph.facebook.com/v18.0/{image_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        image_url = response.json().get('url')
        if not image_url:
            return None
        
        # Download the actual image
        image_response = requests.get(image_url, headers=headers)
        image_response.raise_for_status()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_response.content).decode('utf-8')
        
        # Determine image type
        content_type = image_response.headers.get('content-type', 'image/jpeg')
        
        logger.info(f"📷 Downloaded image: {len(image_base64)} characters, type: {content_type}")
        return f"data:{content_type};base64,{image_base64}"
        
    except Exception as e:
        logger.error(f"❌ Error downloading image: {e}")
        return None

def analyze_image_with_ai(user_id, image_base64, caption=""):
    """Analyze image using OpenAI Vision."""
    try:
        logger.info(f"🔍 Analyzing image for {user_id} with caption: '{caption}'")
        
        # Get user context
        context = memory.get_user_context(user_id)
        
        # Prepare messages for vision
        messages = [
            {"role": "system", "content": IMAGE_PROMPT}
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Previous context: {context}"})
        
        # Add the image message
        user_content = [
            {"type": "text", "text": caption if caption else "What do you see in this image?"},
            {"type": "image_url", "image_url": {"url": image_base64}}
        ]
        messages.append({"role": "user", "content": user_content})
        
        # Call OpenAI Vision
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Supports vision
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"🤖 Image analysis for {user_id}: {ai_response}")
        
        # Store in memory (without the actual image data)
        memory_text = f"User sent an image{': ' + caption if caption else ''}. I analyzed it and responded: {ai_response}"
        memory_stored = memory.store_conversation(user_id, f"[Image]{': ' + caption if caption else ''}", ai_response)
        logger.info(f"💾 Image memory stored for {user_id}: {memory_stored}")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"❌ Error analyzing image: {e}")
        return "I can see you sent an image, but I'm having trouble analyzing it right now. Could you try again or describe what you'd like to know about it?"
    
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
        message_type = message_data.get('message_type')
        
        # Handle different message types
        if message_type == 'text':
            user_message = message_data['message_body']
            ai_response = chat_with_ai(user_id, user_message)
            
        elif message_type == 'image':
            image_id = message_data['image_id']
            caption = message_data.get('image_caption', '')
            
            # Download and analyze image
            image_base64 = download_whatsapp_image(image_id)
            if image_base64:
                ai_response = analyze_image_with_ai(user_id, image_base64, caption)
            else:
                ai_response = "I couldn't download your image. Please try sending it again."
        
        else:
            ai_response = "I can only handle text messages and images right now. Please send me a text or image!"
        
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
        "memory": "Mem0",
        "features": ["text_chat", "image_analysis"]
    })

if __name__ == '__main__':
    # Validate required environment variables
    required_vars = [VERIFY_TOKEN, WHATSAPP_TOKEN, OPENAI_API_KEY, MEM0_API_KEY]
    if not all(required_vars):
        logger.error("❌ Missing required environment variables")
        exit(1)
    
    logger.info("🚀 Starting WhatsApp AI Bot...")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))