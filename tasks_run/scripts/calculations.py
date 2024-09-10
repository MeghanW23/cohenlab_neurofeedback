import sys
import settings
import pandas as pd
from typing import Union
from nilearn.maskers import NiftiMasker
from datetime import datetime, timedelta
from nilearn.glm.first_level import FirstLevelModel
from nilearn.image import high_variance_confounds, concat_imgs
import numpy as np

def get_time(action: str, time1: datetime = None, time2: datetime = None) -> Union[datetime, timedelta]:
    if action == "get_time":
        now = datetime.now()
        return now

    elif action == "subtract_times":
        if time1 is None:
            print(f"to subtract times using get_time(), you must input a value for param: 'time1'")
            sys.exit(1)

        if time2 is None:
            now = datetime.now()
            total_time: timedelta = now - time1

        else:
            total_time: timedelta = time2 - time1

        return total_time


def get_resid():
    masker = NiftiMasker(mask_img=mask, smoothing_fwhm=None)
    masker.fit()

    # create the model
    fmri_glm = FirstLevelModel(
        t_r=settings.repetitionTime,
        hrf_model='spm + derivative',
        mask_img=masker,
        smoothing_fwhm=6,
        # memory=tmpPath,
        # memory_level=1,
        high_pass=1 / 240,
        noise_model='ols',
        verbose=0,
        n_jobs=-2,
        # use all available CPUs for parallel processing
        signal_scaling=False,
        minimize_memory=False,
        )

    # concatenate the list into 4d nii object
    last_nii = niiList[-1]

    concatNii = concat_imgs([niiList])

    # find confounds
    confounds = pd.DataFrame(high_variance_confounds(concatNii, percentile=1))

    # fit the model with the nifti image and the design matrix
    # for Confounds: The number of rows must match the number of volumes in the respective run_img.
    fmri_glm = fmri_glm.fit(run_imgs=concatNii, events=events, confounds=confounds)

    # get the residual at each voxel in mask
    residVal = masker.fit_transform(fmri_glm.residuals[-1])

    # get the mean resid across all voxels
    resid_mean = residVal.mean()

    resid_list.append(resid_mean)

    nf_score_raw = np.mean(resid_list)
    nf_scores.append(nf_score_raw)
    # Update min and max scores only if necessary
    min_score = min(nf_scores)
    max_score = max(nf_scores)
    nf_score_norm = ((nf_score_raw - min_score) / (max_score - min_score)) * 2 - 1

    return resid_mean, nf_score_norm, nf_score_raw, mask_nii
    print("Error in get_resid() func")


def get_mean_activation():
    print("got mean activation")
