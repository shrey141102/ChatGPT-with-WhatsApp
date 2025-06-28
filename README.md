# 🤖 WhatsApp AI Chatbot with Memory & Vision

A simple, powerful WhatsApp chatbot powered by OpenAI's GPT-4o-mini with persistent memory and image analysis capabilities. Built for personal use with minimal setup and maximum functionality.

## ✨ Features

- **🤖 AI-Powered Conversations**: Powered by OpenAI's GPT-4o-mini for cost-effective, smart responses
- **🧠 Persistent Memory**: Remembers conversations across sessions using Mem0 cloud storage
- **📷 Image Analysis**: Analyze and describe images sent via WhatsApp using GPT-4o Vision
- **💬 Context-Aware**: References previous conversations naturally
- **📱 Personal Bot**: Optimized for personal use with simple setup
- **📝 Comprehensive Logging**: Detailed logs for all messages, memory operations, and AI responses
- **🚀 Deploy-Ready**: Simple deployment to Render with minimal configuration

## 🚀 Quick Start

### Prerequisites

- [Meta Developers Account](https://developers.facebook.com/)
- [OpenAI API Key](https://platform.openai.com/account/api-keys)
- [Mem0 API Key](https://mem0.ai/)
- Python 3.11+

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
   # Create .env file with these 4 variables:
   VERIFY_TOKEN=your_verify_token_here
   WHATSAPP_TOKEN=your_whatsapp_access_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   MEM0_API_KEY=your_mem0_api_key_here
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Required Environment Variables (Only 4!)

| Variable | Description | Example |
|----------|-------------|---------|
| `VERIFY_TOKEN` | Token for webhook verification | `my_verify_token_123` |
| `WHATSAPP_TOKEN` | WhatsApp Business API token | `EAA...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `MEM0_API_KEY` | Mem0 API key for memory storage | `mem0-...` |

That's it! No complex configuration needed.

## 📱 WhatsApp Business API Setup

### 1. Create Meta Developers Account
- Go to [Meta Developers](https://developers.facebook.com/)
- Create a new business app

### 2. Add WhatsApp Product
- Add the `whatsapp` product to your app
- Get your permanent access token (`WHATSAPP_TOKEN`)

### 3. Verify Phone Number
- Add and verify your phone number in the app

### 4. Configure Webhook
- Set webhook URL: `https://your-app-name.onrender.com/webhook`
- Set verify token (same as `VERIFY_TOKEN` in your .env)
- Subscribe to `messages` field

### 5. Deploy to Render
- Push code to GitHub
- Connect repository to Render
- Set the 4 environment variables
- Deploy!

## 🧠 Memory System

The bot uses **Mem0** for intelligent memory management:

```
User: "Hi, I'm vegetarian and allergic to nuts"
Bot: "Hello! I'll remember that you're vegetarian with a nut allergy 😊"

[Later in a different session...]
User: "What should I cook for dinner?"
Bot: "Since you're vegetarian and have a nut allergy, here are some safe dinner ideas..."
```

### Memory Features:
- **Persistent**: Remembers across sessions and deployments
- **Contextual**: Automatically retrieves relevant past conversations
- **Smart**: AI-powered memory search and retrieval
- **Automatic**: No manual memory management needed

## 📷 Image Analysis

Send any image to get AI-powered analysis:

```
User: [Sends photo of food]
Bot: "I can see a delicious pasta dish! 🍝 It looks like spaghetti with marinara sauce and fresh basil..."

User: [Sends screenshot with caption "What does this error mean?"]
Bot: "I can see the error message says... This usually means..."
```

### Supported Image Types:
- ✅ **JPG, PNG, WebP**
- ✅ **Images with captions**
- ✅ **Screenshots and photos**
- ❌ Videos, audio, documents (friendly error message)

## 🛠️ API Endpoints

### Webhook Endpoints
- `POST /webhook` - Receives WhatsApp messages
- `GET /webhook` - Webhook verification

### Monitoring Endpoints
- `GET /` - Health check with features list
- `GET /stats` - Simple application statistics

### Example Responses

**Health Check:**
```json
{
  "status": "healthy",
  "service": "WhatsApp AI Bot",
  "memory": "Mem0",
  "features": ["text_chat", "image_analysis"]
}
```

## 📊 Logging

Comprehensive logging for everything:
```
📩 User +1234567890: Hello there!
🧠 Retrieved context for +1234567890: User is vegetarian...
🤖 AI Response to +1234567890: Hi! Good to hear from you again 😊
💾 Memory stored for +1234567890: True

📷 Downloaded image: 25000 characters, type: image/jpeg
🔍 Analyzing image for +1234567890 with caption: 'What is this?'
🤖 Image analysis for +1234567890: I can see a beautiful sunset...
💾 Image memory stored for +1234567890: True
```

## 🚀 Deployment to Render

### One-Click Deploy
1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy WhatsApp AI Bot"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) and sign up
   - Click "New Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

3. **Set Environment Variables:**
   ```
   VERIFY_TOKEN=your_token
   WHATSAPP_TOKEN=your_token  
   OPENAI_API_KEY=your_key
   MEM0_API_KEY=your_key
   ```

4. **Get Your Webhook URL:**
   - Your bot will be available at: `https://your-app-name.onrender.com/webhook`
   - Use this URL in your WhatsApp Business API webhook configuration

### Manual Deployment Commands
```bash
# Build Command
pip install -r requirements.txt

# Start Command  
gunicorn --bind 0.0.0.0:$PORT app:app
```

**Total code: ~165 lines** - Simple and maintainable!

## 💡 Usage Examples

### Text Conversations
```
User: "I love cooking Italian food"
Bot: "That's great! I'll remember you enjoy Italian cuisine 😊"

User: "What should I make tonight?"
Bot: "Since you love Italian food, how about some homemade pasta with..."
```

### Image Analysis
```
User: [Sends recipe photo]
Bot: "I can see a recipe for chocolate chip cookies! 🍪 The ingredients listed are..."

User: [Sends plant photo] "What kind of plant is this?"
Bot: "This looks like a succulent, specifically an Echeveria! 🌱"
```

## 🔧 Troubleshooting

### Common Issues

1. **Webhook verification fails**
   - Check `VERIFY_TOKEN` matches Meta app settings
   - Ensure webhook URL is accessible: `https://your-app.onrender.com/webhook`

2. **Messages not being received**
   - Verify `WHATSAPP_TOKEN` is permanent token (not temporary)
   - Check phone number is verified in Meta app

3. **AI not responding**
   - Verify `OPENAI_API_KEY` is valid with sufficient credits
   - Check Render logs for detailed error messages

4. **Memory not working**
   - Verify `MEM0_API_KEY` is valid
   - Check Render logs for memory operation status

### Debug Tips
```bash
# Check Render logs for detailed information
# Look for these log patterns:
📩 📷 🧠 🤖 💾 ✅ ❌
```

## 🎯 Why This Bot?

- **🎯 Simple**: Only 4 environment variables, minimal setup
- **🧠 Smart**: Remembers everything using advanced AI memory
- **👁️ Visual**: Can see and understand images  
- **💰 Cost-Effective**: Uses GPT-4o-mini for optimal price/performance
- **🚀 Reliable**: Cloud-based memory, production-ready
- **📱 Personal**: Perfect for personal WhatsApp automation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Keep changes simple and focused
4. Submit a pull request

## 📄 License

MIT License - feel free to use for personal projects!

---

**🎉 Ready to deploy your personal AI assistant to WhatsApp in under 10 minutes!**

# Screenshot

![WhatsApp AI Bot with Memory and Vision](https://github.com/shrey141102/ChatGPT-with-WhatsApp/assets/90243443/1d9fec5b-3229-4fe0-ace0-405b01768e10)

*Example: The bot remembering user preferences and analyzing images contextually*


