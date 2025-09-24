# OnPalms Chatbot API

A RAG-based chatbot API for OnPalms warehouse management system that fetches content from WordPress and provides intelligent responses.

## Features

- 🤖 **AI-Powered Chat**: Uses OpenAI GPT-3.5 for intelligent responses
- 🔍 **RAG System**: Retrieves relevant content from OnPalms WordPress site
- 📧 **Lead Capture**: Validates and stores business leads
- 🌐 **CORS Enabled**: Works with any frontend
- 🚀 **Cloud Ready**: Optimized for Render, Heroku, and AWS deployment

## API Endpoints

### `POST /chat`
Send a message to the chatbot.

**Request:**
```json
{
    "message": "What is PALMS?"
}
```

**Response:**
```json
{
    "response": "PALMS™ is a comprehensive warehouse management system...",
    "show_demo_popup": false,
    "show_options": true
}
```

### `POST /save_lead`
Save a lead's contact information.

**Request:**
```json
{
    "name": "John Doe",
    "email": "john@company.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Thank you! Our sales team will contact you soon."
}
```

### `GET /health`
Health check endpoint.

## Environment Variables

Set these environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
PORT=5000
DEBUG=False
```

## Quick Deploy to Render

1. **Fork this repository**
2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repo
3. **Configure:**
   - Build Command: `pip install -r requirements_simple.txt`
   - Start Command: `gunicorn app_simple:app --bind 0.0.0.0:$PORT`
   - Add environment variable: `OPENAI_API_KEY`
4. **Deploy!**

## Local Development

```bash
# Install dependencies
pip install -r requirements_simple.txt

# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Run the app
python app_simple.py
```

## Integration with WordPress

The chatbot is designed to work with the existing footer.php. Just update the API URL:

```javascript
window.palmsConfig = {
    // ... other config
    apiUrl: 'https://your-render-app.onrender.com'
};
```

## Project Structure

```
├── app_simple.py          # Main Flask application
├── chat.py                # Chat logic and AI responses
├── simple_retriever.py    # Content fetching from WordPress
├── requirements_simple.txt # Python dependencies
├── Procfile               # For Heroku/Render deployment
├── runtime.txt            # Python version specification
└── README_DEPLOY.md       # This file
```

## How It Works

1. **Content Fetching**: Automatically fetches pages and posts from OnPalms WordPress API
2. **Simple Search**: Uses keyword matching to find relevant content
3. **AI Processing**: Sends relevant context to OpenAI GPT-3.5 for intelligent responses
4. **Lead Management**: Validates business emails and stores leads in CSV file

## Support

For questions or issues, contact the development team or create an issue in this repository.
