"""Observe PID 1's shutdown state; never infer shutdown from input failure."""
import subprocess


def stopping():
    try:
        result = subprocess.run(['/usr/bin/systemctl','is-system-running'],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            timeout=.5,universal_newlines=True)
        return result.stdout.strip() == 'stopping'
    except (OSError,subprocess.TimeoutExpired): return False
