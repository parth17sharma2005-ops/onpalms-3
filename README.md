# OnPalms Chatbot Backend

A production-ready RAG-powered chatbot backend that learns from WordPress content and captures leads.

## Features

- 🤖 **RAG System**: Retrieves and uses content from WordPress REST API
- 💾 **Lead Storage**: Saves leads to CSV and Google Sheets
- 🔍 **Vector Search**: ChromaDB for semantic content retrieval
- 🚀 **AWS Ready**: Docker containerization for easy deployment
- 📊 **Admin Panel**: API endpoints for lead management
- 🔒 **Business Email Validation**: Filters personal email domains

## Quick Start

### 1. Environment Setup

```bash
# Copy environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
```bash
OPENAI_API_KEY=sk-proj-your-openai-key
ADMIN_KEY=your-secret-admin-key
```

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the RAG system
python retriever.py

# Run the application
python main.py
```

### 3. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t onpalms-chatbot .
docker run -p 5000:5000 --env-file .env onpalms-chatbot
```

## API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "What is PALMS warehouse management?"
}
```

### Save Lead
```http
POST /save_lead
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@company.com"
}
```

### Admin - View Leads
```http
GET /admin/leads
X-Admin-Key: your-secret-admin-key
```

### Admin - Refresh Knowledge Base
```http
POST /admin/refresh
X-Admin-Key: your-secret-admin-key
```

## AWS Deployment

### Option 1: AWS App Runner

1. Push your code to GitHub
2. Create an App Runner service
3. Connect to your repository
4. Set environment variables
5. Deploy

### Option 2: AWS ECS with Fargate

1. Push Docker image to ECR
2. Create ECS cluster
3. Define task definition
4. Create service

### Option 3: AWS Elastic Beanstalk

1. Install EB CLI
2. Initialize: `eb init`
3. Deploy: `eb create production`

## Google Sheets Integration (Optional)

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create service account credentials
4. Download `google_sheets_credentials.json`
5. Create a Google Sheet named "OnPalms Chatbot Leads"
6. Share the sheet with your service account email

## Customization

### Update WordPress URLs
Edit `retriever.py`:
```python
base_urls = [
    "https://your-site.com/wp-json/wp/v2/pages?per_page=100",
    "https://your-site.com/wp-json/wp/v2/posts?per_page=100"
]
```

### Modify AI Persona
Edit `chat_engine.py` system prompt to match your brand voice.

### Add More Data Sources
Extend `retriever.py` to fetch from additional APIs or databases.

## Monitoring

- Health check: `GET /health`
- Logs: Check application logs for errors
- Lead tracking: Monitor CSV file or Google Sheets

## Frontend Integration

Update your `footer.php` API URL:

```javascript
window.palmsConfig = {
    apiUrl: 'https://your-deployed-api.com'
};
```

## Troubleshooting

### Common Issues

1. **Import errors**: Install requirements: `pip install -r requirements.txt`
2. **OpenAI errors**: Check API key in `.env` file
3. **WordPress fetch fails**: Verify URLs and site accessibility
4. **Google Sheets errors**: Check credentials file and sheet permissions

### Debug Mode

Run with debug enabled:
```bash
export DEBUG=true
python main.py
```

## Production Considerations

- Set up proper logging
- Configure CORS for your domain only
- Use environment variables for secrets
- Set up database backup for leads
- Monitor API rate limits
- Implement request rate limiting
- Add SSL/TLS termination

## Support

For issues or questions, check the logs first:
```bash
# Docker logs
docker-compose logs -f chatbot

# Local logs
tail -f app.log
```
