# chat.py - ENHANCED WITH CONTEXTUAL INTELLIGENCE
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

_response_cache = {}
CACHE_MAX_SIZE = 100

# Enhanced AI Persona for better understanding
SYSTEM_PERSONA = """
You are PALMS™ Salesbot, a friendly assistant for PALMS™ Warehouse Management. 

- Always start your response with a normal sentence introducing the topic. This first sentence must NEVER be a bullet point.  
- Only use bullet points for subsequent items if explicitly listing features, products, or clients (max 4 bullets).  
- Do not use bullet points for normal sentences or general explanations.  

- Use the provided chunks only as background knowledge.  
- Always give answers in complete sentences, even if the chunks are cut off.  
- Keep answers short, clear, warm, and approachable. Avoid jargon or overly technical language.  
- Use a conversational tone, like you are talking to a customer.  
- Your goal is to engage visitors, understand their needs, and encourage them to book a demo.  
- Respond politely, enthusiastically, and persuasively.  
- If needed, summarize long chunks into 2–3 sentences.  
- Always end your response with a gentle follow-up question, such as: 
  'Would you like to know more?', 'Should I connect you with our team?', or 'Would you like more details on this?'.  
- If a user requests a demo, respond with: "Kindly fill out the form to sign up for a demo."  
- If a user declines a demo, respond with: "No problem! Let me know if you have any other questions."

Example – correct response:
PALMS™ offers a variety of products designed to streamline warehouse management for businesses of all sizes.
- PALMS WMS: Core system for inventory and operations.
- PALMS 3PL: For third-party logistics providers.
Would you like to know more?

Example – incorrect response:
- PALMS™ offers a variety of products designed to streamline warehouse management for businesses of all sizes.
- PALMS WMS: Core system for inventory and operations.
Would you like to know more?
"""

def detect_demo_request(message):
    """
    Detect if user is asking for a demo based on keywords and context
    Returns True only if user is positively requesting a demo
    """
    message_lower = message.lower()
    
    # First check for negative indicators - if found, return False immediately
    negative_indicators = [
        "don't want", "dont want", "do not want", "not interested",
        "no demo", "no thank", "not now", "maybe later", "not ready",
        "don't need", "dont need", "do not need", "not looking",
        "no thanks", "not yet", "decline", "refuse", "not for me",
        "don't think", "dont think", "do not think", "not sure",
        "not what", "doesn't sound", "doesnt sound", "does not sound"
    ]
    
    for negative in negative_indicators:
        if negative in message_lower:
            return False
    
    # Check for negative patterns
    negative_patterns = [
        r'\b(no|not|don\'?t|do\s+not|never)\s+.*(demo|try|test|interested)\b',
        r'\b(maybe|perhaps|might)\s+(later|another\s+time)\b',
        r'\bnot\s+(ready|sure|interested|now)\b'
    ]
    
    for pattern in negative_patterns:
        if re.search(pattern, message_lower):
            return False
    
    # Now check for positive demo requests
    demo_keywords = [
        'demo', 'demonstration', 'trial', 'test drive', 
        'show me', 'try it', 'preview', 'walkthrough',
        'see how it works', 'want to see',
        'schedule a demo', 'book a demo', 'request demo',
        'free trial', 'pilot', 'poc', 'proof of concept'
    ]
    
    # Check if message contains demo-related keywords with positive intent
    positive_found = False
    for keyword in demo_keywords:
        if keyword in message_lower:
            positive_found = True
            break
    
    return positive_found

LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads.csv")

def save_lead(name, email):
    """Save lead to CSV file"""
    # Only write header if file is empty
    write_header = os.path.getsize(LEADS_FILE) == 0 if os.path.exists(LEADS_FILE) else True
    with open(LEADS_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["Name", "Email", "Timestamp"])
        writer.writerow([name, email, time.strftime("%Y-%m-%d %H:%M:%S")])

def is_business_email(email):
    """Check if email appears to be a business email"""
    # List of common personal email domains
    personal_domains = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", 
        "icloud.com", "protonmail.com", "zoho.com", "live.com", "msn.com"
    ]
    domain = email.split('@')[-1].lower()
    return not any(domain == d for d in personal_domains)

def should_show_inline_form(user_input, conversation_depth=0):
    """Determine if we should show inline form for lead capture"""
    # Patterns that suggest user interest but needs info capture
    interest_patterns = [
        "pricing", "cost", "price", "quote", "budget",
        "contact", "sales", "team", "speak", "call",
        "more information", "details", "learn more",
        "interested", "purchase", "buy", "subscribe"
    ]
    
    # Show form if user shows interest and we don't have their info
    return any(pattern in user_input.lower() for pattern in interest_patterns)

def get_chat_response(user_input, extra_context=''):
    """Main chat response function"""
    try:
        # Detect greetings and demo requests first
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        is_greeting = any(greet in user_input.lower() for greet in greetings)
        wants_demo = detect_demo_request(user_input)
        wants_info_form = should_show_inline_form(user_input)

        # Handle greetings
        if is_greeting:
            return {
                'response': "Hello! I'm here to help you learn about PALMS™ Warehouse Management System. How can I assist you today?",
                'show_demo_popup': False,
                'show_options': False,
                'show_info_form': False
            }
        
        # Handle demo requests
        if wants_demo:
            return {
                'response': "I'd be happy to show you a demo of PALMS™! Our warehouse management system can really transform your operations. Please fill out the form below and we'll get you set up with a personalized demonstration.",
                'show_demo_popup': True,
                'show_options': False,
                'show_info_form': False
            }
        
        # Get relevant content from WordPress
        retrieved_content = retrieve(user_input, n_results=3)
        
        # Build context for AI
        context = "\n\n".join(retrieved_content) if retrieved_content else "General information about PALMS™ Warehouse Management System."
        
        # Create the prompt for OpenAI
        messages = [
            {"role": "system", "content": SYSTEM_PERSONA},
            {"role": "user", "content": f"""
Context from OnPalms website:
{context}

User question: {user_input}

Please answer based on the context provided. Keep it conversational and helpful.
"""}
        ]
        
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()

        # Second AI layer: rephrase to be less technical and more friendly
        try:
            rephrase_prompt = [
                {"role": "system", "content": "You are a helpful assistant. Rewrite the following answer in a friendly, non-technical, easy-to-understand way for a business user. Avoid jargon and make it sound warm and approachable."},
                {"role": "user", "content": answer}
            ]
            rephrase_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=rephrase_prompt,
                max_tokens=200,
                temperature=0.7
            )
            friendly_answer = rephrase_response.choices[0].message.content.strip()
        except Exception as rephrase_error:
            print(f"Rephrase AI Error: {rephrase_error}")
            friendly_answer = answer  # fallback to original

        return {
            'response': friendly_answer,
            'show_demo_popup': False,
            'show_options': True,
            'show_info_form': wants_info_form
        }
        
    except Exception as e:
        print(f"AI Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Fallback response
        return {
            'response': "I'm experiencing a technical difficulty right now. PALMS™ is a comprehensive warehouse management system that helps businesses optimize their operations. Would you like to know more about our features?",
            'show_demo_popup': False,
            'show_options': False,
            'show_info_form': False
        }

if __name__ == "__main__":
    # Test the chat system
    print("🧪 Testing Chat System...")
    
    test_messages = [
        "Hello",
        "What is PALMS?",
        "I want a demo",
        "Tell me about warehouse management"
    ]
    
    for msg in test_messages:
        print(f"\n❓ User: {msg}")
        response = get_chat_response(msg)
        print(f"🤖 Bot: {response['response']}")
        print(f"📅 Demo popup: {response['show_demo_popup']}")
