# Hello World - Project Makefile
# This Makefile builds the hello program and includes DDD commands

# === Build Targets ===

.PHONY: all hello clean help

all: hello

hello: hello.c
	@echo "🔨 Compiling hello.c..."
	@gcc -Wall -o hello hello.c
	@echo "✅ Build successful! Run './hello' to test."

clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -f hello
	@echo "✓ Clean complete."

help:
	@echo "Build Commands:"
	@echo "  make              - Build hello program"
	@echo "  make all          - Build hello program"
	@echo "  make hello        - Build hello program"
	@echo "  make clean        - Clean all artifacts"
	@echo ""
	@make -f .ddd/Makefile ddd-help 2>/dev/null || echo "  (DDD not installed - run bootstrap-ddd.sh)"

# === Include DDD Commands ===
# This optional line adds DDD commands (ddd-daemon-bg, ddd-build, etc.)
# Remove this line if you prefer standalone usage: make -f .ddd/Makefile <target>
-include .ddd/Makefile
