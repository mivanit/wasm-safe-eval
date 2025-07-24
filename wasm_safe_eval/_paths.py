from pathlib import Path
import shutil
import sys
from importlib.resources import files

from wasm_safe_eval._exceptions import RustPythonWasmNotFoundError

# Default paths
WASMTIME_EXEC: str = str(Path.home() / ".wasmtime" / "bin" / "wasmtime")

def _try_find_wasmtime() -> str|None:
    """Try to find the wasmtime executable in the default location."""
    if Path(WASMTIME_EXEC).exists():
        return WASMTIME_EXEC
    else:
        wasmtime_in_path: str|None = shutil.which("wasmtime")
        return wasmtime_in_path

def get_rustpython_wasm_path() -> Path:
    """Get the path to the bundled rustpython.wasm file."""
    output: Path = Path(str(files("wasm_safe_eval").joinpath("rustpython.wasm")))
    if not output.exists():
        raise RustPythonWasmNotFoundError("The rustpython.wasm file could not be found. this is a bug in the wasm-safe-eval package, please report it at https://github.com/mivanit/wasm-safe-eval/issues")
    return output

WASM_RUSTPYTHON_PATH: Path = get_rustpython_wasm_path()