class WasmtimeNotFoundError(Exception):
    """Raised when wasmtime executable is not found."""
    pass


class PlatformNotSupportedError(Exception):
    """Raised when running on non-Linux platform."""
    pass