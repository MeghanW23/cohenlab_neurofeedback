# Impact of Stimulants and In-Scanner Motion on fMRI Neurofeedback and Task Performance in ADHD
This repository outlines the study protocol for the project: *Impact of Stimulants and In-Scanner Motion on fMRI Neurofeedback and Task Performance in ADHD* conducted by [Alexander Cohen's Lab of Translational Neuroimaging at Boston Children's Hospital](https://bchcohenlab.com/).

**Important Notes:**
* As this project is in development, not all material used in this project may be included in the README.md yet and aspects of this project may have changed. For questions on the project material or any other aspect of this project, please see the contact information below.
* Any Private Health Information (PHI) is pushed to private storage locations to protect participants' PHI and to minimize issues related to managing large amounts of data on GitHub. Project users must provide their own data.

**Contact Information:**
* Emails:
   * [Meghan.Walsh2@childrens.harvard.edu](mailto:Meghan.Walsh2@childrens.harvard.edu)
   * [wmeghan0809@gmail.com](mailto:wmeghan0809@gmail.com)
   * [Sofia.Heras@childrens.harvard.edu](mailto:sofia.heras@childrens.harvard.edu)
   * [sofiheras1@gmail.com](mailto:sofiheras1@gmail.com)
* LinkedIn:
   * [Meghan Walsh](https://www.linkedin.com/in/meghan-walsh-359789260/)
   * [Sofia Heras](https://www.linkedin.com/in/sofia-heras-5a557622b/)

## Project Overview
Attention-deficit/hyperactivity disorder (ADHD) is a complex condition often treated with stimulant medications, which have proven effective in managing symptoms like inattention and impulsivity but can cause side effects. The question remains whether non-pharmacological interventions, such as neurofeedback, can replicate or enhance the benefits of stimulants in individuals with ADHD.  Additionally, functional magnetic resonance imaging (fMRI) studies in ADHD research have often been hindered by unaccounted motion artifacts, leading to potential inaccuracies in measuring brain activity. Our research aims to address these gaps by improving the methods used to correct for motion in neuroimaging studies and by exploring the potential of neurofeedback as an alternative or complementary treatment for ADHD.
### Our research has two objectives:
#### (1) Address the Impact of Motion on fMRI Results Involving Individuals with ADHD: 
We will investigate and address the impact of motion artifacts in fMRI research, particularly in ADHD studies where motion has previously been unmeasured or inadequately accounted for. By incorporating new technology to better capture and correct for motion, and by repeating experiments with this improved capability, we aim to refine our understanding of how motion affects neuroimaging results. 

#### (2) Address the Feasibility of Neurofeedback as a Method to Replicate the Effects of Stimulants in ADHD
Our study will explore whether neurofeedback can replicate or enhance the effects of stimulant medications in individuals with ADHD. By comparing brain activity and performance on attention tasks during neurofeedback and stimulant conditions, we aim to determine if neurofeedback can serve as an alternative or complement to stimulants in managing ADHD symptoms. This investigation will contribute to the literature by evaluating the potential of neurofeedback to replicate or amplify the benefits typically associated with stimulant treatments, without the side effects associated with stimulant drugs.
By addressing the impact of motion artifacts and investigating the effects of neurofeedback compared to stimulant medications, our study seeks to refine neuroimaging techniques and expand the understanding of ADHD treatment options. If neurofeedback can replicate or amplify the effects of stimulants on brain activity and attention, it may offer a promising, non-invasive treatment with fewer side effects. Ultimately, this research has the potential to advance both methodological practices in ADHD research and therapeutic approaches for individuals with the condition.

## Prerequisites 
Before you begin, ensure you have met the following requirements:

- **Architecture and OS Requirements**: Our project is designed for macOS machines running on ARM64 architecture. Running the project on other machines will likely require minor adjustments.
- **Docker Installation**: Ensure [Docker](https://docs.docker.com/engine/install/) is installed and configured on your machine.
- **FSL Installation**: [FSL](https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/FslInstallation.html) must be installed on your machine for brain registration, visualization, and analysis.
- **VNC Viewer Installation**: To display our tasks to participants, our primary Docker image utilizes a headless virtual display through `Xvfb` and `x11vnc`. To access this virtual display, we recommend the free TigerVNC Viewer from [TigerVNC](https://tigervnc.org/). While macOS includes a built-in VNC Viewer, its performance is often inferior. Other free VNC Viewers are also available online. *This project can be adapted for use with X11 forwarding; however, we have found that using a VNC has yielded better results.*
- **E3 Access**: Ensure you have access to the Enkefalos-v3 Cluster (E3) at Boston Children’s Hospital, which is a centrally administered secured high-performance computing (HPC) cluster dedicated to research computing and computational studies on both patient health information (PHI) and non-PHI data. You must have access to the Boston Children's Hospital VPN and have a valid CHID to access. 
- **Samba File Server**: Users must create a [Samba File Server](https://ubuntu.com/tutorials/install-and-configure-samba#1-overview) to facilitate DICOM data transfer from the MRI and the user's machine.
- **Dual Monitors**: It is recommended to work with two monitors, as our tasks treat the MRI's screen, which projects tasks and videos to in-scanner participants, as a second monitor.

*Note: It is also recommended that you install [Rectangle](https://rectangleapp.com/) to move and resize windows in macOS using keyboard shortcuts or snap areas. This makes it easier to send the task window from your macbook screen's display to the mri monitor display.*

## Setup 
1. Assure your machine(s) meet the necessary prerequites to run this project. 
2. Clone the Repo: ```git clone https://github.com/MeghanW23/cohenlab_neurofeedback```
3. To run a docker container:
- navigate to the `docker_run` directory in your local repository
- run ```./task_executor.sh```, select the task you would like to run, and input any requested information. *There will likely be extra steps prompted by the script before you can run. In this case, simply follow the instructions provided by the scripts.*
   
## File Structure
- **README.md**: A markdown file that provides an overview of the project.
- **docker_run**: Includes scripts and configuration files necessary for running the Docker container. This directory includes:
  - **task_executor.sh**: A script that prompts the user to select a task and runs the corresponding script within the Docker container.
  - **startup.sh**: A script designed to set up the project environment within the Docker container and run task scripts based on the information given from the `task_executor.sh` script.
  - **test_pygame.py**: A Python script used for testing functionalities related to the Pygame library and our display server, included to verify that the graphical components of the application are functioning correctly within the Docker environment.
  - **test_python.py**: A Python script designed for testing basic python functionalities of the application.
  - **set_permissions**: A directory of scripts that run in the background using `nohup` to set the correct file permissions for DICOM files received from the MRI on the experimenter's machine.
- **other**: A directory that stores archived and old files. 
  - **java-gui**: A directory containing Java-based graphical user interface (GUI) components for managing neurofeedback experiments, including source code, resource files, and build scripts for compiling and running the GUI applications. 
  - **old_material**: A directory that stores archived files and materials, including tarball archives. 
- **sambashare**: A directory faciliating data sharing between the MRI system and local machine, enabling seamless transfer of experimental data and resources. 
- **setup_main_docker**: Contains source material related to the creation of the Docker image. The docker images used for this project can be found [here](https://hub.docker.com/r/meghanwalsh/nfb_docker). This directory includes:
  - **Dockerfile**: A script that contains a series of instructions on how to build the Docker image, specifying the base image, the installation of necessary packages, and the configuration of the environment for running the application.
  - **build_docker.sh**: A shell script that automates the process of building the Docker image as defined in the `Dockerfile`. It creates a multi-architecture docker image in order to accommodate multiple architecture types. 
  - **python_requirements.txt**: A text file listing the Python packages and their respective versions installed in the docker image. This file is used during the Docker image build process to install all necessary Python dependencies, ensuring the application has the right environment for execution.
- **setup_samba_docker**: Contains configuration files and scripts for setting up a Docker container running a Samba server, enabling secure file sharing. The docker images used for this project can be found [here](https://hub.docker.com/r/meghanwalsh/nfb_docker). This directory includes:
  - **Dockerfile**: A script outlining the steps to build the Docker image for the Samba server, including the base image selection, installation of necessary packages, and configuration setting to establish the file-sharing environment. 
  - **README.md**: A markdown file that provides an overview and instructions for setting up the Samba docker. 
  - **smb.conf**: The primary configuration file for Samba, defines the shared directoriesm access permissions, and network settings. 
  - **docker_run_command.sh**: A shell script automating the deployment of the Samba server Docker container by configuring user settings, mapping shared directories, and ensuring the Samba service remains active for file sharing. 
- **tasks_run**: Contains the main task-related files, including additional data directories, materials for various tasks, and scripts for running different experimental tasks.
  - **data**: A collection of data files and logs related to the experimental tasks, organized into subdirectories. 
    - **localizer_data**: Contains logs and brain region masks used in localization scripts.
    - **msit_logs**: Contains log files produced by the [Multi-Source Interference Task](https://github.com/ccraddock/msit) (MSIT) task, aimed at activating the Anterior Cingulate Cortex (ACC).
    - **nfb_logs**: Contains log files produced by the neurofeedback task.
    - **rifg_logs**: Stores logs related to the Right Inferior Frontal Gyrus (RIFG) activation task experiments.
    - **sambashare**: A directory for sharing data between the MRI and the local machine's sambashare directory.
  - **msit_materials**: Contains materials and resources specific to the MSIT, including event files.
  - **nfb_materials**: Holds resources for neurofeedback tasks, including images.
  - **rifg_materials**: Contains materials related to RIFG tasks, including images and event files.
  - **scripts**: A collection of Python and shell scripts used for executing various tasks, data handling, and other functionalities within the project, including GUI-related scripts and other utility scripts. The most important scripts are described in the 'Task Script Descriptions' Section below.


## Task Script Descriptions 
#### Neurofeedback Task:
- **Main Script**: [1_Task_NFB.py](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/1_Task_NFB.py)
- **Description**: A real-time neurofeedback task where individuals in the scanner are shown their brain activity in an attention-related brain region of interest (either Anterior Cingulate Cortex (ACC) or Right Inferior Frontal Gyrus (RIFG)) via a rocket going into a portal. If that brain region becomes more active (i.e. the participant is paying attention more), the rocket gets closer to the portal. If that brain region becomes less active, the rocket gets further from the portal.
<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/nfb_materials/nfb.gif" alt="GIF of Neurofeedback Task" width="600"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> During the neurofeedback task, this participant uses their Anterior Cingulate Cortex (ACC) to move the rocket towards the portal. </p>

#### Multi-Source Interference (MSIT) Task: 
- **Main Script**: [1_Task_MSIT.py](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/1_Task_MSIT.py)
- **Description**: The [Multi-Source Interference Task](https://github.com/ccraddock/msit) (MSIT) has been shown to activate cognitive control and attentional regions in the brain, including the Anterior Cingulate Cortex (ACC), which we aim to localize using this task (Bush and Shin, 2006). This task will also serve as a measure of the participant's attention before and after neurofeedback.
- **Citations**: Bush, G, Shin, LM (2006). The Multi-Source Interference Task: an fMRI task that reliably activates the cingulo-frontal-parietal cognitive/attention network. Nat Protoc, 1, 1:308-13. PMID: 17406250.
<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/msit_materials/msit.gif" alt="GIF of MSIT Task" width="600"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> During the MSIT task, participants must choose the number that is different from the other two. </p>

#### Right Inferior Frontal Gyrus (RIFG) Localization Task:
- **Main Script**: [1_Task_RIFG.py](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/1_Task_RIFG.py)
- **Description**: A Go/no-go task where participants must press a button when they see a cartoon astronaut (Buzz Lightyear from the movie Toy Store), while they must refrain from pressing a button when they occasionally see a cartoon bear (Lotso from the movie Toy Story). Tasks of this nature, which requires participants to inhibit a response (pressing the button) when they see a stimuli, has shown to heavily involve the Right Inferior Frontal Gyrus, or RIFG (Hughes et al. 2013, Rubia et al. 2003). 
- **Citations**:
   1. Hughes ME, Johnston PJ, Fulham WR, Budd TW, Michie PT. Stop-signal task difficulty and the right inferior frontal gyrus. Behav Brain Res. 2013 Nov 1;256:205-13. doi: 10.1016/j.bbr.2013.08.026. Epub 2013 Aug 21. PMID: 23973765.
   2. Rubia K, Smith AB, Brammer MJ, Taylor E. Right inferior prefrontal cortex mediates response inhibition while mesial prefrontal cortex is responsible for error detection. Neuroimage. 2003 Sep;20(1):351-8. doi: 10.1016/s1053-8119(03)00275-1. PMID: 14527595.
<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/rifg_materials/rifg.gif" alt="GIF of RIFG Task" width="600"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> During the RIFG task, participants must not press the button when they see the bear. </p>

#### Rest Task:
- **Main Script**: [1_Task_REST.py](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/1_Task_REST.py)
- **Description**: Executes a 300 second resting-state task (showing just a fixation ccross on the sceen) to capture neural activity when the participant is at rest. 

#### Realtime Mask Registration with Easyreg:
- **Starting Script**: [2_Realtime_RegisterEasyeg.sh](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/2_Realtime_RegisterEasyeg.sh)
- **Description**: Through a series of scripts involving the transfer of files to/from E3 and a local docker container, an MNI-space mask is converted into subject-space using [EasyReg](https://surfer.nmr.mgh.harvard.edu/fswiki/EasyReg), a machine learning tool for registration of brain MRI.
<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/other/easyreg_slides.gif" alt="GIF of Easyreg Slides" width="800"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> The EasyReg-based Registration Pipeline </p>

#### Realtime Mask Registration with Fnirt/Flirt:
- **Main Script**: [2_Realtime_RegisterFnirt.sh](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/2_Realtime_RegisterFnirt.sh)
- **Description**: Using FSL's [FLIRT](https://ftp.nmr.mgh.harvard.edu/pub/dist/freesurfer/tutorial_packages/centos6/fsl_507/doc/wiki/FLIRT.html) and [FNIRT](https://ftp.nmr.mgh.harvard.edu/pub/dist/freesurfer/tutorial_packages/centos6/fsl_507/doc/wiki/FNIRT(2f)UserGuide.html) tools, this script registers ROI masks to participant-specific neuroimaging data from specified tasks. It includes DICOM to NifTi conversion, skull-stripping and mask creation, affine and nonlinear registrationl, as well as mask binarization. 
<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/other/fnirt_slides.gif" alt="GIF of Fnirt Slides" width="800"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> The Fnirt/Flirt-based Registration Pipeline </p>

#### Realtime Localizer:
- **Main Script**: [2_Realtime_Localizer.py](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/scripts/2_Realtime_Localizer.py)
- **Description**: The Localizer script aims to localize and a create mask of a brain region (within a given area) based on activation from either the MSIT task or RIFG task. It several steps including: preprocessing data, computing task-related activation maps using GLM (General Linear Model) analyses, and mask creation via a watershed algorithm. It also allow the experimenter to choose the threshold activation level for voxels included in the outputted mask via visualization in FSLeyes.
<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/other/localizer_slides.gif" alt="GIF of Localizer Slides" width="800"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> The ROI Localization Pipeline </p>

<div align="center" style="margin-top: 40px; margin-bottom: 40px;"> <img src="https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/tasks_run/other/localizer_demo.gif" alt="GIF of Localizer Demonstration" width="800"> </div> <p align="center" style="margin-top: 20px; margin-bottom: 5px;"> The localizer script allows users to select the threshold z-score based on the mask's appearance in FSLeyes. </p>

## Troubleshooting Steps 
### Siemens 3T Prisma MRI Scanner  
- When working with Boston Children's Siemens 3T Prisma MRI Scanner at 2 Brookline Place, we do the following to create a Samba share that the MRI control computer can connect to:
	- To connect to sambashare, log into **med admin** account. If logged into **med user** the connection will not establish accordingly and the DICOM transfer will be unsuccesful. 
	- To connect to sambashare, go into **File Explorer > This PC > Map Network Drive**, and input the following: 
		- **Drive**: Z:, **Folder**: `//<ip>/<folder>` (replace `<ip>` with the Samba server's IP address and `<folder>` with the folder you are sharing to the MRI machine)
		- Input the **Samba user**  established and the password will be the same if not pre-determined. 
	- Once connected, make sure the same files are shown on **File Explorer** window as on **Macbook**. 
	- If there is a Windows pop-up error, the computer may have to be restarted in order to re-establish the connection. 
	- Add-in configurations for MRI sequences must match the drive and information previously inputted for files to be transferred appropriately: 
		- **Target Host**: Z: (or whichever drive is connected), 
		- **Target Directory**: . (can specify directory or leave as "." to indicate the current directory), 
		- **Username**: `WORKGROUP\<user>` (use the **same user** specified in the **Folder** field prior to this step), 
		- **Password**: `<pre-determined or same as user>` (use the assigned password or the same values as the username if unspecified)

