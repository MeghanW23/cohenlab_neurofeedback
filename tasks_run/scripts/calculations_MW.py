import sys
import settings
from typing import Union
from datetime import datetime, timedelta
from nilearn import input_data, image, masking
from nilearn.maskers import NiftiMasker
from nilearn.glm.first_level import FirstLevelModel
import nibabel as nib
import pandas as pd
import log
from nilearn.image import high_variance_confounds, concat_imgs
import numpy as np
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


def get_resid(dictionary: dict, block: int, trial: int):
    # get data necessary
    roi_mask: str = dictionary['whole_session_data']['roi_mask_path']
    niiList: list = dictionary[f"block{block}"]["nii_list"]
    resid_list: list = dictionary[f"block{block}"]["resid_list"]
    nf_scores: list = dictionary[f"block{block}"]["nf_scores"]
    current_nii_img: str = dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"]

    current_nii_img = nib.load(current_nii_img)
    events: dict = update_sliding_design_matrix(design=dictionary[f"block{block}"]["event_dict"], trial=trial)
    dictionary[f"block{block}"]["event_dict"]: dict = events # update in data dictionary

    masker = NiftiMasker(mask_img=roi_mask,smoothing_fwhm=None)
    masker.fit()

    # create the model
    fmri_glm = FirstLevelModel(
        t_r=settings.repetitionTime,
        hrf_model='spm + derivative',
        mask_img=masker,
        smoothing_fwhm=6,
        high_pass=1 / 240,
        noise_model='ols',
        verbose=0,
        n_jobs=-2,
        signal_scaling=False,
        minimize_memory=False,
    )

    if len(niiList) >= settings.WINDOW_SIZE:
        niiList.pop(0)
        niiList.append(current_nii_img)
    else:
        niiList.append(current_nii_img)

    # Log the number of images being concatenated
    log.print_and_log(f"Concatenating {len(niiList)} images.")

    # Concatenate selected images into a single 4D Nifti object
    concatNii = concat_imgs(niiList)
    print(f"length nii list: {len(niiList)}")

    # find confounds (assumed that high_variance_confounds is precomputed or generated here)
    confounds = pd.DataFrame(high_variance_confounds(concatNii, percentile=1))

    # fit the model with the concatenated nifti image and the design matrix
    fmri_glm = fmri_glm.fit(run_imgs=concatNii, events=events, confounds=confounds)

    # Get predicted data from the model
    predicted_data = fmri_glm.predicted(run_imgs=concatNii, events=events, confounds=confounds)

    # Transform the actual data to voxel space
    actual_data = masker.transform(concatNii)

    # Calculate residuals manually as the difference between actual and predicted data
    residuals = actual_data - predicted_data

    # Get the mean residual across all voxels
    resid_mean = residuals.mean()

    # Store residual mean for tracking
    resid_list.append(resid_mean)

    # Calculate neurofeedback score (raw and normalized)
    nf_score_raw = np.mean(resid_list)
    nf_scores.append(nf_score_raw)

    # Normalize neurofeedback score between -1 and 1
    min_score = min(nf_scores)
    max_score = max(nf_scores)
    nf_score_norm = ((nf_score_raw - min_score) / (max_score - min_score)) * 2 - 1

    dictionary[f"block{block}"][f"trial{trial}"]["nf_score"]: float = nf_score_norm

    # Return relevant outputs: mean residual, neurofeedback scores, and the mask used
    return dictionary


def get_mean_activation(roi_mask: str, nifti_image_path: str) -> float:
    nii_img = nib.load(nifti_image_path) # load nifti image from nifti path
    log.print_and_log(f"nii_img_dtpye: {nii_img.get_data_dtype()}")

    accMasker = input_data.NiftiMasker(mask_img=roi_mask, standardize=True)  # Create the ACC mask for getting mean_activation

    mean_activation = accMasker.fit_transform(nii_img).mean()  # Calculate Mean Activation
    log.print_and_log(f"Mean ROI Activation: {mean_activation}")

    return mean_activation

def update_sliding_design_matrix(design: pd.core.frame.DataFrame, trial: int) -> dict:
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