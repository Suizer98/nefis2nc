import os
import subprocess

folder_path = "D:/Sea4cast/Sea4cast/Delft3D-sample/For Hengkek/Sample setup and simulation"
output_path = os.path.join(os.getcwd(), "tests/testdata/")

trih_dat_file = None
trih_def_file = None
trim_dat_file = None
trim_def_file = None
output_trih_file = os.path.join(output_path, "test-trih.nc")
output_trim_file = os.path.join(output_path, "test-trim.nc")

# Iterate through the files in the folder
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.startswith("trih") or filename.startswith("trim") and (filename.endswith(".dat") or filename.endswith(".def")):
            file_path = os.path.join(root, filename)
            if filename.endswith(".dat"):
                if filename.startswith("trih"):
                    trih_dat_file = file_path
                elif filename.startswith("trim"):
                    trim_dat_file = file_path
            elif filename.endswith(".def"):
                if filename.startswith("trih"):
                    trih_def_file = file_path
                elif filename.startswith("trim"):
                    trim_def_file = file_path

print("trih_dat_file:", trih_dat_file)
print("trih_def_file:", trih_def_file)
print("trim_dat_file:", trim_dat_file)
print("trim_def_file:", trim_def_file)

# Check if trih_dat_file and trih_def_file are not None
if trih_dat_file is not None and trih_def_file is not None:
    subprocess.call(["python", "trih2nc.py", trih_dat_file, trih_def_file, output_trih_file])
if trim_dat_file is not None and trim_def_file is not None:
    subprocess.call(["python", "trim2nc.py", trim_dat_file, trim_def_file, output_trim_file])
