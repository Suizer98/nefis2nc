import os
import sys
import logging
import subprocess

log = logging.getLogger(__name__)

import ctypes
from ctypes import *


def load_nef_lib():
    """
    Find and load the dll for NEFIS.
    This has to come from a compiled D-WAQ installation.

    Tries these locations:
     $HOME/code/delft/d3d/master/src/lib
     $PYTHON_DIR/lib
     $D3D_HOME/lib

    return None if the DLL cannot be found
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nefis_dll_path = os.path.join(script_dir, "libNefis.so")

    if os.path.exists(nefis_dll_path):
        try:
            return cdll.LoadLibrary(nefis_dll_path)
        except OSError:
            log.warning("Failed to load nefis DLL - read/write not enabled")
            log.warning("Used nefis.dll in the script directory")
            return cdll.LoadLibrary(nefis_dll_path)


_nef_lib = False  # False=> uninitialized, None=> not found


def nef_lib():
    global _nef_lib
    if _nef_lib is False:
        _nef_lib = load_nef_lib()
    return _nef_lib


script_dir = os.path.dirname(os.path.abspath(__file__))
nefis_dll_path = os.path.join(script_dir, "libNefis.so")
nefis_lib = ctypes.CDLL(nefis_dll_path, ctypes.RTLD_GLOBAL)

# Now you can use functions from the loaded library
print(nefis_lib)
print(nefis_lib.Clsnef())
a = cdll.LoadLibrary(nefis_lib)
a.Clsnef()
