#!/usr/bin/env python3
"""
THE SIMPLEST webhook that actually DOES something
- Receives GitHub events
- Takes a simple action based on the event
"""

import os
from flask import Flask, request, jsonify

app = Flask(__name__)
PORT = int(os.getenv('PORT', 10000))

# Simple counter to track events
event_count = 0

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "events_received": event_count})

@app.route('/webhook', methods=['POST'])
def webhook():
    global event_count
    
    # Get event info
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    data = request.get_json() or {}
    action = data.get('action', 'no-action')
    
    # Increment our counter
    event_count += 1
    
    # DO SOMETHING based on the event type
    if event_type == 'issues':
        if action == 'opened':
            print(f"🐛 New issue created! Total issues opened: {event_count}", flush=True)
            response_message = f"Issue #{event_count} logged!"
        elif action == 'closed':
            print(f"✅ Issue closed! Great work!", flush=True)
            response_message = "Issue closed - nice job!"
        else:
            response_message = f"Issue {action}"
            
    elif event_type == 'pull_request':
        if action == 'opened':
            print(f"🔄 New PR created! Time to review!", flush=True)
            response_message = "PR received - ready for review!"
        elif action == 'closed':
            print(f"🎉 PR merged/closed!", flush=True)
            response_message = "PR closed!"
        else:
            response_message = f"PR {action}"
            
    elif event_type == 'push':
        print(f"📦 Code pushed! New commits incoming!", flush=True)
        response_message = "Push detected - code updated!"
        
    elif event_type == 'ping':
        print(f"🏓 Ping received - webhook is alive!", flush=True)
        response_message = "Pong! Webhook working!"
        
    else:
        print(f"📡 Unknown event: {event_type} - {action}", flush=True)
        response_message = f"Received {event_type} event"
    
    # Always log the basic info
    print(f"Event #{event_count}: {event_type} - {action}", flush=True)
    
    # Return a response
    return jsonify({
        "status": "processed",
        "event": event_type,
        "action": action,
        "message": response_message,
        "total_events": event_count
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Simple Action Webhook",
        "status": "ready to take action",
        "events_processed": event_count,
        "actions": {
            "issues": "Logs new issues and closures",
            "pull_request": "Announces PRs",
            "push": "Detects code pushes",
            "ping": "Responds to health checks"
        }
    })

if __name__ == '__main__':
    print(f"🚀 Simple Action Webhook starting on port {PORT}", flush=True)
    print("Ready to take action on GitHub events!", flush=True)
    app.run(host='0.0.0.0', port=PORT, debug=False)
