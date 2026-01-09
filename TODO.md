# TODO: Codebase Fixes for wasm_safe_eval

## Critical

### 1. Template Injection via `func_name`
**Location:** [safe_eval.py:141](wasm_safe_eval/safe_eval.py#L141)

`func_name` is inserted directly into the code template without validation:
```python
result = {func_name}(*args, **kwargs)
```

**Fix:** Add regex validation before using func_name:
```python
import re

if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', func_name):
    raise ValueError(f"Invalid function name: {func_name!r}")
```

### 2. Overly Broad Exception Handling
**Location:** [safe_eval.py:155](wasm_safe_eval/safe_eval.py#L155)

```python
except Exception as e:  # Catches KeyboardInterrupt, SystemExit, MemoryError
```

**Fix:** Catch specific exception:
```python
except json.JSONDecodeError as e:
    stderr += f"\nError parsing stdout: {e}"
```

## Medium

### 3. No Timeout Validation
**Location:** [safe_eval.py:131](wasm_safe_eval/safe_eval.py#L131)

Negative, zero, or invalid timeout values are passed directly to subprocess.

**Fix:** Add validation:
```python
if timeout is not None and timeout <= 0:
    raise ValueError(f"timeout must be positive, got {timeout}")
```

### 4. Wasmtime Path Check Incomplete
**Location:** [_paths.py:13](wasm_safe_eval/_paths.py#L13)

Only checks `Path.exists()`, not if file is executable.

**Fix:** Check executability:
```python
import os

def _try_find_wasmtime() -> str | None:
    if Path(WASMTIME_EXEC).is_file() and os.access(WASMTIME_EXEC, os.X_OK):
        return WASMTIME_EXEC
    return shutil.which("wasmtime")
```

### 5. `__init__.py` Export Bug
**Location:** [__init__.py](wasm_safe_eval/__init__.py)

- `install_wasmtime` in `__all__` but never imported
- `safe_eval` listed twice

**Fix:**
```python
__all__ = [
    "safe_eval",
    "safe_func_call",
]
```

## Low

### 6. Type Annotation Mismatch
**Location:** [safe_eval.py:25,134](wasm_safe_eval/safe_eval.py#L25)

Returns `SafeEvalResult`/`FuncCallResult` but annotated as `tuple[...]`

**Fix:**
```python
def safe_eval(...) -> SafeEvalResult:
def safe_func_call(...) -> FuncCallResult:
```

### 7. Platform Check
**Location:** [safe_eval.py](wasm_safe_eval/safe_eval.py)

Only install script checks platform, not runtime.

**Fix:** Add assertion:
```python
import platform
assert platform.system() == "Linux", "wasm_safe_eval only supports Linux"
```

## Tests to Add

```python
class TestInputValidation:
    def test_invalid_func_name_special_chars(self):
        with pytest.raises(ValueError, match="Invalid function name"):
            safe_func_call("def f(): pass", [], {}, "func;inject")

    def test_invalid_func_name_empty(self):
        with pytest.raises(ValueError, match="Invalid function name"):
            safe_func_call("def f(): pass", [], {}, "")

    def test_invalid_func_name_spaces(self):
        with pytest.raises(ValueError, match="Invalid function name"):
            safe_func_call("def f(): pass", [], {}, "func name")

    def test_valid_func_name_with_underscore(self):
        code = "def my_func_2(): return 42"
        result, _, returncode = safe_func_call(code, [], {}, "my_func_2")
        assert returncode == 0
        assert result == 42

    def test_negative_timeout(self):
        with pytest.raises(ValueError, match="timeout must be positive"):
            safe_func_call("def f(): pass", [], {}, "f", timeout=-1)

    def test_zero_timeout(self):
        with pytest.raises(ValueError, match="timeout must be positive"):
            safe_func_call("def f(): pass", [], {}, "f", timeout=0)
```
