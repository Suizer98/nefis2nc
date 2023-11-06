import os
import ctypes
from ctypes import *

def load_nef_lib():
    """
    Find and load the DLL for NEFIS.
    This has to come from a compiled D-WAQ installation.

    Tries these locations:
     $HOME/code/delft/d3d/master/src/lib
     $PYTHON_DIR/lib
     $D3D_HOME/lib

    return None if the DLL cannot be found
    """
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # nefis_dll_path = os.path.join(script_dir, "libs", "libNefis.so")
    nefis_dll_path = os.path.join(script_dir, "libs", "nefis.dll")

    if os.path.exists(nefis_dll_path):
        try:
            return cdll.LoadLibrary(nefis_dll_path)
        except OSError:
            log.warning("Failed to load nefis DLL - read/write not enabled")
            log.warning("Used nefis.dll in the script directory")
            return ctypes.CDLL(nefis_dll_path)

_nef_lib = False  # False => uninitialized, None => not found

def nef_lib():
    global _nef_lib
    if _nef_lib is False:
        _nef_lib = load_nef_lib()
    return _nef_lib

# Load the nefis library
nefis_lib = nef_lib()

if nefis_lib:
    # Use dir() to list available functions
    available_functions = [func for func in dir(nefis_lib) if callable(getattr(nefis_lib, func))]

    for func in available_functions:
        print("Function: {}".format(func))
