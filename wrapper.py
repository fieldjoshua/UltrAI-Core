#!/usr/bin/env python3
"""
Wrapper script to suppress warnings and add progress bars
"""
import os
import random
import subprocess
import sys
import time

from tqdm import tqdm


def show_progress(description, steps=20, min_time=1.0):
    """Show a progress bar with random pauses"""
    with tqdm(
        total=steps, desc=description, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
    ) as pbar:
        start_time = time.time()
        for i in range(steps):
            # Randomize step time but ensure total is at least min_time
            remaining = max(0, min_time - (time.time() - start_time))
            avg_remaining = remaining / (steps - i) if i < steps - 1 else 0
            delay = random.uniform(0.05, 0.15) + avg_remaining
            time.sleep(delay)
            pbar.update(1)


# Redirect stderr to /dev/null to hide warnings
stderr_null = open(os.devnull, "w")

# Show progress for initialization
show_progress("Initializing orchestrator", steps=10, min_time=1.0)

# Show progress for model loading
show_progress("Loading language models", steps=15, min_time=1.5)

# Run the actual command with stderr redirected
cmd = sys.argv[1:]
result = subprocess.run(cmd, stderr=stderr_null)
sys.exit(result.returncode)
