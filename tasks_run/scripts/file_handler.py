def get_most_recent(action: str):
    if action == "dicom":
        print("got most recent dicom")
    elif action == "dicom_dir":
        print("got most recent dicom dir")
    elif action == "roi_mask":
        print("got most recent roi mask")
    else:
        print(f" {action} is not a valid choice for get_most_recent() param: 'action'")

def dicom_to_nifti():
    print("did dicom to nifti")

