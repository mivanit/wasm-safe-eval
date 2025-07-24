import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from wasm_safe_eval._paths import WASM_RUSTPYTHON_PATH, _try_find_wasmtime
from wasm_safe_eval._exceptions import WasmtimeNotFoundError



def safe_eval(
    code: str,
    wasmtime_exec: str | None = None,
    wasm_rustpython_path: Path = WASM_RUSTPYTHON_PATH,
) -> tuple[str, str, int]:
    """safely execute a Python code snippet in a WebAssembly RustPython environment.

    # Parameters:
    - `code : str`
		code to execute
    - `wasmtime_exec : str`
		(defaults to `WASMTIME_EXEC`)
    - `wasm_rustpython_path : Path`
		(defaults to `WASM_RUSTPYTHON_PATH`)

    # Returns:
    - `tuple[str, str, int]`
		(stdout, stderr, returncode)
    """
    
    # Get wasmtime executable if not provided
    if wasmtime_exec is None:
        wasmtime_exec = _try_find_wasmtime()
        if wasmtime_exec is None:
            raise WasmtimeNotFoundError(
                "wasmtime executable not found.\n"
                "Please install it by running: python -m wasm_safe_eval.install_wasmtime"
            )

    # Write code to temporary file for secure execution
    temp_filename: str
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
        tf.write(code)
        tf.flush()
        temp_filename = tf.name
    
    try:
        cmd: list[str] = [
            wasmtime_exec,
            # "--dir=-",  # do not expose any host directories
            str(wasm_rustpython_path),
            temp_filename,
        ]
        
        completed: subprocess.CompletedProcess[str] = subprocess.run(
            cmd,
            text=True,  # decode to str instead of bytes
            capture_output=True,  # capture both stdout and stderr
            check=False,  # do not raise on non‑zero exit
        )
    finally:
        # Clean up temporary file
        os.unlink(temp_filename)

    return completed.stdout, completed.stderr, completed.returncode


FUNC_CALL_TEMPLATE: str = '''
# implemented function
# ==============================
{func_code}
# ==============================

# wrapper
# ==============================
import json


# get args and kwargs from JSON

args: list = json.loads("""
{args}
""")

kwargs: dict = json.loads("""
{kwargs}
""")

# call the function
result = {func_name}(*args, **kwargs)
print(json.dumps(result))
'''


class _NoResultSentinel:
    """Sentinel object to indicate no result was returned from the function call."""

    def __init__(self):
        self.message = "No result returned from function call."

    def __repr__(self):
        return f"_NoResultSentinel({self.message!r})"

    def __str__(self):
        return self.message


def safe_func_call(
    code: str,
    args: list,
    kwargs: dict,
    func_name: str = "f",
    wasmtime_exec: str | None = None,
    wasm_rustpython_path: Path = WASM_RUSTPYTHON_PATH,
) -> tuple[Any, str, int]:
    """safely call a function in a WebAssembly RustPython environment."""

    code_augmented: str = FUNC_CALL_TEMPLATE.format(
        func_code=code,
        args=json.dumps(args),
        kwargs=json.dumps(kwargs),
        func_name=func_name,
    )

    stdout, stderr, returncode = safe_eval(
        code_augmented,
        wasmtime_exec=wasmtime_exec,
        wasm_rustpython_path=wasm_rustpython_path,
    )

    result = _NoResultSentinel()
    try:
        if returncode == 0 and stdout:
            result = json.loads(stdout)
    except Exception as e:
        stderr += f"\nError parsing stdout: {e}"

    return (
        result,
        stderr,
        returncode,
    )
