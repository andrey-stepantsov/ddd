.PHONY: all clean

all: hello

hello: hello.c
	@echo "🔨 Compiling hello.c..."
	@gcc -Wall -o hello hello.c
	@echo "✅ Build successful! Run './hello' to test."

clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -f hello
	@echo "✓ Clean complete."
