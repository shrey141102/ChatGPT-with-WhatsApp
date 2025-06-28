import os
import json
import logging
import time
import sqlite3
import hashlib
import hmac
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from contextlib import contextmanager
from threading import Lock

from flask import Flask, request, jsonify
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Import configuration
from config import get_config

# Load environment variables
load_dotenv()

# Get configuration
Config = get_config()

# Configure logging based on config
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# Thread lock for database operations
db_lock = Lock()

# In-memory rate limiting tracker
rate_limit_tracker: Dict[str, List[float]] = defaultdict(list)

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime
    message_id: Optional[str] = None

@dataclass
class Conversation:
    user_id: str
    messages: List[Message]
    last_activity: datetime
    message_count: int = 0

class DatabaseManager:
    """Manages SQLite database operations for conversation storage."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    user_id TEXT PRIMARY KEY,
                    last_activity TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    message_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES conversations (user_id)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                ON messages (user_id, timestamp)
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_conversation(self, user_id: str) -> Conversation:
        """Get or create conversation for a user."""
        with db_lock:
            with self.get_connection() as conn:
                # Get or create conversation record
                conv_row = conn.execute(
                    'SELECT * FROM conversations WHERE user_id = ?', 
                    (user_id,)
                ).fetchone()
                
                if not conv_row:
                    conn.execute(
                        'INSERT INTO conversations (user_id, last_activity) VALUES (?, ?)',
                        (user_id, datetime.now())
                    )
                    conn.commit()
                    message_count = 0
                    last_activity = datetime.now()
                else:
                    message_count = conv_row['message_count']
                    last_activity = datetime.fromisoformat(conv_row['last_activity'])
                
                # Get recent messages
                message_rows = conn.execute('''
                    SELECT * FROM messages 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, Config.MAX_CONVERSATION_LENGTH)).fetchall()
                
                messages = []
                for row in reversed(message_rows):
                    messages.append(Message(
                        role=row['role'],
                        content=row['content'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        message_id=row['message_id']
                    ))
                
                return Conversation(
                    user_id=user_id,
                    messages=messages,
                    last_activity=last_activity,
                    message_count=message_count
                )
    
    def add_message(self, user_id: str, role: str, content: str, message_id: str = None):
        """Add a message to the database."""
        with db_lock:
            with self.get_connection() as conn:
                timestamp = datetime.now()
                
                # Insert message
                conn.execute('''
                    INSERT INTO messages (user_id, role, content, timestamp, message_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, role, content, timestamp, message_id))
                
                # Update conversation
                conn.execute('''
                    UPDATE conversations 
                    SET last_activity = ?, message_count = message_count + 1
                    WHERE user_id = ?
                ''', (timestamp, user_id))
                
                conn.commit()
    
    def cleanup_old_conversations(self, hours: int = 24):
        """Remove old inactive conversations."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with db_lock:
            with self.get_connection() as conn:
                # Get old conversation IDs
                old_convs = conn.execute(
                    'SELECT user_id FROM conversations WHERE last_activity < ?',
                    (cutoff_time,)
                ).fetchall()
                
                if old_convs:
                    user_ids = [row['user_id'] for row in old_convs]
                    placeholders = ','.join('?' * len(user_ids))
                    
                    # Delete messages and conversations
                    conn.execute(f'DELETE FROM messages WHERE user_id IN ({placeholders})', user_ids)
                    conn.execute(f'DELETE FROM conversations WHERE user_id IN ({placeholders})', user_ids)
                    conn.commit()
                    
                    logger.info(f"Cleaned up {len(old_convs)} old conversations")
                    return len(old_convs)
                
                return 0
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        with self.get_connection() as conn:
            total_conversations = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
            total_messages = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
            active_conversations = conn.execute(
                'SELECT COUNT(*) FROM conversations WHERE last_activity > ?',
                (datetime.now() - timedelta(hours=24),)
            ).fetchone()[0]
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'active_conversations_24h': active_conversations
            }

# Initialize database manager
db_manager = DatabaseManager(Config.SQLITE_DB)

def validate_config():
    """Validate that all required environment variables are set."""
    required_vars = ['VERIFY_TOKEN', 'WHATSAPP_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not getattr(Config, var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove potentially harmful characters and limit length
    sanitized = re.sub(r'[<>"\']', '', text.strip())
    return sanitized[:Config.MAX_MESSAGE_LENGTH]

def verify_webhook_signature(payload: str, signature: str) -> bool:
    """Verify webhook signature for security."""
    if not Config.APP_SECRET or not signature:
        return True  # Skip verification if not configured
    
    try:
        expected = hmac.new(
            Config.APP_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, f"sha256={expected}")
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

def is_rate_limited(user_id: str) -> bool:
    """Check if user is rate limited."""
    current_time = time.time()
    user_requests = rate_limit_tracker[user_id]
    
    # Remove requests older than 1 minute
    user_requests[:] = [req_time for req_time in user_requests 
                       if current_time - req_time < 60]
    
    # Check if user has exceeded rate limit
    if len(user_requests) >= Config.RATE_LIMIT_PER_MINUTE:
        return True
    
    # Add current request
    user_requests.append(current_time)
    return False

def get_user_friendly_error(error_type: str) -> str:
    """Return user-friendly error messages."""
    errors = {
        'rate_limit': "You're sending messages too quickly. Please wait a moment.",
        'ai_error': "I'm having trouble thinking right now. Please try again in a moment.",
        'long_message': "Your message is too long. Please break it into smaller parts.",
        'invalid_request': "I couldn't process your message. Please try again.",
        'server_error': "I'm experiencing technical difficulties. Please try again later."
    }
    return errors.get(error_type, "Something went wrong. Please try again.")

def split_long_message(message: str, max_length: int = 1600) -> List[str]:
    """Split long messages for WhatsApp compatibility."""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    while message:
        if len(message) <= max_length:
            parts.append(message)
            break
        
        # Find a good break point (prefer sentence endings, then spaces)
        break_points = ['. ', '! ', '? ', '\n', ' ']
        break_point = -1
        
        for bp in break_points:
            bp_pos = message.rfind(bp, 0, max_length)
            if bp_pos > max_length * 0.7:  # Don't break too early
                break_point = bp_pos + len(bp)
                break
        
        if break_point == -1:
            break_point = max_length
        
        parts.append(message[:break_point].strip())
        message = message[break_point:].strip()
    
    return parts

def chat_with_ai(user_id: str, user_message: str) -> str:
    """Chat with OpenAI API with conversation history."""
    try:
        # Sanitize input
        user_message = sanitize_input(user_message)
        if not user_message:
            return get_user_friendly_error('invalid_request')
        
        # Check message length
        if len(user_message) > Config.MAX_MESSAGE_LENGTH:
            return get_user_friendly_error('long_message')
        
        conversation = db_manager.get_conversation(user_id)
        
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": Config.SYSTEM_PROMPT}]
        
        # Add conversation history
        for msg in conversation.messages[-Config.MAX_CONVERSATION_LENGTH:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            timeout=Config.WEBHOOK_TIMEOUT
        )
        
        ai_response = response.choices[0].message.content
        
        # Store messages in database
        db_manager.add_message(user_id, "user", user_message)
        db_manager.add_message(user_id, "assistant", ai_response)
        
        logger.info(f"AI response generated for user {user_id}")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error in chat_with_ai for user {user_id}: {str(e)}")
        return get_user_friendly_error('ai_error')

def send_whatsapp_message(phone_number_id: str, to_number: str, message: str) -> bool:
    """Send message via WhatsApp API, handling long messages."""
    try:
        # Split long messages
        message_parts = split_long_message(message)
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Send each part
        for i, part in enumerate(message_parts):
            if i > 0:
                time.sleep(1)  # Small delay between parts
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "text": {"body": part}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=Config.WHATSAPP_TIMEOUT)
            response.raise_for_status()
        
        logger.info(f"Message sent successfully to {to_number} ({len(message_parts)} parts)")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return False

def extract_message_data(body: dict) -> Optional[dict]:
    """Extract message data from webhook body."""
    try:
        if (body.get('object') == 'whatsapp_business_account' and
            body.get('entry') and
            body['entry'][0].get('changes') and
            body['entry'][0]['changes'][0].get('value') and
            body['entry'][0]['changes'][0]['value'].get('messages') and
            body['entry'][0]['changes'][0]['value']['messages'][0]):
            
            value = body['entry'][0]['changes'][0]['value']
            message = value['messages'][0]
            
            # Only process text messages for now
            if message.get('type') != 'text':
                return None
            
            return {
                'phone_number_id': value['metadata']['phone_number_id'],
                'from_number': message['from'],
                'message_body': message['text']['body'],
                'message_id': message.get('id'),
                'timestamp': message.get('timestamp')
            }
    except (KeyError, IndexError) as e:
        logger.error(f"Error extracting message data: {str(e)}")
    
    return None

def handle_admin_command(user_id: str, command: str) -> Optional[str]:
    """Handle admin commands if user is authorized."""
    if user_id not in Config.ADMIN_USERS:
        return None
    
    parts = command.lower().split()
    if len(parts) < 2 or parts[0] != '/admin':
        return None
    
    cmd = parts[1]
    
    if cmd == 'stats':
        stats = db_manager.get_stats()
        return f"📊 Bot Statistics:\n" \
               f"Total conversations: {stats['total_conversations']}\n" \
               f"Total messages: {stats['total_messages']}\n" \
               f"Active (24h): {stats['active_conversations_24h']}"
    
    elif cmd == 'cleanup':
        cleaned = db_manager.cleanup_old_conversations(Config.CONVERSATION_TIMEOUT_HOURS)
        return f"🧹 Cleaned up {cleaned} old conversations"
    
    elif cmd == 'help':
        return "🔧 Admin Commands:\n" \
               "/admin stats - Show statistics\n" \
               "/admin cleanup - Clean old conversations\n" \
               "/admin help - Show this help"
    
    return "❓ Unknown admin command. Use '/admin help' for available commands."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp webhook."""
    try:
        # Verify webhook signature if configured
        if Config.APP_SECRET:
            signature = request.headers.get('X-Hub-Signature-256', '')
            if not verify_webhook_signature(request.get_data(as_text=True), signature):
                logger.warning("Invalid webhook signature")
                return 'Unauthorized', 401
        
        body = request.json
        logger.debug(f"Received webhook: {json.dumps(body, indent=2)}")
        
        message_data = extract_message_data(body)
        if not message_data:
            logger.debug("Invalid webhook format or no text message found")
            return '', 200
        
        user_id = message_data['from_number']
        user_message = message_data['message_body']
        
        # Check for admin commands
        admin_response = handle_admin_command(user_id, user_message)
        if admin_response:
            send_whatsapp_message(
                message_data['phone_number_id'],
                user_id,
                admin_response
            )
            return '', 200
        
        # Check rate limiting
        if is_rate_limited(user_id):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            send_whatsapp_message(
                message_data['phone_number_id'],
                user_id,
                get_user_friendly_error('rate_limit')
            )
            return '', 200
        
        # Get AI response
        ai_response = chat_with_ai(user_id, user_message)
        
        # Send response back to WhatsApp
        success = send_whatsapp_message(
            message_data['phone_number_id'],
            user_id,
            ai_response
        )
        
        if not success:
            logger.error(f"Failed to send message to user {user_id}")
        
        return '', 200
        
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}")
        return '', 500

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp setup."""
    try:
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == Config.VERIFY_TOKEN:
            logger.info("Webhook verification successful")
            return challenge, 200
        else:
            logger.warning("Invalid verify token")
            return 'Invalid Verify Token', 403
            
    except Exception as e:
        logger.error(f"Error in webhook verification: {str(e)}")
        return '', 500

@app.route('/')
def health_check():
    """Health check endpoint."""
    stats = db_manager.get_stats()
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": Config.SQLITE_DB,
        **stats
    })

@app.route('/stats')
def get_stats():
    """Get application statistics."""
    stats = db_manager.get_stats()
    return jsonify({
        **stats,
        "rate_limit_per_minute": Config.RATE_LIMIT_PER_MINUTE,
        "max_conversation_length": Config.MAX_CONVERSATION_LENGTH
    })

@app.route('/conversations/<user_id>')
def get_conversation_history(user_id: str):
    """Get conversation history for a specific user (admin only)."""
    # Simple authentication check
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != Config.ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conversation = db_manager.get_conversation(user_id)
        return jsonify({
            "user_id": user_id,
            "message_count": conversation.message_count,
            "last_activity": conversation.last_activity.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_id": msg.message_id
                }
                for msg in conversation.messages[-20:]  # Last 20 messages
            ]
        })
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/admin/cleanup', methods=['POST'])
def admin_cleanup():
    """Manual cleanup endpoint (admin only)."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != Config.ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        hours = request.json.get('hours', Config.CONVERSATION_TIMEOUT_HOURS)
        cleaned = db_manager.cleanup_old_conversations(hours)
        return jsonify({"cleaned_conversations": cleaned})
    except Exception as e:
        logger.error(f"Error in admin cleanup: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

# Cleanup task - run periodically
def schedule_cleanup():
    """Schedule periodic cleanup of old conversations."""
    import threading
    import time
    
    def cleanup_task():
        while True:
            time.sleep(3600)  # Run every hour
            try:
                db_manager.cleanup_old_conversations(Config.CONVERSATION_TIMEOUT_HOURS)
            except Exception as e:
                logger.error(f"Error in scheduled cleanup: {str(e)}")
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

if __name__ == '__main__':
    try:
        validate_config()
        logger.info("Starting WhatsApp AI Chatbot...")
        logger.info(f"Database: {Config.SQLITE_DB}")
        logger.info(f"Admin users: {len(Config.ADMIN_USERS)}")
        
        # Start cleanup scheduler
        schedule_cleanup()
        
        app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        exit(1)