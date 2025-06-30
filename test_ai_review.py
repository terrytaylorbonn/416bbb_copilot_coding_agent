def buggy_function(data):
    # This function has intentional issues for AI to review
    result = data / 0  # Division by zero
    return result.upper()  # Calling method on number

def another_function():
    # No error handling
    with open("nonexistent.txt") as f:
        return f.read()

# Missing documentation and type hints
def process_list(items):
    for i in range(len(items)):
        print(items[i])
