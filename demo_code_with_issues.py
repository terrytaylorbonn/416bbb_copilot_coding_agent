#!/usr/bin/env python3
"""
Sample code with intentional issues for AI review demo
"""

def authenticate_user(username, password):
    # Simple authentication function
    if username == "admin" and password == "123456":
        return True
    
    # Check database
    users = get_users_from_db()
    for user in users:
        if user.username == username and user.password == password:
            return True
    
    return False

def get_users_from_db():
    # Simulate database call
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = 1")
    results = cursor.fetchall()
    conn.close()
    return results

def process_payment(amount, card_number):
    # Process payment
    if len(card_number) == 16:
        print(f"Processing payment of ${amount} with card {card_number}")
        return {"status": "success", "transaction_id": "12345"}
    else:
        return {"status": "error", "message": "Invalid card number"}
