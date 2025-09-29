from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import os
from datetime import datetime
import csv
import re

# Import our chat system
from chat import get_chat_response, save_lead, is_business_email

app = Flask(__name__)

# Enable CORS for specific domains
CORS(app, 
     origins=["https://smartwms.onpalms.com", "http://localhost:3000", "http://127.0.0.1:8080"], 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Session-Id"], 
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=True,
     allow_credentials=True)
CORS(app, 
     origins=["*"], 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Session-Id"], 
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=True)

@app.route("/")
def home():
    """Health check and API info"""
    return jsonify({
        "service": "OnPalms Chatbot API",
        "status": "active",
        "version": "2.0",
        "endpoints": {
            "/chat": "POST - Chat with the bot",
            "/save_lead": "POST - Save lead information",
            "/health": "GET - Health check"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    try:
        print("📨 Received chat request")

        message = None
        
        # Get message from form data or JSON
        if request.form.get('message'):
            message = request.form.get('message')
        elif request.is_json:
            data = request.get_json()
            message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        print(f"💬 User message: {message[:100]}...")

        # Get chat response using existing chat.py logic
        chat_result = get_chat_response(message)
        
        print(f"🤖 Bot response generated")
        
        # Ensure the response is in the correct format
        if isinstance(chat_result, dict):
            response_data = chat_result
        else:
            # Fallback for string responses
            response_data = {
                "response": str(chat_result),
                "show_demo_popup": False,
                "show_options": False
            }

        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Error in /chat endpoint: {str(e)}")
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Server error occurred", 
            "response": "I'm sorry, I'm having technical difficulties. Please try again in a moment.",
            "show_demo_popup": False,
            "show_options": False
        }), 500

@app.route("/save_lead", methods=["POST"])
def save_lead_route():
    """Save lead information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False, 
                "message": "No data provided"
            }), 400
        
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        
        if not name or not email:
            return jsonify({
                "success": False, 
                "message": "Name and email are required"
            }), 400
        
        # Validate business email
        if not is_business_email(email):
            return jsonify({
                "success": False, 
                "message": "Please provide a business email address",
                "show_demo_popup": True  # Show demo popup for non-business emails
            }), 400
        
        # Save the lead using existing function
        save_lead(name, email)
        
        print(f"✅ Lead saved: {name} ({email})")
        
        return jsonify({
            "success": True, 
            "message": "Thank you! Our sales team will contact you soon."
        })
        
    except Exception as e:
        print(f"❌ Error saving lead: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Error saving your information. Please try again."
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "OnPalms Chatbot API",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    # Run the app
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting OnPalms Chatbot API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
