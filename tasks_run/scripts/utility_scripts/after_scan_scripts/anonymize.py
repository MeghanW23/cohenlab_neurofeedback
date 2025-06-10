import os
import pydicom
import sys 

# Load the DICOM DIR
if len(sys.argv) != 3:
    print("Usage: python anonymize.py <path> <pid>")
    sys.exit(1)

# Get the path from the command-line arguments
dicom_dir_path = sys.argv[1]
print(f"The provided dicom path is: {dicom_dir_path}")

# Get the path from the command-line arguments
pid: str = sys.argv[2]
print(f"The provided PID is: {pid}")

for i, path in enumerate(os.listdir(dicom_dir_path)):
    dicom_path: str = os.path.join(dicom_dir_path, path)
    if not os.path.isfile(dicom_path): 
        print(f"NOT A FILE: {dicom_path}")
    else:
        name = os.path.basename(dicom_path)
        dir = os.path.dirname(dicom_path)


        try:
            ds = pydicom.dcmread(dicom_path)
        except OSError as e:
            print(f"Error: {e}")
            print(f"Cannot Anonymize File: {dicom_path}")

        tags_to_anonymize = [
            (0x0010, 0x0010),  # Patient's Name
            (0x0010, 0x0020),  # Patient ID
            (0x0010, 0x0030),  # Patient's Birth Date
            (0x0010, 0x0040),  # Patient's Sex
            (0x0008, 0x0090),  # Referring Physician's Name
        ]

        # Remove or anonymize sensitive tags
        for tag in tags_to_anonymize:
            if i == 0: 
                print(ds[tag])
            if tag in ds:
                del ds[tag]

        # Save the anonymized DICOM file
        new_dir = os.path.join(os.path.dirname(dir), f"ANONYMIZED_{pid}")
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        ds.save_as(os.path.join(new_dir, name))

print(f"Done. Anonymized DICOM Dir at: {new_dir}")