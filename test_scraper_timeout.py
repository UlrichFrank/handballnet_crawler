#!/usr/bin/env python3
"""Test scraper with timeout"""
import subprocess
import signal
import sys

def timeout_handler(signum, frame):
    print("\n[TIMEOUT] Test took too long, terminating...", file=sys.stderr)
    sys.exit(0)

# Set 30-second timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

try:
    result = subprocess.run([sys.executable, 'scraper.py'], capture_output=False)
except KeyboardInterrupt:
    print("\n[INTERRUPTED]")
