"""Error handling and edge case tests for wasm-safe-eval."""

import subprocess
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from wasm_safe_eval.safe_eval import safe_eval, safe_func_call, _NoResultSentinel
from wasm_safe_eval._exceptions import WasmtimeNotFoundError, RustPythonWasmNotFoundError
from wasm_safe_eval._paths import _try_find_wasmtime, get_rustpython_wasm_path


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_syntax_error_handling(self):
        """Test that syntax errors are properly handled."""
        code = """
def broken_function(
    # Missing closing parenthesis and colon
print("This should fail")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode != 0
        assert stderr != ""

    def test_runtime_error_handling(self):
        """Test that runtime errors are properly handled."""
        code = """
undefined_variable + 5
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode != 0
        assert stderr != ""

    def test_infinite_loop_timeout(self):
        """Test that infinite loops don't hang indefinitely."""
        code = """
while True:
    pass
"""
        # This test depends on wasmtime's timeout behavior
        # The subprocess should eventually terminate or timeout
        with pytest.raises(subprocess.TimeoutExpired):
            stdout, stderr, returncode = safe_eval(code, timeout=1)
        
#     def test_memory_intensive_operation(self):
#         """Test handling of memory-intensive operations."""
#         code = """
# # Try to allocate a large amount of memory
# try:
#     big_list = [0] * (10**8)  # 100 million integers
#     print(f"SUCCESS: Allocated list of size {len(big_list)}")
# except MemoryError:
#     print("BLOCKED: MemoryError")
# except Exception as e:
#     print(f"ERROR: {type(e).__name__}: {e}")
# """
#         stdout, stderr, returncode = safe_eval(code)
        
#         # Should either fail with memory error or be blocked
#         if returncode == 0:
#             assert "SUCCESS:" not in stdout or "BLOCKED:" in stdout or "ERROR:" in stdout

    def test_deep_recursion(self):
        """Test handling of deep recursion."""
        code = """
def recursive_function(n):
    if n <= 0:
        return 0
    return recursive_function(n - 1)

try:
    result = recursive_function(10000)  # Very deep recursion
    print(f"SUCCESS: Recursion completed with result {result}")
except RecursionError:
    print("BLOCKED: RecursionError")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should either complete or fail with recursion error
        # Both outcomes are acceptable for security

    def test_wasmtime_not_found_error(self):
        """Test WasmtimeNotFoundError when wasmtime is not available."""
        code = "print('Hello')"
        
        with patch('wasm_safe_eval.safe_eval._try_find_wasmtime', return_value=None):
            with pytest.raises(WasmtimeNotFoundError):
                safe_eval(code)

    def test_safe_func_call_no_result(self):
        """Test safe_func_call when function doesn't return anything."""
        code = """
def print_only():
    print("This function doesn't return anything")
"""
        result, stderr, returncode = safe_func_call(code, [], {}, "print_only")
        
        # Should return _NoResultSentinel when no result is available
        assert isinstance(result, _NoResultSentinel)

    def test_safe_func_call_invalid_json_output(self):
        """Test safe_func_call when function output is not valid JSON."""
        code = """
def invalid_json_func():
    # This will cause JSON parsing to fail
    print("Not JSON output")
    return "some result"
"""
        result, stderr, returncode = safe_func_call(code, [], {}, "invalid_json_func")
        
        # Should return _NoResultSentinel and have error in stderr
        assert isinstance(result, _NoResultSentinel)
        assert "Error parsing stdout" in stderr

    def test_safe_func_call_function_not_found(self):
        """Test safe_func_call when the specified function doesn't exist."""
        code = """
def existing_function():
    return "I exist"
"""
        result, stderr, returncode = safe_func_call(code, [], {}, "non_existing_function")
        
        # Should fail because function doesn't exist
        assert returncode != 0
        assert stderr != ""

    def test_safe_func_call_function_error(self):
        """Test safe_func_call when the function raises an exception."""
        code = """
def error_function():
    raise ValueError("This function always fails")
"""
        result, stderr, returncode = safe_func_call(code, [], {}, "error_function")
        
        # Should fail with non-zero return code
        assert returncode != 0
        assert stderr != ""

    def test_empty_code_execution(self):
        """Test execution of empty code."""
        code = ""
        stdout, stderr, returncode = safe_eval(code)
        
        # Empty code should execute successfully with no output
        assert returncode == 0
        assert stdout == ""

    def test_whitespace_only_code(self):
        """Test execution of whitespace-only code."""
        code = "   \n\t   \n   "
        stdout, stderr, returncode = safe_eval(code)
        
        # Whitespace-only code should execute successfully
        assert returncode == 0

    def test_large_output_handling(self):
        """Test handling of large output."""
        code = """
# Generate large output
for i in range(1000):
    print(f"Line {i}: " + "x" * 100)
"""
        stdout, stderr, returncode = safe_eval(code)
        
        # Should handle large output (may be truncated but shouldn't crash)
        assert returncode == 0
        assert len(stdout) > 1000  # Should have substantial output

    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        code = """
unicode_text = "Hello 世界! 🌍 Привет мир! 🚀"
print(unicode_text)
print(f"Length: {len(unicode_text)}")
"""
        stdout, stderr, returncode = safe_eval(code)
        
        assert returncode == 0
        assert "Hello 世界!" in stdout
        assert "🌍" in stdout
        assert "Привет мир!" in stdout
        assert "🚀" in stdout

    def test_safe_func_call_with_complex_args(self):
        """Test safe_func_call with complex argument types."""
        code = """
def process_data(data_list, options_dict, multiplier=2):
    result = []
    for item in data_list:
        if options_dict.get("double", False):
            result.append(item * multiplier)
        else:
            result.append(item)
    return result
"""
        args = [[1, 2, 3, 4]]
        kwargs = {"options_dict": {"double": True}, "multiplier": 3}
        
        result, stderr, returncode = safe_func_call(code, args, kwargs, "process_data")
        
        assert returncode == 0
        assert result == [3, 6, 9, 12]