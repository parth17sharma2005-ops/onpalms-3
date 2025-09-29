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
You are PALMS™ Bot - a warehouse management expert. Follow these rules EXACTLY:

CRITICAL RULES:
1. ALWAYS respond in exactly two sentences:
   - First sentence (max 20 words): Direct answer to the question
   - Second sentence (max 10 words): Follow-up question related to their interest
2. If unable to answer within context, respond with:
   - "I'd need more specific details about your warehouse needs"
   - "Would you like to schedule a demo to discuss further?"
3. ONLY discuss PALMS™ warehouse management products and features
4. NEVER mention topics not in provided context
5. Always maintain conversation context and history
6. For complex queries, default to offering demo

PRODUCTS (ONLY discuss these):
• PALMS™ WMS: Core warehouse management
• PALMS™ 3PL: Third-party logistics
• PALMS™ Analytics: Business intelligence
• PALMS™ Mobile: Warehouse operations app
• PALMS™ Enterprise: Large-scale solution

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
    """Check if email appears to be a business email"""
    # List of common personal email domains
    personal_domains = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", 
        "icloud.com", "protonmail.com", "zoho.com", "live.com", "msn.com"
    ]
    domain = email.split('@')[-1].lower()
    return not any(domain == d for d in personal_domains)

def validate_response(response, context):
    """
    Validates bot response against known context to prevent hallucination
    Returns (is_valid, cleaned_response)
    """
    response_lower = response.lower()
    context_lower = context.lower()
    
    # Check for obvious hallucination indicators
    hallucination_phrases = [
        "consignment inventory",
        "pay upfront",
        "supplier owns",
        "small budget",
        "store",
        "retail",
        "items don't sell"
    ]
    
    for phrase in hallucination_phrases:
        if phrase in response_lower and phrase not in context_lower:
            return False, None
    
    # Ensure response only mentions products we actually have
    mentioned_products = []
    for product in PALMS_PRODUCTS.keys():
        if product.lower() in response_lower:
            mentioned_products.append(product)
    
    for product in mentioned_products:
        if product.lower() not in context_lower:
            return False, None
    
    # If valid, return cleaned response
    return True, response

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
        retrieved_content = retrieve(user_input, n_results=5)  # Get more results for better context
        
        # Enhance context with product information
        product_context = []
        user_input_lower = user_input.lower()
        
        # Add relevant product info based on user query
        if any(word in user_input_lower for word in ['product', 'offer', 'solution', 'service']):
            product_context.append("PALMS™ Product Line:\n" + "\n".join([f"- {name}: {desc}" for name, desc in PALMS_PRODUCTS.items()]))
        
        # Combine and filter context
        all_context = product_context + (retrieved_content if retrieved_content else ["Basic PALMS™ WMS information"])
        context = "\n\n".join(all_context)
        
        # Create the prompt with strict guidelines
        messages = [
            {"role": "system", "content": SYSTEM_PERSONA},
            {"role": "user", "content": f"""
Context (ONLY use this information - do not make up additional details):
{context}

User question: {user_input}

Requirements:
1. ONLY use information from the context above
2. Keep response short and simple
3. If information isn't in context, say you'll need to check
4. Use bullet points for lists
5. End with a relevant question

Remember: It's better to admit you need to check something than to make up information!
"""}
        ]
        
        # Get response from OpenAI with stricter temperature
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.5  # Lower temperature for more focused responses
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Validate response
        is_valid, cleaned_response = validate_response(answer, context)
        
        if not is_valid:
            # If invalid, generate a safe fallback response
            fallback = "Let me focus on what I know about PALMS™ products. Here are our core solutions:\n"
            fallback += "• PALMS™ WMS: Our main warehouse management system\n"
            fallback += "• PALMS™ Analytics: Real-time business intelligence\n"
            fallback += "Which would you like to know more about?"
            return {
                'response': fallback,
                'show_demo_popup': False,
                'show_options': True
            }
        
        return {
            'response': cleaned_response,
            'show_demo_popup': False,
            'show_options': True
        }
        
    except Exception as e:
        print(f"AI Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Fallback response
        return {
            'response': "I'm having trouble accessing my knowledge base. Here's what I definitely know about PALMS™:\n• We offer warehouse management solutions\n• Our system helps optimize operations\nWould you like to know about any specific feature?",
            'show_demo_popup': False,
            'show_options': False
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
