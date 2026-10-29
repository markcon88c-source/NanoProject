import sys
import time

def progress_bar(current, total, width=40):
    percent = current / total
    filled = int(width * percent)
    bar = "#" * filled + "-" * (width - filled)

    sys.stdout.write(f"\r[{bar}] {percent:.1%}")
    sys.stdout.flush()

# Demo
total = 100
for i in range(total + 1):
    progress_bar(i, total)
    time.sleep(0.05)

print("\nDone!")
