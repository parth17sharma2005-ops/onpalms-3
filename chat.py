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

# Define known product information
PALMS_PRODUCTS = {
    "WMS": "Core warehouse management system",
    "3PL": "Third-party logistics solution",
    "Analytics": "Business intelligence and reporting",
    "Mobile": "Mobile warehouse operations app",
    "Enterprise": "Enterprise-scale WMS solution"
}

# Enhanced AI Persona with strict context control and concise responses
SYSTEM_PERSONA = """
You are PALMS™ Bot - a warehouse management expert representing PALMS™, a leading warehouse management solutions provider. Follow these rules EXACTLY:

CRITICAL RULES:
1. FORMAT YOUR RESPONSES:
   - First line: Direct answer to the question (max 20 words)
   - Second line: Follow-up question (max 10 words)
2. If unable to answer within context, respond with:
   "I'd need more specific details about your warehouse needs.
   Would you like to schedule a demo to discuss further?"
3. STICK TO FACTS: 
   - ONLY use information from the provided context
   - NEVER make up features or capabilities
   - If unsure, offer a demo instead of guessing
4. FOCUS ON CORE OFFERINGS:
   - Only discuss PALMS™ warehouse management products
   - Keep responses focused on actual features
   - Default to offering a demo for detailed questions

PRODUCTS (ONLY discuss these, with EXACT features):
• PALMS™ WMS: 
  - Real-time inventory tracking
  - Automated order processing
  - Warehouse space optimization
  - Stock movement tracking
  
• PALMS™ 3PL: 
  - Multi-warehouse management
  - Client portal access
  - Billing automation
  - Resource allocation
  
• PALMS™ Analytics: 
  - Performance metrics
  - Custom reporting
  - Real-time dashboards
  - Trend analysis
  
• PALMS™ Mobile: 
  - Barcode scanning
  - Mobile picking
  - Real-time updates
  - Worker tracking
  
• PALMS™ Enterprise: 
  - Multi-site management
  - Advanced integrations
  - Custom workflows
  - Enterprise scaling

RESPONSE FORMAT:
[Direct Answer - 20 words max] + [Follow-up Question - 10 words max]

EXAMPLE RESPONSES:
✅ GOOD: "PALMS™ WMS provides real-time inventory tracking and automated order processing. Would you like to see it in action?"

✅ GOOD: "Our 3PL solution manages multiple warehouses through a single dashboard. What specific logistics challenges are you facing?"

❌ BAD: "Let me tell you about our features..." (too vague)
❌ BAD: "PALMS™ WMS does many things..." (not specific)
❌ BAD: Responses longer than 20 words
❌ BAD: Follow-up questions longer than 10 words

❌ BAD: Any response that:
- Discusses non-PALMS topics
- Makes claims not in context
- Uses complex language
- Gives long explanations
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
    """
    Check if email appears to be a business email
    Returns tuple (is_business, show_demo)
    """
    # List of common personal email domains
    personal_domains = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", 
        "icloud.com", "protonmail.com", "zoho.com", "live.com", "msn.com",
        "yahoo.co.uk", "yahoo.co.in", "gmail.co.uk"
    ]
    domain = email.split('@')[-1].lower()
    is_business = not any(domain == d for d in personal_domains)
    # For non-business emails, we want to show the demo popup
    return is_business, not is_business

def generate_product_context(user_input):
    """Generate relevant product context based on user input"""
    context_parts = []
    
    # Always include base product information
    context_parts.append("PALMS™ Product Information:")
    for name, desc in PALMS_PRODUCTS.items():
        context_parts.append(f"{name}: {desc}")
    
    # Add detailed features for relevant queries
    user_input_lower = user_input.lower()
    if any(word in user_input_lower for word in ['product', 'offer', 'solution', 'service', 'feature', 'capability']):
        features = {
            "WMS": [
                "Real-time inventory tracking",
                "Automated order processing",
                "Warehouse space optimization",
                "Stock movement tracking"
            ],
            "3PL": [
                "Multi-warehouse management",
                "Client portal access",
                "Billing automation",
                "Resource allocation"
            ],
            "Analytics": [
                "Performance metrics",
                "Custom reporting",
                "Real-time dashboards",
                "Trend analysis"
            ],
            "Mobile": [
                "Barcode scanning",
                "Mobile picking",
                "Real-time updates",
                "Worker tracking"
            ],
            "Enterprise": [
                "Multi-site management",
                "Advanced integrations",
                "Custom workflows",
                "Enterprise scaling"
            ]
        }
        
        for name, product_features in features.items():
            if name.lower() in user_input_lower or any(f.lower() in user_input_lower for f in product_features):
                context_parts.append(f"\nPALMS™ {name} Features:")
                context_parts.extend([f"- {feature}" for feature in product_features])
    
    return "\n".join(context_parts)

def get_chat_response(user_input, extra_context=''):
    """Main chat response function with enhanced context handling and validation"""
    try:
        # Detect greetings and demo requests first
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        is_greeting = any(greet in user_input.lower() for greet in greetings)
        wants_demo = detect_demo_request(user_input)

        # Handle greetings
        if is_greeting:
            return {
                'response': "Welcome to PALMS™, your warehouse management expert. What specific challenges can I help you address?",
                'show_demo_popup': False,
                'show_options': False
            }
        
        # Handle demo requests
        if wants_demo:
            return {
                'response': "I'll arrange a personalized demo of PALMS™ for your warehouse needs. Please fill out this quick form to proceed.",
                'show_demo_popup': True,
                'show_options': False
            }
        
        # Check if query is too complex or requires detailed explanation
        complex_keywords = ['how', 'explain', 'details', 'features', 'benefits', 'compare', 'difference', 'pricing', 'cost']
        is_complex_query = any(keyword in user_input.lower() for keyword in complex_keywords)
        
        if is_complex_query:
            return {
                'response': "Your question requires a detailed explanation of our solutions. Would you like to schedule a demo for a comprehensive overview?",
                'show_demo_popup': True,
                'show_options': False
            }
        
        # Get relevant content from WordPress
        try:
            retrieved_content = retrieve(user_input, n_results=5)
            print(f"📚 Retrieved content length: {len(retrieved_content) if retrieved_content else 0} items")
        except Exception as retrieve_error:
            print(f"⚠️ Content retrieval error: {str(retrieve_error)}")
            retrieved_content = []
        
        # Always include base product information
        product_context = ["PALMS™ Product Information:"]
        for name, desc in PALMS_PRODUCTS.items():
            product_context.append(f"{name}: {desc}")
        
        # Add detailed features for relevant queries
        user_input_lower = user_input.lower()
        if any(word in user_input_lower for word in ['product', 'offer', 'solution', 'service', 'feature', 'capability']):
            for name, features in {
                "WMS": ["Real-time inventory tracking", "Automated order processing", "Warehouse optimization"],
                "3PL": ["Multi-warehouse management", "Client portal", "Billing automation"],
                "Analytics": ["Performance metrics", "Custom reporting", "Real-time dashboards"],
                "Mobile": ["Barcode scanning", "Mobile picking", "Real-time updates"],
                "Enterprise": ["Multi-site management", "Advanced integrations", "Custom workflows"]
            }.items():
                product_context.append(f"\nPALMS™ {name} Features:")
                product_context.extend([f"- {feature}" for feature in features])
        
        # Combine contexts with proper formatting
        context_parts = ["\n".join(product_context)]
        if retrieved_content:
            context_parts.append("\nAdditional Information:\n" + "\n".join(retrieved_content))
        
        context = "\n\n".join(context_parts)
        print(f"📝 Final context length: {len(context)} characters")
        
        # Generate context based on user input
        context = generate_product_context(user_input)
        print(f"📝 Generated context length: {len(context)} characters")
        
        # Create the prompt with simplified guidelines
        messages = [
            {"role": "system", "content": SYSTEM_PERSONA},
            {"role": "user", "content": f"""
Context:
{context}

User question: {user_input}

Requirements:
1. Answer directly using the context provided
2. Keep responses short and focused
3. End with a relevant follow-up question
"""}
        ]
        
        # Get response from OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"📝 AI response: {answer[:100]}...")
            
            return {
                'response': answer,
                'show_demo_popup': False,
                'show_options': True
            }
        except Exception as openai_error:
            print(f"OpenAI API error: {str(openai_error)}")
            raise openai_error
        
    except Exception as e:
        print("=" * 50)
        print("🔴 ERROR DETAILS")
        print("=" * 50)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"User Input: {user_input}")
        print("-" * 50)
        print("Context:")
        print(context if context else "No context available")
        print("-" * 50)
        print("Full Traceback:")
        print(traceback.format_exc())
        print("=" * 50)

        if isinstance(e, openai.error.AuthenticationError):
            return {
                'response': "There seems to be an issue with the API configuration. The team has been notified.",
                'show_demo_popup': False,
                'show_options': False
            }
        elif isinstance(e, openai.error.APIError):
            return {
                'response': "Our AI service is temporarily unavailable. Please try again in a moment.",
                'show_demo_popup': False,
                'show_options': False
            }
        elif isinstance(e, openai.error.Timeout):
            return {
                'response': "The request took too long to process. Please try a simpler question.",
                'show_demo_popup': False,
                'show_options': False
            }
        else:
            error_type = type(e).__name__
            print(f"⚠️ Unhandled error type: {error_type}")
            
            # More specific error messages based on error type
            if "Context" in str(e) or "content" in str(e).lower():
                return {
                    'response': "I'm having trouble processing the product information. Could you please ask about a specific PALMS™ feature or product?",
                    'show_demo_popup': False,
                    'show_options': True
                }
            elif "rate" in str(e).lower() or "limit" in str(e).lower():
                return {
                    'response': "Our system is experiencing high demand. Please try again in a moment.",
                    'show_demo_popup': False,
                    'show_options': False
                }
            else:
                # More informative general fallback
                top_product = next(iter(PALMS_PRODUCTS.items()))
                return {
                    'response': f"While I'm addressing your question, let me tell you about our flagship product:\n\nPALMS™ {top_product[0]}: {top_product[1]}\n\nWould you like to know more about this or our other solutions?",
                    'show_demo_popup': False,
                    'show_options': True
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
