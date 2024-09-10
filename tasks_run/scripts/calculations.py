import sys
import settings
from typing import Union
from datetime import datetime, timedelta
from nilearn import input_data, image, masking
import nibabel as nib
import log
def get_time(action: str, time1: datetime = None, time2: datetime = None) -> Union[datetime, timedelta]:
    if action == "get_time":
        now = datetime.now()
        return now

    elif action == "subtract_times":
        if time1 is None:
            log.print_and_log(f"to subtract times using get_time(), you must input a value for param: 'time1'")
            sys.exit(1)

        if time2 is None:
            now = datetime.now()
            total_time: timedelta = now - time1

        else:
            total_time: timedelta = time2 - time1

        return total_time


def get_resid():
    print("got resid")


def get_mean_activation(roi_mask: str, nifti_image_path: str):
    nii_img = nib.load(nifti_image_path) # load nifti image from nifti path
    print(f"nii_img_dtpye: {nii_img.get_data_dtype()}")

    accMasker = input_data.NiftiMasker(mask_img=roi_mask, standardize=True)  # Create the ACC mask for getting mean_activation

    mean_activation = accMasker.fit_transform(nii_img).mean()  # Calculate Mean Activation
    log.print_and_log(f"Mean ROI Activation: {mean_activation}")

