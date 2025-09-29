# chat_enhanced.py - Enhanced conversational chat with inline forms
import os
import time
import hashlib
import openai
from dotenv import load_dotenv
from simple_retriever import retrieve
import traceback
import csv
import re

load_dotenv()

# Initialize OpenAI with the older API format (compatible with openai==0.28.1)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Enhanced AI Persona for better conversation
SYSTEM_PERSONA = """
You are PALMS™ Assistant, a friendly and knowledgeable expert on warehouse management systems.

CRITICAL RULES:
1. Keep responses SHORT (2-3 sentences max)
2. Be conversational and natural, not robotic
3. Process the provided context into YOUR OWN WORDS - don't copy/paste chunks
4. Give complete thoughts but in minimal words
5. Always end with a natural follow-up question or engaging statement
6. Be helpful and enthusiastic about PALMS™

RESPONSE STYLE:
- Talk like a knowledgeable friend, not a manual
- Use simple, clear language
- Avoid jargon unless necessary
- Make every word count
- Sound excited about helping

Example GOOD response:
"PALMS™ helps businesses manage their warehouses more efficiently with real-time inventory tracking and automated processes. It's particularly great for growing e-commerce companies. What specific warehouse challenges are you facing?"

Example BAD response:
"PALMS™ Warehouse Management System (WMS) is a digital transformation tool for supply chain and warehouse management designed to effectively manage all warehouse operations..."
"""

# User session tracking
user_sessions = {}

def get_session(session_id="default"):
    """Get or create user session"""
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "message_count": 0,
            "has_provided_info": False,
            "name": None,
            "email": None,
            "conversation_stage": "initial"  # initial, info_requested, info_provided
        }
    return user_sessions[session_id]

def is_business_email(email: str) -> bool:
    """Check if email appears to be a business email"""
    if not email or '@' not in email:
        return False
    
    email = email.lower().strip()
    
    # Common personal email domains to reject
    personal_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
        'aol.com', 'icloud.com', 'protonmail.com', 'zoho.com',
        'live.com', 'msn.com', 'yahoo.co.uk', 'googlemail.com',
        'me.com', 'yahoo.ca', 'yahoo.co.in'
    }
    
    domain = email.split('@')[1]
    return domain not in personal_domains

def save_lead(name: str, email: str):
    """Save lead to CSV file"""
    leads_file = os.path.join(os.path.dirname(__file__), "leads.csv")
    
    # Only write header if file is empty
    write_header = os.path.getsize(leads_file) == 0 if os.path.exists(leads_file) else True
    with open(leads_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["Name", "Email", "Timestamp"])
        writer.writerow([name, email, time.strftime("%Y-%m-%d %H:%M:%S")])

def process_content_for_conversation(raw_content: list, query: str) -> str:
    """Process raw content into conversational format"""
    if not raw_content:
        return "I'd be happy to help you learn about PALMS™ warehouse management solutions."
    
    # Combine and summarize content
    combined_content = " ".join(raw_content[:2])  # Limit to top 2 results
    
    # Create a processing prompt
    processing_prompt = f"""
    Based on this content about PALMS™: {combined_content[:800]}
    
    User asked: {query}
    
    Create a SHORT (2-3 sentences), conversational response that:
    1. Directly answers their question
    2. Sounds natural and helpful
    3. Includes a follow-up question or engaging statement
    4. Is enthusiastic about PALMS™
    
    Don't copy the content directly - process it into your own conversational words.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PERSONA},
                {"role": "user", "content": processing_prompt}
            ],
            max_tokens=120,  # Force short responses
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except:
        # Fallback if OpenAI fails
        return "PALMS™ is a powerful warehouse management system that helps businesses optimize their operations. What specific aspect would you like to know more about?"

def detect_demo_request(message: str) -> bool:
    """Detect if user is requesting a demo"""
    message_lower = message.lower()
    
    demo_keywords = [
        'demo', 'demonstration', 'trial', 'test drive', 
        'show me', 'try it', 'preview', 'walkthrough',
        'see how it works', 'want to see', 'can i see',
        'schedule a demo', 'book a demo', 'request demo'
    ]
    
    return any(keyword in message_lower for keyword in demo_keywords)

def get_chat_response(user_input: str, session_id: str = "default") -> dict:
    """Enhanced chat response with session tracking"""
    try:
        session = get_session(session_id)
        session["message_count"] += 1
        
        # Handle greetings
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        if any(greet in user_input.lower() for greet in greetings):
            response = "Hi there! I'm here to help you discover how PALMS™ can transform your warehouse operations. What brings you here today?"
            
            return {
                'response': response,
                'show_demo_popup': False,
                'show_options': False,
                'show_info_form': session["message_count"] == 1 and not session["has_provided_info"],
                'session_stage': session["conversation_stage"]
            }
        
        # Handle demo requests
        if detect_demo_request(user_input):
            if not session["has_provided_info"]:
                return {
                    'response': "I'd love to show you a personalized PALMS™ demo! Let me get your details first so I can tailor it perfectly for your business.",
                    'show_demo_popup': False,
                    'show_options': False,
                    'show_info_form': True,
                    'session_stage': 'info_requested'
                }
            else:
                return {
                    'response': f"Perfect {session['name']}! I'll have our team reach out to {session['email']} within 24 hours to schedule your personalized PALMS™ demo.",
                    'show_demo_popup': False,
                    'show_options': False,
                    'show_info_form': False,
                    'session_stage': 'demo_scheduled'
                }
        
        # Get relevant content and process it
        raw_content = retrieve(user_input, n_results=3)
        processed_response = process_content_for_conversation(raw_content, user_input)
        
        # Determine if we should show the info form
        show_form = (session["message_count"] == 1 and 
                    not session["has_provided_info"] and 
                    session["conversation_stage"] == "initial")
        
        return {
            'response': processed_response,
            'show_demo_popup': False,
            'show_options': False,
            'show_info_form': show_form,
            'session_stage': session["conversation_stage"]
        }
        
    except Exception as e:
        print(f"AI Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'response': "I'm having a brief technical moment. PALMS™ is an amazing warehouse management system that helps businesses like yours optimize operations. What would you like to know?",
            'show_demo_popup': False,
            'show_options': False,
            'show_info_form': False,
            'session_stage': 'error'
        }

def handle_info_submission(name: str, email: str, session_id: str = "default") -> dict:
    """Handle user info submission"""
    try:
        session = get_session(session_id)
        
        # Validate inputs
        if not name or not email:
            return {
                'success': False,
                'message': 'Please provide both your name and email to continue.',
                'show_form_again': True
            }
        
        # Validate business email
        if not is_business_email(email):
            return {
                'success': False,
                'message': 'Please provide your business email address to continue.',
                'show_form_again': True
            }
        
        # Save the information
        session["name"] = name.strip()
        session["email"] = email.strip().lower()
        session["has_provided_info"] = True
        session["conversation_stage"] = "info_provided"
        
        # Save to CSV
        save_lead(session["name"], session["email"])
        
        return {
            'success': True,
            'message': f'Thanks {session["name"]}! Now I can help you better. What specific warehouse challenges are you looking to solve?',
            'show_form_again': False
        }
        
    except Exception as e:
        print(f"Error handling info submission: {e}")
        return {
            'success': False,
            'message': 'Sorry, there was an error. Please try again.',
            'show_form_again': True
        }

if __name__ == "__main__":
    # Test the enhanced chat system
    print("🧪 Testing Enhanced Chat System...")
    
    test_messages = [
        "Hello there",
        "What is PALMS?",
        "I want a demo",
        "Tell me about warehouse management"
    ]
    
    session_id = "test_user"
    
    for msg in test_messages:
        print(f"\n❓ User: {msg}")
        response = get_chat_response(msg, session_id)
        print(f"🤖 Bot: {response['response']}")
        print(f"📋 Show form: {response['show_info_form']}")
        print(f"🎯 Stage: {response['session_stage']}")
    
    # Test info submission
    print(f"\n📧 Testing info submission...")
    info_result = handle_info_submission("John Doe", "john@company.com", session_id)
    print(f"✅ Result: {info_result}")
