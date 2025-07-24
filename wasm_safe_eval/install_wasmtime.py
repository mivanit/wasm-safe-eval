#!/usr/bin/env python3
"""Install wasmtime binary for wasm-safe-eval package."""

import platform
import subprocess
import shutil
import sys

from wasm_safe_eval._exceptions import PlatformNotSupportedError
from wasm_safe_eval._paths import _try_find_wasmtime


_DIV: str = "=" * shutil.get_terminal_size().columns
SOURCE_URL: str = "https://wasmtime.dev/install.sh"


def install_wasmtime() -> None:
    f"""Install wasmtime from {SOURCE_URL}"""
    # see if it's already installed
    wasmtime_exec: str | None = _try_find_wasmtime()
    if wasmtime_exec:
        print(f"wasmtime already installed at: {wasmtime_exec}\nexiting.")
        return

    # Check platform
    if platform.system() != "Linux":
        msg: str = f"wasm-safe-eval only supports Linux. Current platform: {platform.system() = }"
        if platform.system() == "Windows":
            msg += "\nHint: You can use WSL (Windows Subsystem for Linux) on Windows."
        raise PlatformNotSupportedError(msg)

    cmd: str = f"curl -sSf {SOURCE_URL} | bash"

    # check with the user
    print(
        "This will install the `wasmtime` binary for wasm-safe-eval package, via the following executed in shell:"
    )
    print(cmd)
    print("You can also run this manually. Continue? [y/N]")
    if input().strip().lower() != "y":
        print("Installation aborted.")
        sys.exit(0)

    # Run the official wasmtime installer
    print("Installing wasmtime...")
    print(_DIV)

    print(f"$ {cmd}")
    print(_DIV)
    result: subprocess.CompletedProcess = subprocess.run(cmd, shell=True)

    # check and return
    if result.returncode != 0:
        print(_DIV, file=sys.stderr)
        raise RuntimeError(f"Failed to install wasmtime: {result.stderr}")

    print(_DIV)
    print(
        "wasmtime installed successfully! You may need to restart your terminal for changes to take effect."
    )


if __name__ == "__main__":
    install_wasmtime()
