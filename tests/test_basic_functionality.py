"""Basic functionality tests for wasm-safe-eval."""

import pytest
from wasm_safe_eval.safe_eval import safe_eval, safe_func_call


class TestBasicFunctionality:
    """Test basic functionality of safe_eval and safe_func_call."""

    def test_simple_arithmetic(self):
        """Test that simple arithmetic works."""
        code = "print(2 + 2)"
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "4" in stdout
        assert stderr == ""

    def test_string_operations(self):
        """Test that string operations work."""
        code = """
text = "Hello, World!"
print(text.upper())
print(text.lower())
print(len(text))
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "HELLO, WORLD!" in stdout
        assert "hello, world!" in stdout
        assert "13" in stdout

    def test_list_operations(self):
        """Test that list operations work."""
        code = """
numbers = [1, 2, 3, 4, 5]
print(f"Sum: {sum(numbers)}")
print(f"Length: {len(numbers)}")
print(f"Max: {max(numbers)}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Sum: 15" in stdout
        assert "Length: 5" in stdout
        assert "Max: 5" in stdout

    def test_dictionary_operations(self):
        """Test that dictionary operations work."""
        code = """
data = {"name": "Alice", "age": 30, "city": "New York"}
print(f"Name: {data['name']}")
print(f"Keys: {list(data.keys())}")
print(f"Values: {list(data.values())}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Name: Alice" in stdout
        assert "Keys:" in stdout
        assert "Values:" in stdout

    def test_function_definition(self):
        """Test that function definitions work."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(f"Fibonacci(10): {fibonacci(10)}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Fibonacci(10): 55" in stdout

    def test_class_definition(self):
        """Test that class definitions work."""
        code = """
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name} and I'm {self.age} years old"

person = Person("Bob", 25)
print(person.greet())
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Hello, I'm Bob and I'm 25 years old" in stdout

    def test_loop_operations(self):
        """Test that loops work."""
        code = """
# For loop
total = 0
for i in range(5):
    total += i
print(f"For loop total: {total}")

# While loop
count = 0
while count < 3:
    count += 1
print(f"While loop count: {count}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "For loop total: 10" in stdout
        assert "While loop count: 3" in stdout

    def test_exception_handling(self):
        """Test that exception handling works."""
        code = """
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught exception: {type(e).__name__}")
    result = "undefined"

print(f"Result: {result}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Caught exception: ZeroDivisionError" in stdout
        assert "Result: undefined" in stdout

    def test_list_comprehension(self):
        """Test that list comprehensions work."""
        code = """
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
evens = [x for x in numbers if x % 2 == 0]

print(f"Squares: {squares}")
print(f"Evens: {evens}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Squares: [1, 4, 9, 16, 25]" in stdout
        assert "Evens: [2, 4]" in stdout

    def test_safe_func_call_basic(self):
        """Test basic safe_func_call functionality."""
        code = """
def add(a, b):
    return a + b
"""
        result, stderr, returncode = safe_func_call(code, [3, 4], {}, "add")
        
        assert returncode == 0
        assert result == 7
        assert stderr == ""

    def test_safe_func_call_with_kwargs(self):
        """Test safe_func_call with keyword arguments."""
        code = """
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
"""
        result, stderr, returncode = safe_func_call(code, ["Alice"], {"greeting": "Hi"}, "greet")
        
        assert returncode == 0
        assert result == "Hi, Alice!"

    def test_safe_func_call_complex_return(self):
        """Test safe_func_call with complex return values."""
        code = """
def analyze_list(data):
    return {
        "length": len(data),
        "sum": sum(data),
        "average": sum(data) / len(data) if data else 0,
        "min": min(data) if data else None,
        "max": max(data) if data else None
    }
"""
        result, stderr, returncode = safe_func_call(code, [[1, 2, 3, 4, 5]], {}, "analyze_list")
        
        assert returncode == 0
        assert result["length"] == 5
        assert result["sum"] == 15
        assert result["average"] == 3.0
        assert result["min"] == 1
        assert result["max"] == 5