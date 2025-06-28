"""
Enhanced configuration settings for the WhatsApp AI Chatbot.
All settings can be overridden using environment variables.
"""

import os
from typing import Optional, List

class Config:
    """Application configuration."""
    
    # Required environment variables
    VERIFY_TOKEN: str = os.getenv('VERIFY_TOKEN', '')
    WHATSAPP_TOKEN: str = os.getenv('WHATSAPP_TOKEN', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Security settings
    APP_SECRET: str = os.getenv('APP_SECRET', '')  # For webhook verification
    ADMIN_TOKEN: str = os.getenv('ADMIN_TOKEN', 'admin_secret_token_change_me')
    
    # Admin users (phone numbers that can use admin commands)
    ADMIN_USERS: List[str] = [
        user.strip() for user in os.getenv('ADMIN_USERS', '').split(',') 
        if user.strip()
    ]
    
    # Database settings
    SQLITE_DB: str = os.getenv('SQLITE_DB', 'conversations.db')
    
    # OpenAI settings
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE: float = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Message and conversation settings
    MAX_CONVERSATION_LENGTH: int = int(os.getenv('MAX_CONVERSATION_LENGTH', '10'))
    MAX_MESSAGE_LENGTH: int = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '30'))
    CONVERSATION_TIMEOUT_HOURS: int = int(os.getenv('CONVERSATION_TIMEOUT_HOURS', '24'))
    
    # Timeout settings
    WEBHOOK_TIMEOUT: int = int(os.getenv('WEBHOOK_TIMEOUT', '30'))
    WHATSAPP_TIMEOUT: int = int(os.getenv('WHATSAPP_TIMEOUT', '30'))
    
    # Server settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '5000'))
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'whatsapp_ai.log')
    
    # Feature flags
    ENABLE_ANALYTICS: bool = os.getenv('ENABLE_ANALYTICS', 'False').lower() == 'true'
    ENABLE_WEBHOOK_VERIFICATION: bool = os.getenv('ENABLE_WEBHOOK_VERIFICATION', 'True').lower() == 'true'
    
    # System prompt
    SYSTEM_PROMPT: str = os.getenv('SYSTEM_PROMPT', 
        """You are a helpful AI assistant integrated with WhatsApp. 
        Please provide clear, concise, and helpful responses. 
        Keep responses under 1000 characters when possible for better WhatsApp compatibility.
        Be friendly and professional in your tone.
        
        If a user asks for very long content, break it into digestible parts.
        You can handle various topics but always maintain a helpful and respectful attitude.""")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    ENABLE_WEBHOOK_VERIFICATION = False  # Easier for development
    CONVERSATION_TIMEOUT_HOURS = 1  # Shorter timeout for testing

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    ENABLE_WEBHOOK_VERIFICATION = True
    
    # Production should have these set
    @property
    def APP_SECRET(self):
        secret = os.getenv('APP_SECRET', '')
        if not secret:
            raise ValueError("APP_SECRET must be set in production")
        return secret
    
    @property
    def ADMIN_TOKEN(self):
        token = os.getenv('ADMIN_TOKEN', '')
        if not token or token == 'admin_secret_token_change_me':
            raise ValueError("ADMIN_TOKEN must be set to a secure value in production")
        return token

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    SQLITE_DB = ':memory:'  # Use in-memory database for tests
    RATE_LIMIT_PER_MINUTE = 1000  # No rate limiting in tests
    ENABLE_WEBHOOK_VERIFICATION = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration based on environment."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])