# app_enhanced.py - Production-Ready Flask Application
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import traceback

# Import our modules
from config import config
from utils import (
    lead_manager, chat_analytics, security_utils, file_utils,
    require_api_key, validate_json_input, handle_validation_error, 
    handle_server_error, rate_limit_key, logger
)
from chat import get_chat_response

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-API-Key"],
         methods=["GET", "POST", "OPTIONS"],
         supports_credentials=True)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register error handlers
    app.register_error_handler(400, handle_validation_error)
    app.register_error_handler(500, handle_server_error)
    
    # Routes
    @app.route("/")
    def home():
        """Home page"""
        return jsonify({
            "message": "PALMS™ Chatbot API - Enhanced Version",
            "status": "online",
            "version": "2.0",
            "endpoints": {
                "health": "/health",
                "chat": "/chat",
                "save_lead": "/save_lead", 
                "submit_info": "/submit_info",
                "leads": "/leads?api_key=your-key"
            },
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """Enhanced health check endpoint"""
        try:
            # Test OpenAI API key
            openai_status = "configured" if app.config['OPENAI_API_KEY'] else "missing"
            
            # Test file system
            test_file = os.path.join(app.config['UPLOAD_FOLDER'], '.test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                filesystem_status = "ok"
            except Exception:
                filesystem_status = "error"
            
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
                "openai_api": openai_status,
                "filesystem": filesystem_status,
                "total_leads": lead_manager.get_leads_count()
            })
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500
    
    @app.route("/chat", methods=["POST"])
    def chat():
        """Enhanced chat endpoint with analytics and security"""
        try:
            logger.info("Received chat request")
            
            # Handle both form data and JSON
            if request.is_json:
                data = request.get_json()
                message = data.get("message", "")
                user_email = data.get("email", "")
            else:
                message = request.form.get('message', '')
                user_email = request.form.get('email', '')
            
            # Sanitize input
            message = security_utils.sanitize_input(message)
            
            if not message:
                return jsonify({"error": "Message is required"}), 400
            
            # Validate message length
            if len(message) > 1000:
                return jsonify({"error": "Message too long (max 1000 characters)"}), 400
            
            logger.info(f"Processing message: {message[:100]}...")
            
            # Handle file upload if present
            pdf_text = ''
            if 'file' in request.files:
                file = request.files['file']
                if file and file_utils.allowed_file(file.filename):
                    try:
                        filename = file_utils.secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        
                        # Process PDF
                        import pdfplumber
                        with pdfplumber.open(filepath) as pdf:
                            pdf_text = '\\n'.join(page.extract_text() or '' for page in pdf.pages)
                        
                        # Clean up uploaded file
                        os.remove(filepath)
                        
                    except Exception as e:
                        logger.error(f"File processing error: {e}")
            
            # Get chat response
            chat_result = get_chat_response(message, extra_context=pdf_text)
            
            # Handle both old format (string) and new format (dict)
            if isinstance(chat_result, str):
                bot_response = chat_result
                show_demo_popup = False
                show_options = False
                show_info_form = False
            else:
                bot_response = chat_result.get('response', 'Sorry, I encountered an error.')
                show_demo_popup = chat_result.get('show_demo_popup', False)
                show_options = chat_result.get('show_options', False)
                show_info_form = chat_result.get('show_info_form', False)
            
            # Log analytics
            chat_analytics.log_chat(
                user_message=message,
                bot_response=bot_response,
                demo_requested=show_demo_popup,
                lead_captured=False
            )
            
            response_data = {
                "response": bot_response,
                "show_demo_popup": show_demo_popup,
                "show_options": show_options,
                "show_info_form": show_info_form,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Chat response generated successfully")
            return jsonify(response_data)
        
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": "I'm experiencing technical difficulties. Please try again.",
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route("/save_lead", methods=["POST"])
    @validate_json_input(['name', 'email'])
    def save_lead_route():
        """Enhanced lead saving with validation"""
        try:
            data = request.get_json()
            
            name = security_utils.sanitize_input(data.get("name", ""))
            email = security_utils.sanitize_input(data.get("email", ""))
            company = security_utils.sanitize_input(data.get("company", ""))
            source = security_utils.sanitize_input(data.get("source", "chatbot"))
            notes = security_utils.sanitize_input(data.get("notes", ""))
            
            # Validate inputs
            if not name or len(name) < 2:
                return jsonify({"success": False, "message": "Please provide a valid name."}), 400
            
            if not security_utils.validate_email(email):
                return jsonify({"success": False, "message": "Please provide a valid email address."}), 400
            
            if not security_utils.is_business_email(email):
                return jsonify({
                    "success": False, 
                    "message": "Please provide a business email address."
                }), 400
            
            # Save the lead
            if lead_manager.save_lead(name, email, company, source, notes):
                # Log analytics
                chat_analytics.log_chat(
                    user_message="Lead form submission",
                    bot_response="Lead saved",
                    demo_requested=True,
                    lead_captured=True
                )
                
                logger.info(f"Lead captured: {email}")
                
                return jsonify({
                    "success": True,
                    "message": "Thank you! Our sales team will contact you soon."
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Unable to process your request. Please try again."
                }), 500
        
        except Exception as e:
            logger.error(f"Error saving lead: {e}")
            return jsonify({
                "success": False,
                "message": "Technical error. Please try again later."
            }), 500
    
    @app.route("/submit_info", methods=["POST"])
    def submit_info():
        """Handle inline form submissions from chatbot"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "message": "No data provided"
                }), 400
            
            name = security_utils.sanitize_input(data.get("name", ""))
            email = security_utils.sanitize_input(data.get("email", ""))
            
            # Validate inputs
            if not name or len(name) < 2:
                return jsonify({
                    "success": False,
                    "message": "Please provide a valid name.",
                    "show_form_again": True
                }), 400
            
            if not security_utils.validate_email(email):
                return jsonify({
                    "success": False,
                    "message": "Please provide a valid email address.",
                    "show_form_again": True
                }), 400
            
            if not security_utils.is_business_email(email):
                return jsonify({
                    "success": False,
                    "message": "Please provide a business email address (no Gmail, Yahoo, etc.)",
                    "show_form_again": True
                }), 400
            
            # Save the lead with inline form source
            if lead_manager.save_lead(name, email, "", "inline_form", "Captured via chatbot inline form"):
                # Log analytics
                chat_analytics.log_chat(
                    user_message="Inline form submission",
                    bot_response="Contact info captured",
                    demo_requested=False,
                    lead_captured=True
                )
                
                logger.info(f"Inline form lead captured: {email}")
                
                return jsonify({
                    "success": True,
                    "message": f"Thanks {name}! I now have your details. How can I help you with PALMS™ today?",
                    "show_form_again": False
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Unable to save your information. Please try again.",
                    "show_form_again": True
                }), 500
        
        except Exception as e:
            logger.error(f"Error in submit_info: {e}")
            return jsonify({
                "success": False,
                "message": "Technical error. Please try again.",
                "show_form_again": True
            }), 500
    
    @app.route("/leads", methods=["GET"])
    @require_api_key
    def view_leads():
        """View all captured leads (requires API key)"""
        try:
            leads = lead_manager.get_all_leads()
            analytics = chat_analytics.get_analytics()
            
            # Create enhanced HTML report
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>PALMS™ Chatbot Dashboard</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                          margin: 0; padding: 40px; background: #f5f7fa; }}
                    .header {{ background: linear-gradient(135deg, #2F5D50 0%, #3A80BA 100%); 
                              color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
                    h1 {{ margin: 0; font-size: 2rem; }}
                    .subtitle {{ opacity: 0.9; margin-top: 8px; }}
                    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                             gap: 20px; margin-bottom: 30px; }}
                    .stat-card {{ background: white; padding: 24px; border-radius: 8px; 
                                 box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                    .stat-number {{ font-size: 2.5rem; font-weight: bold; color: #2F5D50; margin-bottom: 8px; }}
                    .stat-label {{ color: #666; font-size: 0.9rem; }}
                    .content {{ background: white; border-radius: 8px; padding: 30px; 
                               box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                    th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
                    tr:hover {{ background: #f8f9fa; }}
                    .download-btn {{ background: #3A80BA; color: white; padding: 12px 24px; 
                                   text-decoration: none; border-radius: 6px; display: inline-block; 
                                   margin: 20px 0; font-weight: 500; }}
                    .download-btn:hover {{ background: #2F5D50; }}
                    .timestamp {{ color: #666; font-size: 0.85rem; }}
                    .no-data {{ text-align: center; color: #666; padding: 40px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🤖 PALMS™ Chatbot Dashboard</h1>
                    <div class="subtitle">Lead Management & Analytics</div>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{len(leads)}</div>
                        <div class="stat-label">Total Leads</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{analytics.get('total_chats', 0)}</div>
                        <div class="stat-label">Chat Conversations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{analytics.get('demo_requests', 0)}</div>
                        <div class="stat-label">Demo Requests</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{(analytics.get('leads_captured', 0) / max(analytics.get('demo_requests', 1), 1) * 100):.1f}%</div>
                        <div class="stat-label">Conversion Rate</div>
                    </div>
                </div>
                
                <div class="content">
                    <h2>💼 Captured Leads</h2>
                    <a href="/leads/download" class="download-btn">📥 Download CSV</a>
            """
            
            if leads:
                html += """
                    <table>
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Company</th>
                                <th>Source</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for lead in leads:
                    timestamp = lead.get('Timestamp', '')
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            formatted_time = timestamp
                    else:
                        formatted_time = 'Unknown'
                    
                    html += f"""
                        <tr>
                            <td><span class="timestamp">{formatted_time}</span></td>
                            <td>{lead.get('Name', '')}</td>
                            <td>{lead.get('Email', '')}</td>
                            <td>{lead.get('Company', 'Not specified')}</td>
                            <td>{lead.get('Source', 'chatbot')}</td>
                        </tr>
                    """
                
                html += "</tbody></table>"
            else:
                html += '<div class="no-data">📭 No leads captured yet</div>'
            
            html += """
                </div>
                <div style="text-align: center; margin-top: 40px; color: #666;">
                    <small>Generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</small>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error viewing leads: {e}")
            return jsonify({"error": "Unable to retrieve leads"}), 500
    
    @app.route("/leads/download", methods=["GET"])
    @require_api_key
    def download_leads():
        """Download leads as CSV"""
        try:
            leads_file = lead_manager.leads_file
            if os.path.exists(leads_file):
                return send_file(
                    leads_file,
                    as_attachment=True,
                    download_name=f"palms_leads_{datetime.now().strftime('%Y%m%d')}.csv",
                    mimetype='text/csv'
                )
            else:
                return jsonify({"error": "No leads file found"}), 404
        
        except Exception as e:
            logger.error(f"Error downloading leads: {e}")
            return jsonify({"error": "Unable to download leads"}), 500
    
    @app.route("/sync-to-sheets", methods=["GET", "POST"])
    @require_api_key
    def sync_to_sheets():
        """Sync all leads to Google Sheets"""
        return jsonify({
            "error": "Google Sheets integration not implemented yet",
            "message": "Use CSV download for now"
        }), 501
    
    @app.route("/analytics", methods=["GET"])
    @require_api_key
    def get_analytics():
        """Get analytics data as JSON"""
        try:
            analytics = chat_analytics.get_analytics()
            analytics['total_leads'] = lead_manager.get_leads_count()
            return jsonify(analytics)
        
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return jsonify({"error": "Unable to retrieve analytics"}), 500
    
    # API-only routes - no templates needed for chatbot service
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    logger.info("Starting PALMS™ Chatbot Backend...")
    
    # Get environment
    env = os.environ.get('FLASK_ENV', 'development')
    debug = env == 'development'
    
    if debug:
        logger.info("Running in development mode")
        app.run(debug=True, host="127.0.0.1", port=8000)
    else:
        logger.info("Running in production mode")
        # Use gunicorn in production
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
