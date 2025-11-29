import time

def log_debug(message):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("debug.log", "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"✓ Logged: {message}")
    except Exception as e:
        print(f"✗ Logging failed: {e}")

# Test logging
log_debug("TEST: Direct log_debug function call")
print("\nCheck debug.log now - should see 'TEST' entry")
