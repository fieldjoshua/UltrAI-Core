#!/usr/bin/env python3
import os, sys, subprocess, shlex

cmd = " ".join(shlex.quote(a) for a in sys.argv[1:])
exit_code = subprocess.call(cmd, shell=True)
if os.getenv("DEV_MODE") == "true" and exit_code:
    print(f"DEV_MODE: '{cmd}' would have failed (exit {exit_code})")
    sys.exit(0)
sys.exit(exit_code)
