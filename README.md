# 🤖 WhatsApp AI Chatbot

A robust and feature-rich WhatsApp chatbot powered by OpenAI's GPT models. This application provides a seamless integration between WhatsApp Business API and OpenAI's conversational AI, with advanced features like conversation history, rate limiting, and comprehensive logging.

## ✨ Features

- **🤖 AI-Powered Conversations**: Powered by OpenAI's GPT models (GPT-3.5-turbo, GPT-4, etc.)
- **💬 Conversation Memory**: Maintains conversation history for context-aware responses
- **⚡ Rate Limiting**: Prevents spam and abuse with configurable rate limits
- **📊 Monitoring & Analytics**: Built-in endpoints for health checks and statistics
- **🔒 Error Handling**: Comprehensive error handling and logging
- **⚙️ Configurable**: Highly configurable through environment variables
- **📝 Logging**: Detailed logging for debugging and monitoring
- **🚀 Production Ready**: Includes production-ready configurations

## 🚀 Quick Start

### Prerequisites

- [Meta Developers Account](https://developers.facebook.com/)
- [OpenAI API Key](https://platform.openai.com/account/api-keys)
- Python 3.8+

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ChatGPT-with-WhatsApp.git
   cd ChatGPT-with-WhatsApp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

4. **Run the application:**
   ```bash
   python server.py
   ```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VERIFY_TOKEN` | Token for webhook verification | `my_verify_token_123` |
| `WHATSAPP_TOKEN` | WhatsApp Business API token | `EAA...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `MAX_TOKENS` | `1000` | Maximum tokens for AI responses |
| `TEMPERATURE` | `0.7` | AI response creativity (0-1) |
| `MAX_CONVERSATION_LENGTH` | `10` | Max conversation history length |
| `RATE_LIMIT_PER_MINUTE` | `30` | Messages per minute per user |
| `WEBHOOK_TIMEOUT` | `30` | Webhook timeout in seconds |
| `PORT` | `5000` | Server port |
| `DEBUG` | `False` | Enable debug mode |

## 📱 WhatsApp Business API Setup

### 1. Create Meta Developers Account
- Go to [Meta Developers](https://developers.facebook.com/)
- Create a new business app

### 2. Add WhatsApp Product
- Add the `whatsapp` product to your app
- Get your temporary access token (`WHATSAPP_TOKEN`)

### 3. Verify Phone Number
- Add and verify your recipient phone number

### 4. Configure Webhook
- Set webhook URL: `https://your-domain.com/webhook`
- Set verify token (same as `VERIFY_TOKEN` in your .env)
- Subscribe to `messages` field

### 5. Deploy Your Application
- Deploy to your preferred hosting platform (Heroku, Railway, etc.)
- Set environment variables on your hosting platform
- Update webhook URL with your deployed domain

## 🛠️ API Endpoints

### Webhook Endpoints
- `POST /webhook` - Receives WhatsApp messages
- `GET /webhook` - Webhook verification

### Monitoring Endpoints
- `GET /` - Health check
- `GET /stats` - Application statistics
- `GET /conversations/<user_id>` - Get conversation history

### Example API Responses

**Health Check:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "active_conversations": 5
}
```

**Statistics:**
```json
{
  "active_conversations": 5,
  "total_messages_processed": 150,
  "rate_limit_per_minute": 30
}
```

## 📊 Monitoring & Logging

The application includes comprehensive logging and monitoring:

- **File Logging**: All logs are saved to `whatsapp_ai.log`
- **Console Logging**: Real-time logs in console
- **Health Checks**: Built-in health check endpoint
- **Statistics**: Track conversations and message counts
- **Error Tracking**: Detailed error logging with stack traces

## 🔒 Security Features

- **Rate Limiting**: Prevents abuse with configurable limits
- **Input Validation**: Validates all incoming webhook data
- **Error Handling**: Graceful error handling without exposing sensitive data
- **Environment Variables**: Secure configuration management

## 🚀 Deployment

### Render (Recommended for Free Hosting)
```bash
# 1. Push your code to GitHub
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Deploy on Render
# - Go to render.com and sign up
# - Connect your GitHub repository
# - Use the render.yaml file for automatic configuration
# - Set environment variables in Render dashboard
```

**Quick Deploy with render.yaml:**
1. Connect your GitHub repository to Render
2. Select "Blueprint" deployment
3. Render will automatically detect `render.yaml`
4. Set required environment variables:
   - `VERIFY_TOKEN`
   - `WHATSAPP_TOKEN` 
   - `OPENAI_API_KEY`

**Manual Deploy:**
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python server.py`
- Port: `10000` (Render default)

📖 **Detailed Render Guide**: See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

### Heroku
```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set VERIFY_TOKEN=your_token
heroku config:set WHATSAPP_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key

# Deploy
git push heroku main
```

### Railway
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "server.py"]
```

**Docker Compose:**
```bash
docker-compose up -d
```

## 🧪 Testing

Run the application in development mode:
```bash
export FLASK_ENV=development
python server.py
```

Test webhook verification:
```bash
curl "http://localhost:5000/webhook?hub.verify_token=your_token&hub.challenge=test"
```

## 📈 Performance Optimization

- **Conversation Trimming**: Automatically trims old messages to prevent memory issues
- **Rate Limiting**: Prevents API abuse and reduces costs
- **Timeout Handling**: Configurable timeouts for external API calls
- **Memory Management**: Efficient data structures for conversation storage

## 🔧 Troubleshooting

### Common Issues

1. **Webhook verification fails**
   - Check that `VERIFY_TOKEN` matches your Meta app settings
   - Ensure webhook URL is accessible

2. **Messages not being sent**
   - Verify `WHATSAPP_TOKEN` is valid and not expired
   - Check phone number is verified in Meta app

3. **AI responses not working**
   - Verify `OPENAI_API_KEY` is valid
   - Check OpenAI API quota and billing

4. **Rate limiting issues**
   - Adjust `RATE_LIMIT_PER_MINUTE` in environment variables
   - Check logs for rate limit warnings

### Debug Mode
Enable debug mode for detailed logging:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python server.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the AI capabilities
- Meta for the WhatsApp Business API
- Flask community for the web framework

---

**Note**: This is an improved version of the original WhatsApp AI chatbot with enhanced features, better error handling, and production-ready configurations.

# Screenshot

![WhatsApp Image 2023-11-30 at 01 06 33](https://github.com/shrey141102/ChatGPT-with-WhatsApp/assets/90243443/1d9fec5b-3229-4fe0-ace0-405b01768e10)

