import os
import subprocess
import requests
import json

# folder_path = "D:/Sea4cast/Sea4cast/Delft3D-sample/For Hengkek/Sample setup and simulation"
folder_path = os.path.join(os.getcwd(), "tests/testdata/") # testing in docker container
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

# Post file URL for TrihDataLocation
print("Importing trih data locations")
url = "http://localhost:8000/dms/trih-data-locations/import"
filename = os.path.basename(output_trih_file)
payload = {
    "name": filename,  
    "source": "test",  
    "uploader": "test",  
    "description": "test", 
    "metadata": json.dumps({}),  # Ensure metadata is a JSON string
    "has_inland_data": True,  
    "has_coastal_data": False, 
}
files = {
    "file": (filename, open(output_trih_file, "rb")),
}
response = requests.post(url, data=payload, files=files)
print("Status code for TrihDataLocation:", response.status_code)

# Post file URL for TrihData
print("Importing trih water level data")
url_trih_data = "http://localhost:8000/dms/trih-data/import"
filename_trih_data = os.path.basename(output_trih_file)  # Assuming this is the correct filename
payload_trih_data = {
    "name": filename_trih_data,
    "source": "test",
    "uploader": "test",
    "description": "test",
    "metadata": json.dumps({}),  # Ensure metadata is a JSON string
    "has_inland_data": True,
    "has_coastal_data": False,
}
files_trih_data = {
    "file": (filename_trih_data, open(output_trih_file, "rb")),
}
response_trih_data = requests.post(url_trih_data, data=payload_trih_data, files=files_trih_data)
print("Status code for TrihData:", response_trih_data.status_code)

# Post file URL for TrimData
print("Importing trim 2D data")
url_trim_data = "http://localhost:8000/dms/trim-data/import"
filename_trim_data = os.path.basename(output_trim_file)  # Assuming this is the correct filename
payload_trim_data = {
    "name": filename_trim_data,
    "source": "test",
    "uploader": "test",
    "description": "test",
    "metadata": json.dumps({}),  # Ensure metadata is a JSON string
    "has_inland_data": True,
    "has_coastal_data": False,
}
files_trim_data = {
    "file": (filename_trim_data, open(output_trim_file, "rb")),
}
response_trim_data = requests.post(url_trim_data, data=payload_trim_data, files=files_trim_data)
print("Status code for TrimData:", response_trim_data.status_code)
