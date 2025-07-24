WASM_DIR = .wasm

WASM_RUSTPYTHON = $(WASM_DIR)/RustPython

WASM_RUSTPYTHON_BINARY = wasm_safe_eval/rustpython.wasm

# Read the tag straight from pyproject.toml
RUSTPYTHON_TAG := $(shell uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['rustpython-tag'])")

$(WASM_RUSTPYTHON):
	git clone --depth 1 --branch $(RUSTPYTHON_TAG) \
		--single-branch https://github.com/RustPython/RustPython.git \
		$(WASM_RUSTPYTHON)
	rm -rf $(WASM_RUSTPYTHON)/.git

$(WASM_RUSTPYTHON_BINARY): $(WASM_RUSTPYTHON)
	rustup target add wasm32-wasip1
	cd $(WASM_RUSTPYTHON) && cargo build --release --target wasm32-wasip1 --features="freeze-stdlib"
	cp $(WASM_RUSTPYTHON)/target/wasm32-wasip1/release/rustpython.wasm $(WASM_RUSTPYTHON_BINARY)

# https://github.com/bytecodealliance/wasmtime/
.PHONY: dep-wasm-wasmtime
dep-wasm-wasmtime:
	@echo "Checking for wasmtime ..."
	@wasmtime --version

.PHONY: build
build: $(WASM_RUSTPYTHON_BINARY)
	@echo "Building wasm_safe_eval ..."
	uv build

.PHONY: clean
clean:
	rm -rf $(WASM_DIR)

.PHONY: check
check:
	uv run ruff check wasm_safe_eval --fix
	uv run ruff format wasm_safe_eval
	uv run mypy wasm_safe_eval
	uv run pytest tests/