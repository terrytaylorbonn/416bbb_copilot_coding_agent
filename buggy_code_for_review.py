def calculate_average(numbers):
    # This function has several issues for AI to catch
    total = 0
    for i in range(len(numbers)):  # Should use enumerate or direct iteration
        total += numbers[i]
    
    return total / len(numbers)  # No check for empty list - division by zero!

def process_user_input():
    # No error handling for invalid input
    user_data = input("Enter a number: ")
    result = int(user_data)  # Could raise ValueError
    return result * 2

class DataProcessor:
    def __init__(self):
        pass  # Empty constructor - could be removed
    
    def process_data(self, data):
        # No type hints, no docstring
        result = []
        for item in data:
            if item > 0:  # What if item is not a number?
                result.append(item * 2)
        return result

# Global variable - generally not recommended
GLOBAL_COUNTER = 0

def increment_counter():
    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1  # Thread safety issues
