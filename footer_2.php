<?php
/**
 * The template for displaying the footer.
 *
 * Contains the body & html closing tags.
 *
 * @package HelloElementor
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
<!-- PALMS Chatbot - Direct Theme Integration -->
<?php if (!wp_is_mobile() || true) { // Show on all devices ?>
<!-- PALMS Chatbot Widget - Standalone HTML -->
<!-- Add this code anywhere in your WordPress site (footer.php, custom HTML widget, etc.) -->

<style>
/* PALMS Chatbot - Standalone CSS - No WordPress conflicts */
#palms-standalone-chatbot * {
    box-sizing: border-box !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

#palms-standalone-chatbot {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: column !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    /* Size and styling will be controlled by JavaScript */
}

/* Minimized state */
#palms-standalone-chatbot.minimized {
    width: 64px !important;
    height: 64px !important;
    border-radius: 50% !important;
    background: #2F5D50 !important;
    cursor: pointer !important;
    align-items: center !important;
    justify-content: center !important;
}

#palms-standalone-chatbot.minimized:hover {
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

#palms-standalone-chatbot.minimized .palms-chat-icon {
    display: flex !important;
}

#palms-standalone-chatbot.minimized .palms-header {
    display: none !important;
}

/* Body - FIXED HEIGHT */
.palms-body {
    flex: 1 !important;
    padding: 16px !important;
    overflow-y: auto !important;
    height: 400px !important;
    max-height: 400px !important;
    min-height: 400px !important;
    background: #FAFBFC !important;
}

.palms-body::after {
    content: "" !important;
    display: table !important;
    clear: both !important;
}

/* Messages */
.palms-message {
    margin-bottom: 12px !important;
    padding: 12px 16px !important;
    border-radius: 18px !important;
    max-width: 80% !important;
    word-wrap: break-word !important;
    font-size: 1rem !important;
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
    font-size: 1rem !important;
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
    font-size: 0.85rem !important;
    color: #6E7B85 !important;
    text-align: center !important;
    line-height: 1.2 !important;
}

/* Hidden states */
.palms-hidden {
    display: none !important;
}
</style>

<div id="palms-standalone-chatbot" class="minimized">
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
        <div class="palms-disclaimer">Disclaimer: This chatbot provides information for general purposes only and does not constitute professional advice.</div>
    </form>
</div>

<script>
// PALMS Standalone Chatbot JavaScript
(function() {
    let minimized = true;
    let optionsShownOnce = false;
    let hasAutoOpened = false;
    
    const widget = document.getElementById('palms-standalone-chatbot');
    const body = widget.querySelector('.palms-body');
    const form = widget.querySelector('.palms-input-form');
    const input = widget.querySelector('.palms-input');
    
    window.palmsMinimize = function() {
        minimized = true;
        
        // Nuclear CSS override for minimize with smooth transition
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
        
        // Nuclear CSS override for maximize - FIXED HEIGHT with smooth transition
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
        
        // Force body to have fixed height with scroll
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
                palmsAddMessage("Hello. I am PALMS assistant and here to help you.", false);
            }, 400);
        }
    };
    
    function palmsAddMessage(text, isUser = false) {
        const msg = document.createElement('div');
        msg.className = 'palms-message ' + (isUser ? 'user' : 'bot');
        msg.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        body.appendChild(msg);
        
        // Add clearfix
        const clearfix = document.createElement('div');
        clearfix.style.clear = 'both';
        clearfix.style.height = '0';
        body.appendChild(clearfix);
        
        body.scrollTop = body.scrollHeight;
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
    
    window.palmsSendMessage = async function(event) {
        event.preventDefault();
        
        const message = input.value.trim();
        if (!message) return;
        
        palmsAddMessage(message, true);
        input.value = '';
        
        const typing = palmsAddTyping();
        
        try {
            const response = await fetch('https://onpalms-chatbot-api.onrender.com/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            palmsRemoveTyping();
            
            const botText = data.response || "Sorry, I couldn't process your request.";
            palmsAddMessage(botText, false);
            
        } catch (err) {
            palmsRemoveTyping();
            palmsAddMessage("I'm having trouble connecting. Please try again in a moment.", false);
        }
    };
    
    // Initialize chatbot after all functions are defined
    function initializeChatbot() {
        // Set correct initial minimized state
        palmsMinimize();
        
        // Auto-open chatbot after 2.5 seconds on first visit
        setTimeout(() => {
            if (!hasAutoOpened && minimized) {
                hasAutoOpened = true;
                palmsMaximize();
                
                // Auto-minimize after 8 seconds if user hasn't interacted
                setTimeout(() => {
                    if (!optionsShownOnce && body.children.length <= 2) { // Only welcome message
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

<!-- Copy everything from the standalone file I created -->
<?php } ?>
</body>
</html>
