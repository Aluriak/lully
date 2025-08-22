
import subprocess
from typing import Optional, Union

def ask(passpath: str, pass_args: Union[list[str], str] = '', *, pass_bin_path: str = '/bin/pass', cmd: str = 'show', log: bool = False) -> Optional[str]:
    if log:
        print('asking for ', passpath)
    pass_args = [] if not pass_args else pass_args  # default and empty vals are empty list
    pass_args = pass_args.split(' ') if isinstance(pass_args, str) else pass_args  # str values are casted to list
    _cmd = [pass_bin_path, cmd, *pass_args, passpath]
    assert not any(s == '' for s in pass_args), pass_args  # happened once, was annoying
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
    elif line == 'Password Store':
        if log:
            print('Invalid command: got the whole passwords hierarchy')
        return None
    return line

