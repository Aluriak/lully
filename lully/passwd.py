
import subprocess
from typing import Optional

def ask(passpath: str, *, pass_bin_path: str = '/bin/pass', log: bool = False) -> Optional[str]:
    cmd = [pass_bin_path, 'show', passpath]
    if log:
        print(f"Will access password with `{' '.join(cmd)}`…")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    lines = stdout.decode().strip().splitlines(False)
    return lines[0] if lines else None

