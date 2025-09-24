# 🚀 OnPalms Chatbot - Render Deployment Guide

## ✅ Ready for Deployment!

Your chatbot API is now ready to deploy on Render. Here's what you need to do:

### 1. Push to GitHub

First, push your code to GitHub:

```bash
# If you haven't set up GitHub remote yet:
git remote add origin https://github.com/YOUR_USERNAME/onpalms-chatbot.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub** repository
4. **Configure the service:**
   - **Name**: `onpalms-chatbot-api`
   - **Branch**: `main`
   - **Root Directory**: leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements_simple.txt`
   - **Start Command**: `gunicorn app_simple:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

5. **Add Environment Variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DEBUG`: `False`

6. **Click "Create Web Service"**

### 3. Update Your WordPress Frontend

Once deployed, you'll get a URL like: `https://onpalms-chatbot-api.onrender.com`

Update your `footer.php` file:

```javascript
window.palmsConfig = {
    ajaxUrl: '<?php echo admin_url('admin-ajax.php'); ?>',
    nonce: '<?php echo wp_create_nonce('palms_chat_nonce'); ?>',
    apiUrl: 'https://your-render-app.onrender.com'  // Replace with your actual URL
};
```

### 4. Test Your Deployment

Test these endpoints:

- **Health Check**: `GET https://your-app.onrender.com/health`
- **Chat**: `POST https://your-app.onrender.com/chat`
- **Save Lead**: `POST https://your-app.onrender.com/save_lead`

## 📁 Files Included for Deployment

- ✅ `app_simple.py` - Main Flask application (clean, no extra dependencies)
- ✅ `chat.py` - Chat logic with OpenAI integration
- ✅ `simple_retriever.py` - WordPress content fetching (no vector DB)
- ✅ `requirements_simple.txt` - Minimal, Render-compatible dependencies
- ✅ `Procfile` - Render deployment configuration
- ✅ `runtime.txt` - Python version specification
- ✅ `.gitignore` - Clean git ignore file

## 🔧 Key Features

- **No problematic dependencies** (no flask_limiter, chromadb, etc.)
- **Simple RAG system** using keyword search instead of vector embeddings
- **Lead capture** with business email validation
- **CORS enabled** for WordPress integration
- **Error handling** with fallback responses
- **Health checks** for monitoring

## 💡 Post-Deployment Notes

1. **First load might be slow** (Render cold start) - this is normal
2. **WordPress content is cached** for 1 hour to reduce API calls
3. **Leads are saved to CSV** in the container (consider adding database later)
4. **Monitor logs** in Render dashboard for any issues

## 🎯 Your API Endpoints

Once deployed, your API will be available at:

- `GET /` - API information and health
- `GET /health` - Simple health check
- `POST /chat` - Main chat endpoint
- `POST /save_lead` - Lead capture endpoint

## 🔑 Environment Variables Needed

Make sure to set these in Render:

```
OPENAI_API_KEY=sk-proj-your-openai-key-here
DEBUG=False
```

## 🚨 Troubleshooting

If deployment fails:

1. **Check build logs** in Render dashboard
2. **Verify all files** are committed to GitHub
3. **Double-check** requirements_simple.txt has no typos
4. **Make sure** OPENAI_API_KEY is set correctly

## ✨ You're All Set!

Once deployed, just update the `apiUrl` in your WordPress footer.php and your chatbot will be live! 🎉
