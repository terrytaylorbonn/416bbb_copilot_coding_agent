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

def unsafe_file_reader(filename):
    # New buggy function to test AI review
    file = open(filename, 'r')  # No try/except, file never closed
    content = file.read()
    return content.upper()  # What if content is None?

def divide_numbers(a, b):
    # Another function with issues
    return a / b  # No check for b == 0

def process_list_unsafely(items):
    # New function with multiple issues for AI to detect
    result = items[0]  # IndexError if list is empty
    for i in range(len(items)):  # Inefficient iteration
        if items[i] == None:  # Should use 'is None'
            continue
        result = result + items[i]  # Type issues if mixed types
    return result

def sql_injection_risk(user_input):
    # Security vulnerability for AI to catch
    query = f"SELECT * FROM users WHERE name = '{user_input}'"  # SQL injection risk
    return query

def memory_leak_function():
    # Memory issues
    big_list = []
    while True:  # Infinite loop - will cause memory issues
        big_list.append([0] * 1000000)
        if len(big_list) > 100:
            break  # This break is unreachable due to memory issues
    return big_list
