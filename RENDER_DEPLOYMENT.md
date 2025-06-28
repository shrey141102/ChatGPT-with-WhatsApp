# 🚀 Deploy to Render

This guide will walk you through deploying your WhatsApp AI Chatbot to Render, a modern cloud platform that offers free hosting for web services.

## 📋 Prerequisites

Before deploying, make sure you have:

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Meta Developers Account**: For WhatsApp Business API
4. **OpenAI API Key**: For AI responses

## 🔧 Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your repository contains these files:
- `server.py` - Main application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration (optional but recommended)
- `README.md` - Documentation

### 2. Create a Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Verify your email address

### 3. Deploy Your Application

#### Option A: Using render.yaml (Recommended)

1. **Connect Repository**:
   - In Render dashboard, click "New +"
   - Select "Blueprint" (if you have render.yaml)
   - Connect your GitHub repository
   - Render will automatically detect the render.yaml file

2. **Configure Environment Variables**:
   - After the blueprint is created, go to your service
   - Navigate to "Environment" tab
   - Add these required variables:
     ```
     VERIFY_TOKEN=your_verify_token_here
     WHATSAPP_TOKEN=your_whatsapp_token_here
     OPENAI_API_KEY=your_openai_api_key_here
     ```

#### Option B: Manual Deployment

1. **Create Web Service**:
   - In Render dashboard, click "New +"
   - Select "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `whatsapp-ai-chatbot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Plan**: Free (or choose paid plan for better performance)

3. **Set Environment Variables**:
   - Click "Environment" tab
   - Add these variables:

   | Variable | Value | Description |
   |----------|-------|-------------|
   | `VERIFY_TOKEN` | `your_verify_token` | Your webhook verification token |
   | `WHATSAPP_TOKEN` | `your_whatsapp_token` | WhatsApp Business API token |
   | `OPENAI_API_KEY` | `your_openai_api_key` | OpenAI API key |
   | `OPENAI_MODEL` | `gpt-3.5-turbo` | AI model to use |
   | `MAX_TOKENS` | `1000` | Max tokens per response |
   | `TEMPERATURE` | `0.7` | AI creativity level |
   | `RATE_LIMIT_PER_MINUTE` | `30` | Rate limit per user |
   | `PORT` | `10000` | Port (Render uses 10000) |
   | `DEBUG` | `False` | Debug mode |
   | `LOG_LEVEL` | `INFO` | Logging level |

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### 4. Get Your Webhook URL

After deployment, Render will provide you with a URL like:
```
https://your-app-name.onrender.com
```

Your webhook URL will be:
```
https://your-app-name.onrender.com/webhook
```

### 5. Configure WhatsApp Business API

1. **Go to Meta Developers**:
   - Visit [developers.facebook.com](https://developers.facebook.com)
   - Navigate to your WhatsApp Business app

2. **Configure Webhook**:
   - Go to "Webhooks" section
   - Set webhook URL: `https://your-app-name.onrender.com/webhook`
   - Set verify token: (same as your `VERIFY_TOKEN`)
   - Subscribe to `messages` field

3. **Test Webhook**:
   - Use the test script: `python test_webhook.py`
   - Or manually test: `https://your-app-name.onrender.com/`

## 🔍 Testing Your Deployment

### 1. Health Check
Visit your app URL to check if it's running:
```
https://your-app-name.onrender.com/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "active_conversations": 0
}
```

### 2. Test Webhook Verification
```bash
curl "https://your-app-name.onrender.com/webhook?hub.verify_token=your_token&hub.challenge=test"
```

### 3. Check Statistics
```
https://your-app-name.onrender.com/stats
```

## ⚙️ Render-Specific Configuration

### Free Plan Limitations
- **Sleep Mode**: Free services sleep after 15 minutes of inactivity
- **Cold Start**: First request after sleep may take 30-60 seconds
- **Bandwidth**: Limited bandwidth on free plan
- **Build Time**: Limited build time

### Recommended Settings for Production
```yaml
# In render.yaml or environment variables
RATE_LIMIT_PER_MINUTE: 20  # Lower for free plan
MAX_TOKENS: 800  # Lower to reduce costs
WEBHOOK_TIMEOUT: 25  # Lower timeout
```

### Environment Variables for Production
```bash
# Performance
PORT=10000
DEBUG=False
LOG_LEVEL=WARNING

# Cost Optimization
MAX_TOKENS=800
TEMPERATURE=0.7
RATE_LIMIT_PER_MINUTE=20

# Reliability
WEBHOOK_TIMEOUT=25
MAX_CONVERSATION_LENGTH=8
```

## 🔧 Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility
   - Check build logs in Render dashboard

2. **Service Won't Start**:
   - Verify `startCommand` is correct
   - Check environment variables are set
   - Review logs in Render dashboard

3. **Webhook Not Working**:
   - Verify webhook URL is correct
   - Check `VERIFY_TOKEN` matches Meta app
   - Ensure service is not sleeping (free plan)

4. **Cold Start Issues**:
   - Consider upgrading to paid plan
   - Implement health check pings
   - Use external monitoring service

### Debug Mode
To enable debug mode temporarily:
1. Go to your service in Render dashboard
2. Navigate to "Environment" tab
3. Set `DEBUG=True`
4. Redeploy the service

### Viewing Logs
1. Go to your service in Render dashboard
2. Click "Logs" tab
3. View real-time logs and errors

## 📊 Monitoring

### Built-in Endpoints
- **Health Check**: `GET /`
- **Statistics**: `GET /stats`
- **Conversation History**: `GET /conversations/<user_id>`

### External Monitoring
Consider setting up external monitoring to keep your free service awake:
- UptimeRobot
- Pingdom
- Health checks every 10-15 minutes

## 💰 Cost Optimization

### Free Plan Tips
1. **Reduce API Calls**: Lower rate limits
2. **Optimize Responses**: Reduce max tokens
3. **Efficient Logging**: Use WARNING level in production
4. **Monitor Usage**: Check Render dashboard regularly

### Paid Plan Benefits
- No sleep mode
- Faster cold starts
- More resources
- Custom domains
- SSL certificates

## 🔄 Continuous Deployment

Render automatically deploys when you push to your main branch:
1. Push changes to GitHub
2. Render detects changes
3. Automatically rebuilds and deploys
4. Zero downtime deployment

## 📞 Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Render Community**: [community.render.com](https://community.render.com)
- **GitHub Issues**: For application-specific issues

---

**Note**: The free plan on Render is great for testing and small-scale deployments. For production use with many users, consider upgrading to a paid plan for better performance and reliability. 