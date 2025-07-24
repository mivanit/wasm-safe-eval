WASM_DIR = .wasm

WASM_RUSTPYTHON = $(WASM_DIR)/RustPython

WASM_RUSTPYTHON_BINARY = wasm_safe_eval/rustpython.wasm

$(WASM_RUSTPYTHON):
	mkdir -p $(WASM_RUSTPYTHON)
	git clone https://github.com/RustPython/RustPython.git $(WASM_RUSTPYTHON) --depth 1

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

.PHONY: check
check:
	uv run ruff check wasm_safe_eval --fix
	uv run ruff format wasm_safe_eval
	uv run mypy wasm_safe_eval
	uv run pytest wasm_safe_eval/tests