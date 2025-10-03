<?php
/**
 * Enhanced PALMS Chatbot with Inline Forms
 * Features: Conversational AI, Inline Forms, Business Email Validation
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}

if ( ! function_exists( 'elementor_theme_do_location' ) || ! elementor_theme_do_location( 'footer' ) ) {
	if ( hello_elementor_display_header_footer() ) {
		if ( did_action( 'elementor/loaded' ) && hello_header_footer_experiment_active() ) {
			get_template_part( 'template-parts/dynamic-footer' );
		} else {
			get_template_part( 'template-parts/footer' );
		}
	}
}
?>

<?php wp_footer(); ?>
<!-- PALMS Enhanced Chatbot - Direct Theme Integration -->
<?php if (!wp_is_mobile() || true) { // Show on all devices ?>

<style>
/* PALMS Enhanced Chatbot - Standalone CSS */
#palms-enhanced-chatbot * {
    box-sizing: border-box !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

#palms-enhanced-chatbot {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: column !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}

/* Minimized state */
#palms-enhanced-chatbot.minimized {
    width: 64px !important;
    height: 64px !important;
    border-radius: 50% !important;
    background: #2F5D50 !important;
    cursor: pointer !important;
    align-items: center !important;
    justify-content: center !important;
}

#palms-enhanced-chatbot.minimized:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 8px 25px rgba(47, 93, 80, 0.3) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}

/* Header */
.palms-header {
    background: linear-gradient(135deg, #2F5D50 0%, #3A80BA 100%) !important;
    color: #fff !important;
    padding: 16px 20px !important;
    border-radius: 12px 12px 0 0 !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}

.palms-minimize-btn {
    background: transparent !important;
    border: none !important;
    color: #fff !important;
    cursor: pointer !important;
    padding: 4px !important;
    border-radius: 4px !important;
    width: 24px !important;
    height: 24px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: background 0.2s !important;
}

.palms-minimize-btn:hover {
    background: rgba(255,255,255,0.1) !important;
}

/* Chat icon */
.palms-chat-icon {
    cursor: pointer !important;
    display: none !important;
}

#palms-enhanced-chatbot.minimized .palms-chat-icon {
    display: flex !important;
}

#palms-enhanced-chatbot.minimized .palms-header {
    display: none !important;
}

/* Body */
.palms-body {
    flex: 1 !important;
    padding: 16px !important;
    overflow-y: auto !important;
    height: 400px !important;
    max-height: 400px !important;
    min-height: 400px !important;
    background: #FAFBFC !important;
}

/* Messages */
.palms-message {
    margin-bottom: 12px !important;
    padding: 12px 16px !important;
    border-radius: 18px !important;
    max-width: 85% !important;
    word-wrap: break-word !important;
    font-size: 0.95rem !important;
    line-height: 1.4 !important;
    display: inline-block !important;
    clear: both !important;
}

.palms-message.user {
    background: #F2F4F6 !important;
    color: #1E1E1E !important;
    float: right !important;
    border-bottom-right-radius: 6px !important;
}

.palms-message.bot {
    background: #2F5D50 !important;
    color: #fff !important;
    float: left !important;
    border-bottom-left-radius: 6px !important;
}

.palms-message.system {
    background: #E3F2FD !important;
    color: #1565C0 !important;
    float: left !important;
    border: 1px solid #BBDEFB !important;
    font-size: 0.9rem !important;
}

/* Inline Form Styles */
.palms-inline-form {
    background: #FFFFFF !important;
    border: 2px solid #E0E7FF !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin: 12px 0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    clear: both !important;
    width: 100% !important;
}

.palms-form-title {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #2F5D50 !important;
    margin-bottom: 12px !important;
    text-align: center !important;
}

.palms-form-row {
    margin-bottom: 12px !important;
}

.palms-form-input {
    width: 100% !important;
    padding: 10px 12px !important;
    border: 2px solid #E5E7EB !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    background: #FFFFFF !important;
    color: #1F2937 !important;
    outline: none !important;
    transition: border-color 0.2s !important;
}

.palms-form-input:focus {
    border-color: #3A80BA !important;
    box-shadow: 0 0 0 3px rgba(58, 128, 186, 0.1) !important;
}

.palms-form-input::placeholder {
    color: #9CA3AF !important;
}

.palms-form-submit {
    width: 100% !important;
    padding: 12px !important;
    background: #3A80BA !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}

.palms-form-submit:hover {
    background: #2F5D50 !important;
}

.palms-form-error {
    background: #FEF2F2 !important;
    color: #DC2626 !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    margin-top: 8px !important;
    border-left: 4px solid #DC2626 !important;
}

/* Typing animation */
.palms-message.typing {
    background: #2F5D50 !important;
    color: #fff !important;
    float: left !important;
    padding: 16px !important;
}

.palms-typing-dots {
    display: flex !important;
    gap: 4px !important;
}

.palms-typing-dots span {
    width: 8px !important;
    height: 8px !important;
    background: #fff !important;
    border-radius: 50% !important;
    animation: palmsTyping 1.4s infinite ease-in-out !important;
}

.palms-typing-dots span:nth-child(1) { animation-delay: -0.32s !important; }
.palms-typing-dots span:nth-child(2) { animation-delay: -0.16s !important; }

@keyframes palmsTyping {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}

/* Input form */
.palms-input-form {
    display: flex !important;
    flex-direction: column !important;
    padding: 16px 16px 8px 16px !important;
    background: #F2F4F6 !important;
    border-radius: 0 0 12px 12px !important;
}

.palms-input-row {
    display: flex !important;
    gap: 8px !important;
    align-items: center !important;
    margin-bottom: 12px !important;
}

.palms-input {
    flex: 1 !important;
    padding: 12px 16px !important;
    border: 1px solid #D9DEE2 !important;
    border-radius: 24px !important;
    font-size: 0.95rem !important;
    background: #fff !important;
    color: #1E1E1E !important;
    outline: none !important;
    font-family: inherit !important;
}

.palms-input:focus {
    border-color: #3A80BA !important;
    box-shadow: 0 0 0 3px rgba(58, 128, 186, 0.1) !important;
}

.palms-send-btn {
    background: #3A80BA !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50% !important;
    width: 48px !important;
    height: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    font-size: 1.5rem !important;
    transition: background 0.2s !important;
}

.palms-send-btn:hover {
    background: #2F5D50 !important;
}

/* Disclaimer */
.palms-disclaimer {
    margin: 0 !important;
    padding: 8px 12px !important;
    font-size: 0.8rem !important;
    color: #6E7B85 !important;
    text-align: center !important;
    line-height: 1.2 !important;
}

/* Hidden states */
.palms-hidden {
    display: none !important;
}
</style>

<div id="palms-enhanced-chatbot" class="minimized">
    <div class="palms-header">
        <span>PALMS Assistant</span>
        <button class="palms-minimize-btn" onclick="palmsMinimize()">
            <svg viewBox="0 0 20 20" fill="currentColor" style="width:16px;height:16px;">
                <rect x="4" y="9" width="12" height="2" rx="1" fill="currentColor"/>
            </svg>
        </button>
    </div>
    
    <div class="palms-chat-icon" onclick="palmsMaximize()" style="width:64px;height:64px;background:white;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:8px;box-sizing:border-box;border:3px solid #2F5D50;">
        <img src="https://smartwms.onpalms.com/wp-content/uploads/2025/09/palmslogo.png" alt="PALMS Logo" style="width:48px;height:48px;object-fit:contain;border-radius:4px;" />
    </div>
    
    <div class="palms-body palms-hidden"></div>
    
    <form class="palms-input-form palms-hidden" onsubmit="palmsSendMessage(event)">
        <div class="palms-input-row">
            <input type="text" class="palms-input" placeholder="Ask about PALMS™..." autocomplete="off" />
            <button type="submit" class="palms-send-btn">➤</button>
        </div>
        <div class="palms-disclaimer">Powered by PALMS™ AI Assistant</div>
    </form>
</div>

<script>
// PALMS Enhanced Chatbot JavaScript
(function() {
    let minimized = true;
    let hasAutoOpened = false;
    
    const widget = document.getElementById('palms-enhanced-chatbot');
    const body = widget.querySelector('.palms-body');
    const form = widget.querySelector('.palms-input-form');
    const input = widget.querySelector('.palms-input');
    
    // API Configuration
    const API_URL = 'https://onpalms-chatbot-api.onrender.com'; // Change this for experimental deployment
    
    window.palmsMinimize = function() {
        minimized = true;
        
        widget.style.cssText = `
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            width: 64px !important;
            height: 64px !important;
            border-radius: 50% !important;
            background: #2F5D50 !important;
            z-index: 999999 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.16) !important;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            transform: scale(1) !important;
        `;
        
        widget.classList.add('minimized');
        body.classList.add('palms-hidden');
        form.classList.add('palms-hidden');
    };
    
    window.palmsMaximize = function() {
        minimized = false;
        
        widget.style.cssText = `
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            width: 380px !important;
            height: 600px !important;
            max-height: 600px !important;
            min-height: 600px !important;
            border-radius: 12px !important;
            background: #FAFBFC !important;
            z-index: 999999 !important;
            display: flex !important;
            flex-direction: column !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.16) !important;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            transform: scale(1) !important;
        `;
        
        if (body) {
            body.style.cssText = `
                flex: 1 !important;
                padding: 16px !important;
                overflow-y: auto !important;
                height: 400px !important;
                max-height: 400px !important;
                background: #FAFBFC !important;
            `;
        }
        
        widget.classList.remove('minimized');
        body.classList.remove('palms-hidden');
        form.classList.remove('palms-hidden');
        
        // Add welcome message if first time
        if (body.children.length === 0) {
            setTimeout(() => {
                palmsAddMessage("Hi! I'm your PALMS™ assistant. How can I help you optimize your warehouse today?", false);
            }, 400);
        }
    };
    
    function palmsAddMessage(text, isUser = false, messageType = 'normal') {
        const msg = document.createElement('div');
        let className = 'palms-message ';
        
        if (messageType === 'system') {
            className += 'system';
        } else {
            className += isUser ? 'user' : 'bot';
        }
        
        msg.className = className;
        msg.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        body.appendChild(msg);
        
        // Add clearfix
        const clearfix = document.createElement('div');
        clearfix.style.clear = 'both';
        clearfix.style.height = '0';
        body.appendChild(clearfix);
        
        body.scrollTop = body.scrollHeight;
        return msg;
    }
    
    function palmsAddInlineForm() {
        const formContainer = document.createElement('div');
        formContainer.className = 'palms-inline-form';
        formContainer.innerHTML = `
            <div class="palms-form-title">Please share your details to continue</div>
            <div class="palms-form-row">
                <input type="text" class="palms-form-input" name="name" placeholder="Your name" required />
            </div>
            <div class="palms-form-row">
                <input type="email" class="palms-form-input" name="email" placeholder="Your business email" required />
            </div>
            <button type="button" class="palms-form-submit" onclick="palmsSubmitInfo(this)">Continue</button>
            <div class="palms-form-error palms-hidden"></div>
        `;
        
        body.appendChild(formContainer);
        body.scrollTop = body.scrollHeight;
        
        return formContainer;
    }
    
    function palmsAddTyping() {
        const msg = document.createElement('div');
        msg.className = 'palms-message typing';
        msg.innerHTML = '<span class="palms-typing-dots"><span></span><span></span><span></span></span>';
        body.appendChild(msg);
        body.scrollTop = body.scrollHeight;
        return msg;
    }
    
    function palmsRemoveTyping() {
        const typing = body.querySelector('.palms-message.typing');
        if (typing) typing.remove();
    }
    
    window.palmsSubmitInfo = async function(button) {
        const form = button.closest('.palms-inline-form');
        const nameInput = form.querySelector('input[name="name"]');
        const emailInput = form.querySelector('input[name="email"]');
        const errorDiv = form.querySelector('.palms-form-error');
        
        const name = nameInput.value.trim();
        const email = emailInput.value.trim();
        
        // Hide previous errors
        errorDiv.classList.add('palms-hidden');
        
        // Basic validation
        if (!name || !email) {
            errorDiv.textContent = 'Please fill in both fields.';
            errorDiv.classList.remove('palms-hidden');
            return;
        }
        
        // Disable form during submission
        button.disabled = true;
        button.textContent = 'Submitting...';
        
        try {
            const response = await fetch(`${API_URL}/submit_info`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ name, email })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Remove the form and show success message
                form.remove();
                palmsAddMessage(data.message, false, 'system');
            } else {
                // Show error and keep form
                errorDiv.textContent = data.message;
                errorDiv.classList.remove('palms-hidden');
                button.disabled = false;
                button.textContent = 'Continue';
                
                if (!data.show_form_again) {
                    form.remove();
                }
            }
        } catch (err) {
            console.error('Info submission error:', err);
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.classList.remove('palms-hidden');
            button.disabled = false;
            button.textContent = 'Continue';
        }
    };
    
    window.palmsSendMessage = async function(event) {
        event.preventDefault();
        
        const message = input.value.trim();
        if (!message) return;
        
        palmsAddMessage(message, true);
        input.value = '';
        
        const typing = palmsAddTyping();
        
        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            palmsRemoveTyping();
            
            const botText = data.response || "Sorry, I couldn't process your request.";
            palmsAddMessage(botText, false);
            
            // Show inline form if requested
            if (data.show_info_form) {
                setTimeout(() => {
                    palmsAddInlineForm();
                }, 800);
            }
            
        } catch (err) {
            palmsRemoveTyping();
            palmsAddMessage("I'm having trouble connecting. Please try again in a moment.", false);
        }
    };
    
    // Initialize chatbot
    function initializeChatbot() {
        palmsMinimize();
        
        // Auto-open after 2.5 seconds on first visit
        setTimeout(() => {
            if (!hasAutoOpened && minimized) {
                hasAutoOpened = true;
                palmsMaximize();
                
                // Auto-minimize after 8 seconds if no interaction
                setTimeout(() => {
                    if (body.children.length <= 2) { // Only welcome message
                        palmsMinimize();
                    }
                }, 8000);
            }
        }, 2500);
    }
    
    // Initialize immediately
    initializeChatbot();
})();
</script>

<?php } ?>
</body>
</html>
