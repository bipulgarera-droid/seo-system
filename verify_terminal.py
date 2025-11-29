import sys
import time

print("--- START TERMINAL TEST ---")
print("Printing to STDOUT...", flush=True)
print("Printing to STDERR...", file=sys.stderr, flush=True)
print("--- END TERMINAL TEST ---")
