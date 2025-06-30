#!/usr/bin/env python3
"""
Simple test file for GitHub Actions demo
"""

def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def greet(name="World"):
    """Generate a greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("🧪 Running simple tests...")
    
    # Test addition
    result = add(2, 3)
    assert result == 5, f"Expected 5, got {result}"
    print("✅ Addition test passed")
    
    # Test multiplication
    result = multiply(4, 5)
    assert result == 20, f"Expected 20, got {result}"
    print("✅ Multiplication test passed")
    
    # Test greeting
    result = greet("GitHub Actions")
    expected = "Hello, GitHub Actions!"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ Greeting test passed")
    
    print("🎉 All tests passed! GitHub Actions is working!")
