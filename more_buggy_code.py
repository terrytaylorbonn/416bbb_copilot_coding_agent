def risky_function():
    # Multiple security and error issues for AI to catch
    password = "admin123"  # Hardcoded password - security issue
    file_path = input("Enter file path: ")
    
    # No path validation - security vulnerability
    with open(file_path, 'r') as f:  # Could raise FileNotFoundError
        data = f.read()
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{data}'"
    
    return query

def memory_leak_function():
    # Infinite loop - will cause issues
    big_list = []
    while True:
        big_list.append([0] * 1000000)  # Memory leak
        if len(big_list) > 100:
            break  # This break is unreachable due to memory issues

class UnsafeClass:
    def __init__(self):
        self.data = {}
    
    def unsafe_eval(self, user_input):
        # NEVER use eval with user input!
        return eval(user_input)  # Major security vulnerability
    
    def divide_numbers(self, a, b):
        return a / b  # No zero division check
