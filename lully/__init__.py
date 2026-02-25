
__version__ = '3.3.0'

import os
import sys
from typing import Optional

has_import_error = False
# optional dependancies are haunting
from .shellmore import envvar_is_false
def importlog(module: str, reason: Optional[str]):
    if envvar_is_false('LULLY_SILENT_IMPORT_FAILURE'):
        print(f"could not import lully.{module} module because of missing module {reason}", file=sys.stderr)
        global has_import_error
        has_import_error = True


try:
    from .debug import *
except ImportError as err:
    importlog('debug', err.name)
try:
    from . import texty
except ImportError as err:
    importlog('texty', err.name)



from . import colop, hashing, passwd, sql, string, url, xml
from .subs import multi_subs_by_match, multi_subs_by_regex, multi_replace
from .fief import fief
from .colop import *
from .files import *
from .binary import *
from .logger import *
from .random import *
from .popglob import popglob
from .hashing import *
from .funcmore import t_iden, iden, has_param, x, y
from .itermore import *
from .shellmore import is_repl, envvar_is_true, user_inputs_yes
from .confiseur import Bonbon, Confiseur
from .printmore import *
from .dateutils import *
from .collections import *

# internal dependencies
from .kotlin import *

# classy imports
from .funcmore import x as ẍ, y as ÿ


if has_import_error:
    print("(to remove missing import logging, set LULLY_SILENT_IMPORT_FAILURE=1)", file=sys.stderr)

if envvar_is_true('LULLY_ENABLE_REPL', default=False):
    popglob(in_repl=True)
    print("Lully populated the REPL context with aliases. To prevent that behavior, set LULLY_ENABLE_REPL=0", file=sys.stderr)
