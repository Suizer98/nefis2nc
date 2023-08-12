# nefis2nc

[[_TOC_]]

## Description

Here is a working nefis2nc repo that based on rustychirs' works:
https://github.com/rustychris/stompy/tree/master that aims to replace 
vs_trih2nc.m and vs_trim2nc.m using Python.

This project is mainly focused on converting Delft3D-FLOW trih and trim output
into more organised netcdf files. The trih2nc.py aims to create a netcdf file 
as close as possible to the output of vs_trih2nc.m, while the trim2nc do the same
for vs_trim2nc.m.

For now the working codes are:
1. trih2nc.py
2. trim2nc.py
3. trih_matplot_class.py (only works on py3++)
4. trim_matplot_class.py (only works on py3++)

## Docker method

### Running docker compose for easier setup

- Dockerfile and docker-compose.yml are created in such a way that you don't need to build environment by yourself, all you need is to run docker's command.
- After cloning this repo, in your terminal simply run:

```
docker-compose up -d  # Start the containers in the background
docker exec -it nefis2nc /bin/bash  # Attach to the container's terminal
```

- After entering docker container:
```
root@7e8c9bfe1c7a:/app# ls
Dockerfile         docker-compose.yml  stompy2   trih2nc.py             trim_matplot_class.py
Dockerfile-window  libs                test.py   trih_matplot_class.py  whls
README.md          requirements.txt    testdata  trim2nc.py

root@7e8c9bfe1c7a:/app# python trih2nc.py
No handlers could be found for logger "utils"
/app/stompy2/stompy/model/delft/nefis_nc.py:93: FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, `arr[np.array(seq)]`, which will result either in an error or a different result.
  value=value[val_slices]
NetCDF file has been created.

root@7e8c9bfe1c7a:/app# cd testdata

root@7e8c9bfe1c7a:/app/testdata# ls
output-trih-final.nc  test  trih-scsmCddb.dat  trih-scsmCddb.def
```

## Preparing environment for local developments

### Prerequisites

- python 2.7 installed on window machine/linux machine
- pip or conda installed

The original stompy repo only supports 'libnefis.so' which works on linux machines,
If you are using window machine, you can attach the nefis.dll file so it works on your end.
We can modify the load_nef_lib function in stompy repo to create magics.

### pip method

- Best to install the netcdf wheel file included in this repo, check requirements.txt for your reference:

```
pip install netCDF4-1.1.7+numpy16-cp27-none-win_amd64.whl
```

- During the stompy's installation, there will be 'No Module found' issues, you should install all dependencies accordingly.
- In your terminal, git clone and cd to stompy repo, then run editable install.
- Alternatively, just go to stompy2 (which all errors resolved) and perform:

```
pip install -e .
```

- Noticed that we have 'nefis.dll' or 'libNefis.so' already in ./libs right? You should copy to: \stompy\stompy\model\delft
1. Make sure the nefis.dll/libNefis.so is same directory with nefis.py (or do your own preferences):
2. Add lines below to load_nef_lib function:

```
def load_nef_lib():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nefis_dll_path = os.path.join(script_dir, 'libNefis.so')

    if os.path.exists(nefis_dll_path):
        try:
            return cdll.LoadLibrary(nefis_dll_path)
        except OSError:
            log.warning("Failed to load nefis DLL - read/write not enabled")
            log.warning("Used nefis.dll in the script directory")
            return None
```

Or you can make it like:

```
    elif sys.platform == 'win32':
        # this is for widow
        basenames = ['nefis.dll']
```

3. In python 2.7, stompy repo might give you error (syntax, spelling) in \stompy\stompy\utils.py and 
\stompy\stompy\io\qnc.py, you can find the edited working files in libs, just copy them to the right path.

```
    except ImportErro:
NameError: name 'ImportErro' is not defined
```

### conda method

- If you are encountering issue like below when running 'trih2nc.py' in virtual env:

```
    from scipy.linalg import _fblas
ImportError: DLL load failed: The network path was not found.

```

- This issue maybe coming from stompy repo's 'nefis_nc.py' which involved scipy library
- Then switching to conda is good option, in your terminal:

```
conda create --name testenv python=2.7
conda activate testenv
conda install scipy
```



