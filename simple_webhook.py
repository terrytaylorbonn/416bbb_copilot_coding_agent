# simple_webhook.py
#!/usr/bin/env python3
"""
Ultra Simple Webhook Handler for Render.com
Just logs what it receives - nothing fancy
"""

import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Render.com requires PORT env var
PORT = int(os.getenv('PORT', 10000))

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok", "message": "Simple webhook is running"})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Dead simple webhook - just log what we get"""
    
    # Get basic info
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    
    try:
        data = request.get_json()
        action = data.get('action', 'no-action') if data else 'no-data'
        
        # Just log it with more detail
        print(f"🔔 Webhook received: {event_type} - {action}", flush=True)
        print(f"📦 Full payload keys: {list(data.keys()) if data else 'None'}", flush=True)
        
        # Simple response
        return jsonify({
            "status": "received", 
            "event": event_type,
            "action": action,
            "timestamp": "received"
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "name": "Simple Webhook Handler",
        "status": "running",
        "endpoints": ["/health", "/webhook"]
    })

if __name__ == '__main__':
    print(f"🚀 Starting simple webhook on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
