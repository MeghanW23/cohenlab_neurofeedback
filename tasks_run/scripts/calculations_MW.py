import sys
import settings
from typing import Union
from datetime import datetime, timedelta
from nilearn.input_data import NiftiMasker
import nibabel as nib
import pandas as pd
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


def get_resid(dictionary: dict):
    return dictionary

def get_mean_activation(roi_mask: str, nifti_image_path: str) -> float:
    nii_img = nib.load(nifti_image_path)  # load nifti image from nifti path

    accMasker = NiftiMasker(mask_img=roi_mask, standardize=True)  # Create the ACC mask for getting mean_activation

    mean_activation = accMasker.fit_transform(nii_img).mean()  # Calculate Mean Activation
    log.print_and_log(f"Mean ROI Activation: {mean_activation}")

    return mean_activation

def update_sliding_design_matrix(design: pd.DataFrame, trial: int) -> dict:
    tr_onset_time = (int(trial) - 1) * settings.repetitionTime

    if trial == 1:
        des_mat = {'trial_type': ['rest'], 'onset': [tr_onset_time], 'duration': [settings.repetitionTime]}
        design = pd.DataFrame(des_mat)

    else:
        if len(design['trial_type']) >= settings.WINDOW_SIZE:
            design = design.iloc[1:]  # Remove the first row (oldest)

    if 1 < trial < settings.START_NF_TRIAL:
        new_row = pd.DataFrame({'trial_type': ['rest'], 'onset': [tr_onset_time], 'duration': [settings.repetitionTime]})
        design = pd.concat([design, new_row], ignore_index=True)

    elif trial >= settings.START_NF_TRIAL:
        new_row = pd.DataFrame({'trial_type': ['neurofeedback'], 'onset': [tr_onset_time], 'duration': [settings.repetitionTime]})
        design = pd.concat([design, new_row], ignore_index=True)

    log.print_and_log(f"length design matrix: {len(design['trial_type'])}")
    log.print_and_log(design)

    return design