from pathlib import Path
import shutil

from wasm_safe_eval._exceptions import WasmtimeNotFoundError

# Default paths
WASMTIME_EXEC: str = str(Path.home() / ".wasmtime" / "bin" / "wasmtime")

def _try_find_wasmtime() -> str|None:
	"""Try to find the wasmtime executable in the default location."""
	if Path(WASMTIME_EXEC).exists():
		return WASMTIME_EXEC
	else:
		wasmtime_in_path: str|None = shutil.which("wasmtime")
		return wasmtime_in_path

# Get the path to the bundled rustpython.wasm
_PACKAGE_DIR = Path(__file__).parent
WASM_RUSTPYTHON_PATH: Path = _PACKAGE_DIR / "rustpython.wasm"