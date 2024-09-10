import os
import sys
import time
import json
import shutil
import random
import logging
import pydicom
import warnings
import subprocess
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
from nilearn.maskers import NiftiMasker
from datetime import datetime, timedelta
from nilearn.glm.first_level import FirstLevelModel
from nilearn.image import high_variance_confounds, concat_imgs, index_img, resample_img

# Supress Warnings
warnings.filterwarnings("ignore", category=UserWarning)

""" VARIABLE AND PATH SETUP """
# Experiment Design Variables
# pid = 'P001'
# run = '1'
pid = input("Enter Participant ID: ")
run = input("Enter Run Number: ")
block = input("Enter Block Number: ")
session = input("Enter Session Number: ")

while True:

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    static_runNum = '1'  # only accepts 1 (for now)
    dataLength = 24
    nfStartTr = 20
    nfEndTr = 140
    restStartTr = 1
    restEndTr = 19
    repetitionTime = 1.06

    # Initialize Lists
    niiList = []
    activationList = []
    resid_list = []
    nf_scores = []
    z_scoreList = []
    bl_imgs = []
    blNiiList = []

    # Z-score vars
    blMean = 0
    blStd = 0

    # Resid Data
    resid = 0
    dict_for_design = {}
    design = pd.DataFrame
    mask_nii = ()

    # for getting needed Dirs
    directories = []
    dicomParentPath = '/home/rt/sambashare/'
    maskDir = "/home/rt/rt-cloud/projects/adhd_rt/subjects/"
    SecondRecentDicom = ""
    sambashareStartSize = len(os.listdir(dicomParentPath))
    dicom_dir = ""
    # Create output Paths
    output_dirName = f"{pid}_run{run}_nifti_output_{timestamp}"
    output_basePath = "/home/rt/rt-cloud/projects/adhd_rt/nii_outputs"
    macOutdir = '/Users/meghan/rt-cloud/outDir'
    logDir = "/home/rt/rt-cloud/projects/adhd_rt/runLogs/"
    os.makedirs(logDir, exist_ok=True)
    outputLogName = f"/home/rt/rt-cloud/projects/adhd_rt/runLogs/{pid}_s{session}_r{run}_b{block}_output{timestamp}.log"

    """ FUNCTIONS """
    def error_notif(e):
        print(
            "===============================================")
        print(
            "====================ATTENTION==================")
        print(e)
        print(
            "====================ATTENTION==================")
        print(
            "===============================================")

        logging.info(f"====== ATTENTION ======")
        logging.info(e)

        subprocess.run(['mpg123', '/home/rt/rt-cloud/projects/adhd_rt/veryshortnotif.mp3'], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)


    def get_most_recent_mask(directory):  # to select the most recent mask in the directory

        # Get a list of all files in the specified directory
        files_list = [os.path.join(directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]

        # Sort files by modification time (newest first)
        sorted_files = sorted(files_list, key=lambda x: os.path.getmtime(x), reverse=True)

        if not sorted_files:
            error_notif(e)
            print(f"No files found in {directory}.")
            return None

        most_recent_file = sorted_files[0]
        return most_recent_file


    def get_latest_dcm(directory):
        # List comprehension to get all files in the directory that end with '.dcm'
        dcm_files = [os.path.join(directory, file) for file in os.listdir(directory) if
                     os.path.isfile(os.path.join(directory, file)) and file.endswith('.dcm')]

        if not dcm_files:
            return None

        # Return the latest modified .dcm file
        return max(dcm_files, key=os.path.getmtime)


    def dicom_to_nifti(dicom_file, outDir):
        # NOTE: USING -s y CREATES A 3D NII FILE WITH NO 4D DATA
        """
        # Run the command
        subprocess.run(['dcm2niix', '-s', 'y', '-o', outDir, dicom_file]) # stdout=subprocess.PIPE,
                       # stderr=subprocess.STDOUT)

        # grab the nifti file in the dir (ends with .nii) and doesn't follow the syntax of the previous TRs output file
        nifti_files = [file for file in os.listdir(outDir) if
                       (file.endswith(('.nii', '.nii.gz')) and not file.startswith('TR')) and not file.startswith(
                           'maskImg_tr')]

        if len(nifti_files) == 1:
            # grab old nii path
            ogNifti_path = os.path.join(outDir, nifti_files[0])

            # create new nii path
            newNifti_path = os.path.join(outDir, niiFilename)

            # rename
            os.rename(ogNifti_path, newNifti_path)

            return newNifti_path

        elif len(nifti_files) == 0:
            error_notif(e)
            raise ValueError("No NIfTI file found after conversion.")

        else:
            error_notif(e)
            raise ValueError("Expected one NIfTI file, but found multiple.")
        """
        try:
            subprocess.run(['dcm2niix', '-f', f'nii_TR{TR}', '-s', 'y', '-o', outDir, dicom_file])
        except Exception as e:
            error_notif(e)

        nifti = os.path.join(outDir, f'nii_TR{TR}.nii')
        if not os.path.exists(nifti):
            nifti = os.path.join(outDir, f'nii_TR{TR}.nii.gz')
            if not os.path.exists(nifti):
                print(f"Couldn't Find Nifti Img: {nifti}")

        return nifti

    def get_resid(events, mask, niiList):
        # fit masker to mask in subject space
        try:
            masker = NiftiMasker(
                mask_img=mask,
                smoothing_fwhm=None,
                # high_variance_confounds=True,  # regress out things like WM and CSF
            )
            masker.fit()

            # create the model
            fmri_glm = FirstLevelModel(
                t_r=repetitionTime,
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
            logging.info(f"Shape of Most Recent Nii Image: {last_nii.shape}")

            concatNii = concat_imgs([niiList])

            # find confounds
            confounds = pd.DataFrame(high_variance_confounds(concatNii, percentile=1))
            # print("Confounds:")
            # print(confounds)

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
        except Exception as e:
            error_notif(e)
            print("Error in get_resid() func")


    def get_zscore(activation):
        try:
            z_score = (activation - blMean) / blStd  # get z-score (Based on rest data)
            z_scoreList.append(z_score)

            min_score = min(z_scoreList)
            max_score = max(z_scoreList)

            zscore_norm = ((z_score - min_score) / (max_score - min_score)) * 2 - 1

            incrementalMin_score = min(z_scoreList[-25:])
            incrementalMax_score = max(z_scoreList[-25:])

            incremental_zscore_norm = ((z_score - incrementalMin_score) / (
                        incrementalMax_score - incrementalMin_score)) * 2 - 1

            return z_score, zscore_norm, incremental_zscore_norm
        except ValueError as e:
            error_notif(e)
            print("VALUE ERROR IN get_zscore ()")
        except Exception as e:
            error_notif(e)


    def wait_for_key():
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.getch()
        else:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


    def get_most_recent_sambashare_dir(sambashare):
        try:
            for entry in os.scandir(sambashare):
                if entry.is_dir():
                    directories.append(entry.path)
            # Looks for the most recently created directory
            latest_directory = max(directories, key=os.path.getctime)
            dicom_dir = os.path.join(sambashare, latest_directory)
            return dicom_dir
        except Exception as e:
            error_notif(e)
            print("ERROR IN get_most_recent_sambashare_dir()")


    def get_ready_for_data(dicomParentPath):
        # Print Directories
        directories = [entry.path for entry in os.scandir(dicomParentPath) if entry.is_dir()]
        if not directories:
            print("No directories found.")

        print("Available directories:")
        for idx, directory in enumerate(directories, start=1):
            print(f"{idx}. {os.path.basename(directory)}")

        sambashareStartSize = len(os.listdir(dicomParentPath))
        sambashareEndSize = sambashareStartSize
        waitForNew = ""
        MostRecent = ""
        keyPress = ""
        dicomDir = ""
        while True:
            waitForNew = input("Wait For New Dir? (y/n): ")
            if waitForNew == 'y':
                while True:
                    if sambashareStartSize < sambashareEndSize:
                        print("NEW DIRECTORY FOUND! STARTING ...")
                        dicomDir = get_most_recent_sambashare_dir(sambashare=dicomParentPath)
                        print("=============================================================================")
                        print(f"Location of subject's Sambashare Data: {dicomDir}")
                        print("=============================================================================")
                        logging.info("Location of subject's Sambashare Data: \n" + dicomDir + "\n")
                        break
                    else:
                        sambashareEndSize = len(os.listdir(dicomParentPath))
                        print("Waiting for New Sambashare Dir ... ")
                        time.sleep(0.1)
                break
            elif waitForNew == 'n':
                break
            else:
                print("Invalid Choice. Try Again.")
        if waitForNew == 'n':
            while True:
                MostRecent = input("Use Most Recent?: (y/n): ")
                if MostRecent == 'y':
                    dicomDir = get_most_recent_sambashare_dir(sambashare=dicomParentPath)
                    print("=============================================================================")
                    print(f"Location of subject's Sambashare Data: {dicomDir}")
                    print("=============================================================================")
                    logging.info("Location of subject's Sambashare Data: \n" + dicomDir + "\n")
                    break
                elif MostRecent == 'n':
                    break
                else:
                    print("Invalid Choice. Try Again.")
        if MostRecent == 'n':
            while True:
                keyPress = input("Get Most Recent After A Keypress? (y/n): ")
                if keyPress == 'y':
                    print("Press Any Key to Begin.")
                    wait_for_key()
                    dicomDir = get_most_recent_sambashare_dir(sambashare=dicomParentPath)
                    print("=============================================================================")
                    print(f"Location of subject's Sambashare Data: {dicomDir}")
                    print("=============================================================================")
                    logging.info("Location of subject's Sambashare Data: \n" + dicom_dir + "\n")
                    break
                elif keyPress == 'n':
                    break
                else:
                    print("Invalid Choice. Try Again.")
        if keyPress == 'n':
            dicomDirBasename = input("Please type in which directory you want to use: ")
            dicomDir = os.path.join(dicomParentPath, dicomDirBasename)
            print("=============================================================================")
            print(f"Location of subject's Sambashare Data: {dicomDir}")
            print("=============================================================================")
            logging.info("Location of subject's Sambashare Data: \n" + dicomDir + "\n")

        if dicomDir is None:
            error_notif(e)
            print("dicomDir is None")
        return dicomDir


    # Set Up an Output Log
    # Remove the output log from last session
    # Setup Logging
    try:
        if not os.path.exists(outputLogName):
            with open(outputLogName, 'w'):
                pass
    except Exception as e:
        error_notif(e)
        print("Error creating the output log file")

    try:
        logging.basicConfig(filename=f"/home/rt/rt-cloud/projects/adhd_rt/runLogs/{pid}_s{session}_r{run}_b{block}_output{timestamp}.log", level=logging.INFO)
    except Exception as e:
        error_notif(e)
        print("Error configuring output log")

    print("PLEASE TURN SOUND ON IF YOU WANT AUDITORY ERROR NOTIFICATIONS.")

    # Decide How you Would Like to Select the Sambashare Dir, then select it
    dicom_dir = get_ready_for_data(dicomParentPath)

    # Wait for the first Dicom to enter the folder ...
    while True:
        if get_latest_dcm(dicom_dir) is None:
            time.sleep(0.01)
            print("Waiting for the first dicom ... ")
        else:
            print("Dicoms found in the directory. Starting run now ... ")
            break

    """ PRE-RUN SETUP """
    # Get most recent mask
    print("=============================================================================")
    acc_mask_sub_space = get_most_recent_mask(maskDir)
    print(f"Using Mask: {acc_mask_sub_space}")
    logging.info(f"Using Mask: {acc_mask_sub_space}")
    print("=============================================================================")
    # acc_mask_sub_space = "/home/rt/rt-cloud/projects/adhd_rt/subjects/acc_mask_in_sub_space_P001_20240318_140309.nii.gz"

    # Create the output directory if it doesn't exist
    output_dir_path = os.path.join(output_basePath, output_dirName)
    try:
        os.makedirs(output_dir_path, exist_ok=True)
        logging.info(f"Created Output Dir: {output_dir_path}")
    except OSError as e:
        error_notif(e)

    """ CYCLE THROUGH EACH DICOM """
    for TR in range(1, 141):
        start_loop_time = datetime.now()
        print(f"=================================TR{TR}====================================")
        print(f"STARTING TR: {TR}")
        print("==========================================================================")
        logging.info(f"=================================TR{TR}====================================")
        #if TR == 60 or TR == '60':
        #    time.sleep(2)
        #    print("Sleeping")
        # Grab the most recent DICOM
        dicom = get_latest_dcm(dicom_dir)
        basename = os.path.basename(dicom)
        logging.info(f"Grabbed Dicom: {basename}")
        print(basename)
        if dicom == SecondRecentDicom:
            print(" ======== ATTENTION ======== ")
            print("        REUSING DICOM        ")
            print(" ======== ATTENTION ======== ")
        else:
            SecondRecentDicom = dicom

        # Dicom to Nifti Conversion includes extensive error and warning handling due to occasional rejections of a dicom by dcm2niix
        try:
            # Name the output NIfTI file (NOTE: nii.gz is not going to work if doing dcm2niix -s y)
            output_Nii_filename = f"TR{TR}.nii"
            # Convert DICOM to NIfTI
            nii_filePath = dicom_to_nifti(dicom_file=dicom, outDir=output_dir_path)
            # Load the NIfTI image data
            nii_img = nib.load(nii_filePath)

        except Warning as e:
            # protect against warning that a file is too small to do dcm2niix
            if "FileSize < (ImageSize+HeaderSize)" in str(e):
                error_notif(e)
                # end this iteration of the loop
                end_loop_time = datetime.now()
                total_loop_time = end_loop_time - start_loop_time
                if total_loop_time.total_seconds() < repetitionTime:
                    wait_time = timedelta(seconds=repetitionTime) - total_loop_time
                    print(f"WAITING FOR {wait_time} SECONDS.")
                    logging.info(f"WAITING FOR {wait_time} SECONDS.")
                    time.sleep(wait_time.total_seconds())
                elif total_loop_time.total_seconds() > repetitionTime:
                    print("=======================================================")
                    print("CAUTION: THIS LOOP'S PROCESS TIME WAS GREATER THAN THE REPETITION TIME")
                    print(f"Total Time: {total_loop_time}")
                    print("=======================================================")
                    if total_loop_time.total_seconds() > repetitionTime + 2.05:
                        error_notif(e="CAUTION: THIS LOOP'S PROCESS TIME WAS SIGNIFICANTLY GREATER THAN THE REPETITION TIME")
                continue  # Start next TR
            else:  # other warnings should not interrupt the dicom_to_nifti conversion
                output_Nii_filename = f"TR{TR}.nii"
                # Convert DICOM to NIfTI
                nii_filePath = dicom_to_nifti(dicom_file=dicom, outDir=output_dir_path)
                # Load the NIfTI image data
                nii_img = nib.load(nii_filePath)
                logging.info("Successful dicom to nifti conversion")
                print(f"Non-important error raised: {e}")
                logging.info(f"Non-important error raised: {e}")
        except Exception as e:
            error_notif(e)

            print("Skipping this DICOM ... ")
            logging.info("Skipping this DICOM ... ")
            end_loop_time = datetime.now()
            total_loop_time = end_loop_time - start_loop_time
            if total_loop_time.total_seconds() < repetitionTime:
                wait_time = timedelta(seconds=repetitionTime) - total_loop_time
                print(f"WAITING FOR {wait_time} SECONDS.")
                logging.info(f"WAITING FOR {wait_time} SECONDS.")
                time.sleep(wait_time.total_seconds())
            elif total_loop_time.total_seconds() > repetitionTime:
                print("=======================================================")
                print("CAUTION: THIS LOOP'S PROCESS TIME WAS GREATER THAN THE REPETITION TIME")
                print(f"Total Time: {total_loop_time}")
                print("=======================================================")

                if total_loop_time.total_seconds() > repetitionTime + 0.04:
                    error_notif(e="CAUTION: THIS LOOP'S PROCESS TIME WAS SIGNIFICANTLY GREATER THAN THE REPETITION TIME")

            continue  # Start next TR
        tr_onset_time = (int(TR) - 1) * 1.06
        # get Mean Activation and (Put in Array for BL Data Analysis)
        accMasker = input_data.NiftiMasker(mask_img=acc_mask_sub_space,
                                           standardize=True)  # Create the ACC mask for getting mean_activation
        mean_activation = accMasker.fit_transform(nii_img).mean()  # Calculate Mean Activation
        print(f"Mean ROI Activation: {mean_activation}")
        logging.info(f"Mean ROI Activation: {mean_activation}")
        activationList.append(mean_activation)
        activationArray = np.asarray(activationList)

        niiList.append(nii_img)
        if len(niiList) > dataLength:
            niiList.pop(0)
            logging.info(f"Length of Nii List after Cutting: {len(niiList)}")

        if TR < nfStartTr:
            if TR == restStartTr:

                # create "events" object used to build the design matrix by glm.fit() - "One events object expected per run_img"
                logging.info("Created the Event Matrix")
                dict_for_design = {'trial_type': ['rest'], 'onset': [tr_onset_time], 'duration': [1.06]}
                design = pd.DataFrame(dict_for_design)
                logging.info(design)
                # print(design)

                # skip get_resid() as it needs 4d data
            else:
                # Update design Matrix
                dmPos = TR - 1
                design.loc[dmPos] = ['rest', tr_onset_time, 1.06]
                logging.info(design)
                # print(design)


                # get Baseline Residuals
                resid, scoreNf, rawScoreNF, mask_nii = get_resid(events=design, mask=acc_mask_sub_space,
                                                                 niiList=niiList)  # get Resid
                print(f"Resid: {resid}")
                print(f"Total Score: {scoreNf}")
                logging.info(f"Resid: {resid}")
                logging.info(f"Total Score: {scoreNf}")
                logging.info(f'Raw NF Score: {rawScoreNF}')

            if TR == restEndTr:
                blMean = np.mean(activationArray)
                blStd = np.std(activationArray)
                print(" ================================")
                logging.info(" ================================")
                logging.info(" ================================")
                print("BASELINE ACTIVATION STATISTICS:")
                logging.info("BASELINE ACTIVATION STATISTICS:")
                logging.info(" ================================")
                logging.info(" ================================")
                print(" ================================")
                print(f"BaseLine Mean: {blMean}")
                logging.info(f"BaseLine Mean: {blMean}")
                logging.info(f"BaseLine Standard Deviation: {blStd}")
                # determine if results are fitting of normal curve
                statistic, p_value = stats.shapiro(activationArray)  # Perform Shapiro-Wilk test
                alpha = 0.05  # Define significance level
                logging.info("Shapiro-Wilk Test:")
                logging.info(f"Statistic: {statistic}")
                logging.info(f"P-value: {p_value}")
                # Interpret the results
                if p_value > alpha:
                    print("---------------------")
                    print("Sample looks Gaussian")
                    logging.info("Sample looks Gaussian")
                    print("---------------------")

                else:
                    print("-------------------------------")
                    print("Sample does not look Gaussian ")
                    logging.info("Sample does not look Gaussian ")
                    print("-------------------------------")
                print(" ================================")
                print(" ================================")

            # create JSON
            MacRestFilename = f"/Users/meghan/rt-cloud/outDir/rest_tr_{TR}.json"
            # MacRestFilenameBackup = f"/Users/meghan/rt-cloud/outDir/rest_tr_{TR - 1}.json"

            DellRestFilename = f'/home/rt/rt-cloud/outDirMw/rest_tr_{TR}.json'
            DellRestFilenameBackup = f'/home/rt/rt-cloud/outDirMw/rest_tr_{TR - 1}.json'

            # send Empty data, all the rest json files do is tell A_L that another TR of rest has happened
            data = {
                "values": "NaN"
            }

            try:
                # Write data to a JSON file
                with open(DellRestFilename, 'w') as json_file:
                    json.dump(data, json_file)
                    logging.info("JSON created Successfully.")
                    # print(f"Sent JSON FILE: {os.path.basename(DellRestFilename)}")

            except Exception as e:  # if there are errors in the json file, use the 2nd to last as a backup
                error_notif(e)
                DellRestFilename = DellRestFilenameBackup
                try:
                    # Write data to a JSON file
                    with open(DellRestFilename, 'w') as json_file:
                        json.dump(data, json_file)
                except Exception as backup_error:
                    error_notif(e)

            # send JSON
            try:
                # send json
                subprocess.run(['scp', DellRestFilename, f'mac:{MacRestFilename}'])
                logging.info(f"SENT JSON FILE: {DellRestFilename} to MAC: {MacRestFilename} Successfully")
                # print(f"Sent JSON FILE: {os.path.basename(DellRestFilename)}")
            except subprocess.CalledProcessError as e:
                error_notif(e)
                print("SKIPPING THIS TR")
            except Exception as e:
                error_notif(e)
                print("SKIPPING THIS TR")

        elif TR >= nfStartTr:
            # Update Design Matrix
            # time.sleep(0.1)
            dmPos = TR - 1  # current TRs index in the dataframe
            if len(design) < dataLength:
                design.loc[dmPos] = ['nf', tr_onset_time, 1.06]  # adds new row to design data frame
                logging.info("Events")
                logging.info(design)
                # print(design)

            else:
                design.drop(index=design.index[0], axis=0, inplace=True)
                design.loc[dmPos] = ['nf', tr_onset_time, 1.06]  # adds new row to design data frame
                design = design.reset_index(drop=True)  # Resetting index
                logging.info("events")
                logging.info(design)
                # print(design)


            # Get Residual data
            resid, scoreNf, rawScoreNF, mask_nii = get_resid(events=design, mask=acc_mask_sub_space,
                                                             niiList=niiList)  # get Resid
            print(f"Resid: {resid}")
            print(f"Total Score: {scoreNf}")
            logging.info(f"Resid: {resid}")
            logging.info(f"Total Score: {scoreNf}")
            logging.info(f'Raw NF Score: {rawScoreNF}')

            # Get z-score data
            z_score, znorm, znorm_increment = get_zscore(activation=mean_activation)
            print(f"Z-score: {z_score}")
            logging.info(f"Z-score: {z_score}")
            logging.info(f"Normalized Z-Score: {znorm}")
            print(f"Incremental, Normalized Z-Score: {znorm_increment}")
            logging.info(f"Incremental, Normalized Z-Score: {znorm_increment}")

            # create JSON
            MacNfJsonFilename = f"/Users/meghan/rt-cloud/outDir/run{static_runNum}_TR{TR}.json"
            DellNfJsonFilename = f"/home/rt/rt-cloud/outDirMw/run{static_runNum}_TR{TR}.json"
            DellNfJsonFilenameBackup = f"/home/rt/rt-cloud/outDirMw/run{static_runNum}_TR{TR - 1}.json"

            # Change to Whatever we are using for the NF score
            data = {
                "values": znorm_increment
            }

            try:
                # Write data to a JSON file
                with open(DellNfJsonFilename, 'w') as json_file:
                    json.dump(data, json_file)
                    logging.info("JSON created Successfully.")
            except Exception as e:  # if there are errors in the json file, use the 2nd to last as a backup
                error_notif(e)
                DellNfJsonFilename = DellNfJsonFilenameBackup
                try:
                    # Write data to a JSON file
                    with open(DellNfJsonFilename, 'w') as json_file_backup:
                        json.dump(data, json_file_backup)
                        logging.info(f"BACKUP JSON created Successfully.")
                except Exception as backup_error:
                    error_notif(e)
                    print(f"Failed to write data to backup file '{DellNfJsonFilename}': {backup_error}")
                    logging.info(f"Failed to write data to backup file '{DellNfJsonFilename}': {backup_error}")

            # send JSON
            try:
                # send json
                subprocess.run(['scp', DellNfJsonFilename, f'mac:{MacNfJsonFilename}'])
                logging.info(f"SENT JSON FILE: {DellNfJsonFilename} TO MAC: {MacNfJsonFilename}")
                # print(f"Sent JSON FILE: {os.path.basename(DellNfJsonFilename)}")

            except subprocess.CalledProcessError as e:
                error_notif(e)
                print("SKIPPING THIS TR")
                logging.info("SKIPPING THIS TR")
            except Exception as e:
                error_notif(e)

        if TR == nfEndTr:
            # Print z-scores for first {restEndTr} blocks
            try:
                for nii in range(1, nfStartTr):
                    logging.info(f" === Z Info for TR {nii} === ")
                    z_score, znorm, znorm_increment = get_zscore(activationList[int(nii) - 1])
                    logging.info(f"Z-score: {z_score}")
                    logging.info(f"Normalized Z-Score: {znorm}")
                    logging.info(f"Incremental, Normalized Z-Score: {znorm_increment}")
            except Exception as e:
                error_notif(e)
        # adjust for timing of next TR
        end_loop_time = datetime.now()
        total_loop_time = end_loop_time - start_loop_time
        print(f"Total Loop Time: {total_loop_time}")
        logging.info(f"Total Loop Time: {total_loop_time}")
        if total_loop_time.total_seconds() < repetitionTime:
            wait_time = timedelta(seconds=repetitionTime) - total_loop_time
            print(f"WAITING FOR {wait_time} SECONDS.")
            logging.info(f"WAITING FOR {wait_time} SECONDS.")
            time.sleep(wait_time.total_seconds())
        elif total_loop_time.total_seconds() > repetitionTime:
            print(f"EXCEEDING REPETITION TIME BY {total_loop_time.total_seconds() - repetitionTime}")
            if total_loop_time.total_seconds() > repetitionTime + 2.04:
                error_notif(e="CAUTION: THIS LOOP'S PROCESS TIME WAS SIGNIFICANTLY GREATER THAN THE REPETITION TIME")

    print("ALL TRS ARE DONE.")
    print("Performing Last Steps ... ")

    try:
        shutil.rmtree(output_dir_path)
        logging.info(f"Removed Directory: {output_dir_path}")
        print(f"Removed Directory: {output_dir_path}")
    except Exception as e:
        error_notif(e)
    print("Script is done.")

    # calculate new run and block
    if block == '2':
        if run == '1':
            run = '2'
        elif run == '2':
            run = '3'
        else:
            run = '4'
        block = '1'
    elif block == '1':
        block = '2'

    if run > '3' or block > '2':
        print("Finished all Runs and Blocks.")

        break

    print("Review Next Block's Settings:")
    print("-----")
    print(f"PID: {pid}")
    print(f"Run: {run}")
    print(f"Block {block}")
    print(f"Session: {session}")
    print("-----")
    while True:
        accept = input("Accept Settings? (y/n): ")
        if accept == 'y':
            print("Settings Accepted. Starting New Block.")
            break

        elif accept == 'n':
            print("Settings Not Accepted. Please Enter Settings Manually.")
            while True:
                pid = input("Enter Participant ID: ")
                run = input("Enter Run Number: ")
                block = input("Enter Block Number: ")
                session = input("Enter Session Number: ")

                print("Review Next Block's Settings:")
                print("-----")
                print(f"PID: {pid}")
                print(f"Run: {run}")
                print(f"Block {block}")
                print(f"Session: {session}")
                print("-----")

                accept2 = input("Accept Now? (y/n): ")
                if accept2 == 'y':
                    print("Settings Accepted. Starting New Block.")
                    break
                elif accept2 == 'n':
                    print("Ok, Try Again: ")
                else:
                    print("Invalid Choice. Type either 'y' or 'n'. Try again.")
            break

        else:
            print("Invalid Choice. Type either 'y' or 'n'. Try again.")
