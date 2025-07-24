# wasm_safe_eval

# IMPORTANT NOTE: USE THIS AT YOUR OWN RISK, I HAVE NO IDEA IF IT'S ACTUALLY SAFE

This is a tool which lets you run untrusted Python code in a WebAssembly environment, using [RustPython](https://github.com/RustPython/RustPython) and [Wasmtime](https://wasmtime.dev/). The idea is that this is more lightweight than having a docker container or something -- although I have no idea if it actually is.


# Installation

```
pip install git+https://github.com/mivanit/wasm-safe-eval.git
```

This will install the python package, which contains the prebuilt `rustpython.wasm` binary.

You will need to install [wasmtime](https://wasmtime.dev/), which can be done with:

```bash
python -m wasm_safe_eval.install_wasmtime
```

which simply runs:

```bash
curl -sSf https://wasmtime.dev/install.sh | bash
```

# Usage

## Just running code

You will need to figure out on your own how you want to add input or extract output from the function. `safe_eval` returns a tuple of `(stdout, stderr, returncode)`.

```python
from wasm_safe_eval import safe_eval

result = safe_eval("""
def main():
	print("Hello, world!")
main()
""")
result
print(result.stdout)  # Should print "Hello, world!"
```


## Function calls

We provide a special interface for running a potentially unsafe function, assuming the inputs and outputs can be serialized to/from JSON. This works like:

```python
from wasm_safe_eval import safe_func_call

code = """
def add(a, b):
	return a + b
"""

result = safe_func_call(
	code = code,
	args = [1, 2],
	kwargs = {},
	func_name = "add",	
)
assert result.result == 3
assert result.returncode == 0
```