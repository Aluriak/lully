
import subprocess
from typing import Optional

def ask(passpath: str, pass_args: str = '', *, pass_bin_path: str = '/bin/pass', cmd: str = 'show', log: bool = False) -> Optional[str]:
    print('asking for ', passpath)
    _cmd = [pass_bin_path, cmd, *pass_args.split(' '), passpath]
    if log:
        print(f"Will access password with `{' '.join(_cmd)}`…")
    proc = subprocess.Popen(_cmd, stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    lines = stdout.decode().strip().splitlines(False)
    line = lines[0] if lines else None
    if line and line.startswith('Error: ') and line.endswith(' is not in the password store.'):
        if log:
            print(line)
        return None
    return line

