"""
Utility functions and classes for PALMS Chatbot
"""
import os
import re
import csv
import json
import uuid
import logging
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from flask import request, jsonify

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utilities"""
    
    @staticmethod
    def sanitize_input(text):
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', str(text))
        # Limit length
        return text.strip()[:1000]
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_business_email(email):
        """Check if email is from a business domain"""
        if not email:
            return False
            
        # Common personal email domains to reject
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'live.com', 'msn.com',
            'ymail.com', 'protonmail.com', 'mail.com'
        }
        
        domain = email.split('@')[-1].lower()
        return domain not in personal_domains

class FileUtils:
    """File handling utilities"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUtils.ALLOWED_EXTENSIONS
    
    @staticmethod
    def secure_filename(filename):
        """Secure filename wrapper"""
        return secure_filename(filename)

class LeadManager:
    """Manage lead storage and retrieval"""
    
    def __init__(self, leads_file="leads.csv"):
        self.leads_file = leads_file
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.leads_file):
            with open(self.leads_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Name', 'Email', 'Company', 'Source', 'Notes'])
    
    def save_lead(self, name, email, company="", source="chatbot", notes=""):
        """Save a lead to CSV"""
        try:
            with open(self.leads_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    name,
                    email,
                    company,
                    source,
                    notes
                ])
            return True
        except Exception as e:
            logger.error(f"Error saving lead: {e}")
            return False
    
    def get_all_leads(self):
        """Get all leads from CSV"""
        try:
            leads = []
            if os.path.exists(self.leads_file):
                with open(self.leads_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    leads = list(reader)
            return leads
        except Exception as e:
            logger.error(f"Error reading leads: {e}")
            return []
    
    def get_leads_count(self):
        """Get total number of leads"""
        return len(self.get_all_leads())

class ChatAnalytics:
    """Track chat analytics"""
    
    def __init__(self, analytics_file="chat_analytics.json"):
        self.analytics_file = analytics_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create analytics file if it doesn't exist"""
        if not os.path.exists(self.analytics_file):
            self._save_analytics({
                "total_chats": 0,
                "demo_requests": 0,
                "leads_captured": 0,
                "last_updated": datetime.now().isoformat()
            })
    
    def _load_analytics(self):
        """Load analytics from file"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "total_chats": 0,
                "demo_requests": 0,
                "leads_captured": 0,
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_analytics(self, data):
        """Save analytics to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
    
    def log_chat(self, user_message, bot_response, demo_requested=False, lead_captured=False):
        """Log a chat interaction"""
        try:
            analytics = self._load_analytics()
            analytics["total_chats"] += 1
            
            if demo_requested:
                analytics["demo_requests"] += 1
            
            if lead_captured:
                analytics["leads_captured"] += 1
            
            analytics["last_updated"] = datetime.now().isoformat()
            self._save_analytics(analytics)
            
        except Exception as e:
            logger.error(f"Error logging chat analytics: {e}")
    
    def get_analytics(self):
        """Get current analytics"""
        return self._load_analytics()

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session_id(self, request):
        """Get or create session ID"""
        session_id = request.headers.get('X-Session-Id')
        if not session_id:
            session_id = str(uuid.uuid4())
        return session_id
    
    def get_session_data(self, session_id):
        """Get session data"""
        return self.sessions.get(session_id, {})
    
    def update_session(self, session_id, data):
        """Update session data"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id].update(data)

# Initialize global instances
security_utils = SecurityUtils()
file_utils = FileUtils()
lead_manager = LeadManager()
chat_analytics = ChatAnalytics()
session_manager = SessionManager()

# Decorators
def require_api_key(f):
    """Require API key for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = os.environ.get('API_KEY', 'palms-admin-key-2024')
        
        if not api_key or api_key != expected_key:
            return jsonify({"error": "Valid API key required"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_json_input(required_fields):
    """Validate JSON input has required fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "JSON input required"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit_key(request):
    """Generate rate limit key from request"""
    return request.remote_addr

# Error handlers
def handle_validation_error(e):
    """Handle 400 validation errors"""
    return jsonify({
        "error": "Validation error",
        "message": str(e),
        "timestamp": datetime.now().isoformat()
    }), 400

def handle_server_error(e):
    """Handle 500 server errors"""
    logger.error(f"Server error: {e}")
    return jsonify({
        "error": "Internal server error",
        "message": "Please try again later",
        "timestamp": datetime.now().isoformat()
    }), 500
