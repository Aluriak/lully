
__version__ = '2.0.0'

import os
import sys

# optional dependancies are haunting
def importlog(module: str, reason: str) -> print:
    if os.getenv('LULLY_SILENT_IMPORT_FAILURE', '').lower() not in {'1', 'y', 'yes', 'o', 'oui'}:
        print(f"could not import lully.{module} module because of missing module {reason}", file=sys.stderr)

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

# classy imports
from .funcmore import x as ẍ
