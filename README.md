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

Tech stacks:
![Tech stacks](https://skillicons.dev/icons?i=python,docker,ubuntu,bash,anaconda)

For now the working codes are:
1. trih2nc.py
2. trim2nc.py
3. listener.py

## Running conversion scripts
1. Install every dependencies needed inside Conda environment, see [conda method](#conda-method).
2. Go to listener.py, make sure your folder contain Delft3D output, then edit variable as you wishes:
```
folder_path = "D:/Sea4cast/Sea4cast/Delft3D-sample/For Hengkek/Sample setup and simulation"
output_path = os.path.join(os.getcwd(), "tests/testdata/")
```
3. In your terminal or any possible executable ways, run 
```
python listener.py
```

## Setting up Docker Ubuntu environment

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

root@7e8c9bfe1c7a:/app# python trih2nc.py datfile deffile outputfile
No handlers could be found for logger "utils"
/app/stompy2/stompy/model/delft/nefis_nc.py:93: FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, `arr[np.array(seq)]`, which will result either in an error or a different result.
  value=value[val_slices]
NetCDF file has been created.
```

## Preparing Conda environment on Window machine

### Prerequisites

- python 2.7 installed on window machine/linux machine
- conda installed

The original stompy repo only supports 'libnefis.so' which works on linux machines,
If you are using window machine, you can attach the nefis.dll file so it works on your end.
We can modify the load_nef_lib function in stompy repo to create magics.

### conda method

Best to run this script in conda environment if without Docker, to setup the env run 'nefis2nc.bat' on your window machine:

```
nefis2nc.bat
```

You may open the batch script with editor to see the manual steps to setup conda env, you need to open cmd.exe for 'nefis2nc' directory:
```
conda create --name nefis2nc python=2.7
conda activate nefis2nc
cd stompy

call pip install -e .

cd ..
for %%I in (whls\*.whl) do (
    pip install %%I
)

conda install --yes scipy
conda install --yes autopep8
```
