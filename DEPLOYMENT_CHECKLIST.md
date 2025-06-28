# ✅ Deployment Checklist

Use this checklist to ensure you have everything ready for deploying your WhatsApp AI Chatbot to Render.

## 📋 Pre-Deployment Checklist

### ✅ Code Repository
- [ ] Code is pushed to GitHub repository
- [ ] All files are committed and pushed
- [ ] Repository is public or connected to Render

### ✅ Required Files
- [ ] `server.py` - Main application
- [ ] `requirements.txt` - Python dependencies
- [ ] `render.yaml` - Render configuration
- [ ] `README.md` - Documentation

### ✅ Environment Variables Ready
- [ ] `VERIFY_TOKEN` - Your webhook verification token
- [ ] `WHATSAPP_TOKEN` - WhatsApp Business API token
- [ ] `OPENAI_API_KEY` - OpenAI API key

### ✅ Meta Developers Setup
- [ ] Meta Developers account created
- [ ] WhatsApp Business app created
- [ ] Phone number verified
- [ ] Temporary access token obtained

### ✅ OpenAI Setup
- [ ] OpenAI account created
- [ ] API key generated
- [ ] API key has sufficient credits

## 🚀 Render Deployment Steps

### ✅ Step 1: Render Account
- [ ] Sign up at [render.com](https://render.com)
- [ ] Connect GitHub account
- [ ] Verify email address

### ✅ Step 2: Deploy Application
- [ ] Click "New +" in Render dashboard
- [ ] Select "Blueprint" (if using render.yaml)
- [ ] Connect your GitHub repository
- [ ] Wait for automatic deployment

### ✅ Step 3: Configure Environment Variables
- [ ] Go to your service in Render dashboard
- [ ] Navigate to "Environment" tab
- [ ] Add required environment variables:
  - [ ] `VERIFY_TOKEN`
  - [ ] `WHATSAPP_TOKEN`
  - [ ] `OPENAI_API_KEY`
- [ ] Save environment variables

### ✅ Step 4: Get Your URL
- [ ] Note your Render service URL
- [ ] Your webhook URL will be: `https://your-app.onrender.com/webhook`

### ✅ Step 5: Configure WhatsApp Webhook
- [ ] Go to Meta Developers dashboard
- [ ] Navigate to your WhatsApp Business app
- [ ] Go to "Webhooks" section
- [ ] Set webhook URL: `https://your-app.onrender.com/webhook`
- [ ] Set verify token (same as your `VERIFY_TOKEN`)
- [ ] Subscribe to `messages` field
- [ ] Test webhook verification

## 🧪 Post-Deployment Testing

### ✅ Health Check
- [ ] Visit: `https://your-app.onrender.com/`
- [ ] Should return: `{"status": "healthy", ...}`

### ✅ Webhook Verification Test
- [ ] Run: `python test_webhook.py`
- [ ] Or manually test webhook verification
- [ ] Should return challenge response

### ✅ WhatsApp Integration Test
- [ ] Send a message to your WhatsApp number
- [ ] Verify AI responds correctly
- [ ] Check conversation history endpoint

### ✅ Monitoring Setup
- [ ] Check Render logs for any errors
- [ ] Monitor application statistics: `https://your-app.onrender.com/stats`
- [ ] Set up health check pings (optional)

## 🔧 Troubleshooting Checklist

### ✅ If Build Fails
- [ ] Check `requirements.txt` has all dependencies
- [ ] Verify Python version compatibility
- [ ] Check build logs in Render dashboard

### ✅ If Service Won't Start
- [ ] Verify `startCommand` is correct: `python server.py`
- [ ] Check all environment variables are set
- [ ] Review logs in Render dashboard

### ✅ If Webhook Not Working
- [ ] Verify webhook URL is correct
- [ ] Check `VERIFY_TOKEN` matches Meta app
- [ ] Ensure service is not sleeping (free plan)

### ✅ If AI Not Responding
- [ ] Verify `OPENAI_API_KEY` is valid
- [ ] Check OpenAI API quota and billing
- [ ] Test OpenAI API separately

## 📊 Production Considerations

### ✅ For Free Plan
- [ ] Service will sleep after 15 minutes of inactivity
- [ ] First request after sleep may take 30-60 seconds
- [ ] Consider setting up health check pings

### ✅ For Paid Plan
- [ ] No sleep mode
- [ ] Faster cold starts
- [ ] More resources available

### ✅ Monitoring
- [ ] Set up external monitoring (UptimeRobot, Pingdom)
- [ ] Monitor Render dashboard regularly
- [ ] Check application logs periodically

## 🎉 Success Indicators

Your deployment is successful when:
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Webhook verification works
- [ ] WhatsApp messages receive AI responses
- [ ] No errors in Render logs
- [ ] Application statistics are tracking correctly

---

**Need Help?**
- Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions
- Review Render documentation: [docs.render.com](https://docs.render.com)
- Check application logs in Render dashboard 