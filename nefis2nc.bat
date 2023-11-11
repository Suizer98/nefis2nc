@echo on

:: Create env
call conda create --name nefis2nc python=2.7 --yes

:: Activate environment
call conda activate nefis2nc

:: Check if the environment activation was successful
if errorlevel 1 (
    echo "Failed to activate the 'nefis2nc' environment."
    pause
    exit /b 1
)

:: Change the current directory to 'stompy'
cd stompy

:: Install the 'stompy' package in editable mode using pip
call pip install -e .

:: Install any .whl files from the 'whls' directory
cd ..
for %%I in (whls\*.whl) do (
    pip install %%I
)

:: Specifically conda install scipy to resolve dll issue
call conda install --yes scipy
call conda install --yes autopep8

:: Deactivate the Conda environment
call conda deactivate
