import sys
import os

def test_print():
    # Test different print methods
    print("1. Basic print", flush=True)
    sys.stdout.write("2. sys.stdout.write\n")
    sys.stdout.flush()
    os.write(1, b"3. os.write to stdout\n")
    sys.stderr.write("4. sys.stderr.write\n")
    os.write(2, b"5. os.write to stderr\n")

def test_imports():
    print("Testing imports:", flush=True)
    try:
        import anthropic
        print("✓ anthropic imported", flush=True)
        print(f"anthropic version: {anthropic.__version__}", flush=True)
    except Exception as e:
        print(f"✗ anthropic import failed: {str(e)}", flush=True)

if __name__ == "__main__":
    print("Script starting...", flush=True)
    test_print()
    test_imports()
    print("Script completed", flush=True) 