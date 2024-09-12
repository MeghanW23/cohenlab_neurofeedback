import sys
import settings
from typing import Union
from datetime import datetime, timedelta
from nilearn.input_data import NiftiMasker
import nibabel as nib
import pandas as pd
import Logger
from nilearn.glm.first_level import FirstLevelModel
from nilearn.image import high_variance_confounds, concat_imgs
from nilearn import image
import numpy as np

def get_time(action: str, time1: datetime = None, time2: datetime = None) -> Union[datetime, timedelta]:
    if action == "get_time":
        now = datetime.now()
        return now

    elif action == "subtract_times":
        if time1 is None:
            Logger.print_and_log(f"to subtract times using get_time(), you must input a value for param: 'time1'")
            sys.exit(1)

        if time2 is None:
            now = datetime.now()
            total_time: timedelta = now - time1

        else:
            total_time: timedelta = time2 - time1

        return total_time
def get_mean_activation(roi_mask: str, nifti_image_path: str) -> float:
    nii_img = nib.load(nifti_image_path)  # load nifti image from nifti path

    accMasker = NiftiMasker(mask_img=roi_mask, standardize=True)  # Create the ACC mask for getting mean_activation

    mean_activation = accMasker.fit_transform(nii_img).mean()  # Calculate Mean Activation
    Logger.print_and_log(f"Mean ROI Activation: {mean_activation}")

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

    Logger.print_and_log(f"length design matrix: {len(design['trial_type'])}")
    Logger.print_and_log(design)

    return design

def get_resid(dictionary: dict, block: int, trial: int):
    # Get necessary data from dictionary
    roi_mask: str = dictionary['whole_session_data']['roi_mask_path']
    niiList: list = dictionary[f"block{block}"]["nii_list"]
    resid_list: list = dictionary[f"block{block}"]["resid_list"]
    nf_scores: list = dictionary[f"block{block}"]["nf_scores"]
    current_nii_img_path: str = dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"]

    nii_img = image.load_img(current_nii_img_path)

    # Update the sliding design matrix for the current trial
    events: dict = update_sliding_design_matrix(design=dictionary[f"block{block}"]["event_dict"], trial=trial)
    dictionary[f"block{block}"]["event_dict"] = events  # update in data dictionary

    # Create Nifti masker using the ROI mask
    masker = NiftiMasker(mask_img=roi_mask, smoothing_fwhm=None)
    masker.fit()

    # Create the FirstLevelModel for fMRI analysis
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

    # Maintain a sliding window of images (remove the oldest if we reach window size)
    if len(niiList) >= settings.WINDOW_SIZE:
        niiList.pop(0)  # Remove oldest Nifti image
    niiList.append(nii_img)  # Append current Nifti image

    # Log number of images being concatenated
    Logger.print_and_log(f"Concatenating {len(niiList)} images.")

    # Concatenate the Nifti images into a single 4D image
    concatNii = concat_imgs(niiList)

    Logger.print_and_log(f"Length of nii list: {len(niiList)}")

    # Find confounds (like high variance confounds for the concatenated image)
    confounds = pd.DataFrame(high_variance_confounds(concatNii, percentile=1))

    # Fit the model to the concatenated Nifti image using the design matrix
    fmri_glm = fmri_glm.fit(run_imgs=concatNii, events=events, confounds=confounds)

    residVal = masker.fit_transform(fmri_glm.residuals[-1])

    # Get the mean residual across all voxels
    resid_mean = residVal.mean()
    dictionary[f"block{block}"][f"trial{trial}"]["resid_mean"] = resid_mean

    # Append the mean residual to the residual list for tracking
    resid_list.append(resid_mean)

    # Calculate neurofeedback score (raw score as the mean of all residuals)
    nf_score_raw = np.mean(resid_list)
    nf_scores.append(nf_score_raw)

    # Normalize the neurofeedback score between -1 and 1
    min_score = min(nf_scores)
    max_score = max(nf_scores)
    nf_score_norm = ((nf_score_raw - min_score) / (max_score - min_score)) * 2 - 1

    # Store normalized neurofeedback score in the dictionary
    dictionary[f"block{block}"][f"trial{trial}"]["nf_score"] = nf_score_norm

    # Return updated dictionary with neurofeedback score and residual information
    return dictionary
