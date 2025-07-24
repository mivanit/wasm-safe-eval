WASM_DIR = .wasm

WASM_RUSTPYTHON = $(WASM_DIR)/RustPython

WASM_RUSTPYTHON_BINARY = $(WASM_DIR)/rustpython.wasm

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
	@wasmtime --version >/dev/null 2>&1 || ( \
		echo "Installing wasmtime" && \
		curl -sSf https://wasmtime.dev/install.sh | bash \
	)
	@wasmtime --version


.PHONY: dep-wasm
dep-wasm: $(WASM_RUSTPYTHON_BINARY) dep-wasm-wasmtime
	@echo "Install wasmtime and compile a python interpreter for it"
	

.PHONY: dep-wasm-clean
dep-wasm-clean:
	@echo "Clean up wasm stuff"
	rm -rf $(WASM_RUSTPYTHON)