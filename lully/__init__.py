
__version__ = '2.2.0'

import os
import sys
from typing import Optional

has_import_error = False
# optional dependancies are haunting
def importlog(module: str, reason: Optional[str]):
    if os.getenv('LULLY_SILENT_IMPORT_FAILURE', '').lower() not in {'1', 'y', 'yes', 'o', 'oui'}:
        print(f"could not import lully.{module} module because of missing module {reason}", file=sys.stderr)
        global has_import_error
        has_import_error = True


try:
    from .debug import *
except ImportError as err:
    importlog('debug', err.name)



from . import colop, hashing, passwd, sql, string, url, xml
from .subs import multi_subs_by_match, multi_subs_by_regex, multi_replace
from .fief import fief
from .colop import *
from .files import *
from .binary import *
from .logger import *
from .random import *
from .hashing import *
from .funcmore import *
from .itermore import *
from .confiseur import Bonbon, Confiseur
from .printmore import *
from .dateutils import *

# internal dependencies
from .kotlin import *

# classy imports
from .funcmore import x as ẍ, y as ÿ


if has_import_error:
    print("(to remove missing import logging, set LULLY_SILENT_IMPORT_FAILURE=1)", file=sys.stderr)

