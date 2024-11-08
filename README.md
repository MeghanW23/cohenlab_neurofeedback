# Impact of Stimulants and In-Scanner Motion on fMRI Neurofeedback and Task Performance in ADHD

This repository outlines the study protocol examining the impact of fMRI neurofeedback, aiming to replicate stimulant effects, and in-scanner motion on behavioral changes and task performance in ADHD, conducted by [Alexander Cohen's Lab of Translational Neuroimaging at Boston Children's Hospital](https://bchcohenlab.com/).

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

- **Architecture**: The project supports either `amd64` or `arm64` architectures, which refer to the 64-bit versions of the x86 and ARM instruction sets, respectively, ensuring compatibility with a wide range of modern computing devices.
- **Docker Installation**: Ensure [Docker](https://docs.docker.com/engine/install/) is installed and configured on your machine.
- **FSL Installation**: [FSL](https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/FslInstallation.html) must be installed on your machine for brain ROI mask registration.
- **XQuartz Installation**: [XQuartz](https://www.xquartz.org/) must be installed to enable X11 forwarding for graphical applications.
- **E3 Access**: Ensure you have access to the E3 system (as well as have access to the Boston Children's Hospital VPN and have a valid CHID)
- **Dual Monitors**: It is recommended to work with two monitors for better workflow efficiency.

## Setup 
1. Clone the Repo: ```git clone https://github.com/MeghanW23/cohenlab_neurofeedback```
   
2. In your new local repository directory, navigate to `docker_run` and make `task_executor.sh` executable. Run: `sudo chmod +x docker_run_command.sh` on your terminal.

3. Set up XQuartz.
   1. Open ```Applications``` > ```Utilities``` > ```XQuartz```. Alternatively, you can search for "XQuartz" using Spotlight and launch it from there.
   2. Open XQuartz, then go to ```XQuartz``` in the menu bar and select ```Preferences```.
   3. In the ```Settings``` tab, ensure "Allow connections from network clients" is checked.
   4. In the ```Input``` tab, ensure both "Follow system keyboard layout" and "Enable key equivalents under X11" are checked
   5. In the ```Output``` tab, ensure "Auto-show menu bar in full-screen mode" are checked.

4. To run a docker container, do:
-  navigate to the `docker_run` directory in your local repository
- run ```./docker_run_command.sh```, select the task you would like to run, and input any requested information.
   
## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Architecture**: The project supports either `amd64` or `arm64` architectures, which refer to the 64-bit versions of the x86 and ARM instruction sets, respectively, ensuring compatibility with a wide range of modern computing devices.
- **Docker Installation**: Ensure Docker is installed and configured on your machine.
- **FSL Installation**: FSL must be installed for neuroimaging data analysis.
- **XQuartz Installation**: XQuartz must be installed to enable X11 forwarding for graphical applications.
- **Boston Children's Hospital CH ID**: You will need a valid CH ID for access.
- **VPN Access**: Access to the Boston Children's Hospital VPN.
- **E3 Access**: Ensure you have access to the E3 system.
- **Sambashare Mount**: Users must create a sambashare mount on their local machine to facilitate DICOM data transfer from the MRI and the user's machine.
- **Dual Monitors**: It is recommended to work with two monitors for better workflow efficiency.

## File Structure

- **README.md**: A markdown file that provides an overview of the project.

- **docker-setup**: Contains source material related to the creation of the Docker image. This directory includes:
  - **Dockerfile**: A script that contains a series of instructions on how to build the Docker image, specifying the base image, the installation of necessary packages, and the configuration of the environment for running the application.
  - **build_docker.sh**: A shell script that automates the process of building the Docker image as defined in the `Dockerfile`. It creates a multi-architecture docker image in order to accomidate multiple architecture types. 
  - **python_requirements.txt**: A text file listing the Python packages and their respective versions required for the application. This file is used during the Docker image build process to install all necessary Python dependencies, ensuring the application has the right environment for execution.

- **docker_run**: Includes scripts and configuration files necessary for running the Docker container. This directory contains:
  - **task_executor.sh**: A script that prompts the user to select a task and runs the corresponding script within the Docker container.
  - **startup.sh**: A script designed to set up the project environment within the Docker container and run task scripts based on the information given frun om the `docker_run_command.sh` script.
  - **test_pygame.py**: A Python script used for testing functionalities related to the Pygame library and x11 forwarding, included to verify that the graphical components of the application are functioning correctly within the Docker environment.
  - **test_python.py**: A Python script designed for testing basic python functionalities of the application.
- **old_material**: A directory that stores archived files and materials, including tarball archives.

- **tasks_run**: Contains the main task-related files, including additional data directories, materials for various tasks, and scripts for running different experimental tasks.
*NOTE: Any imaging or personal data is pushed to private storage locations on E3 to protect participants' Protected Health Information (PHI) and to minimize issues related to managing large amounts of data on GitHub.*
  - **data**: A collection of data files and logs related to the experimental tasks, organized into subdirectories. 
    - **localizer_data**: Contains logs and neuroimaging masks used in localization scripts.
    - **msit_logs**: Holds log files producted by the [Multi-Source Interference Task](https://github.com/ccraddock/msit) (MSIT) task.
    - **nfb_logs**: Contains log files from neurofeedback experiments.
    - **rifg_logs**: Stores logs related to our Right Inferior Frontal Gyrus (RIFG) activation task experiments.
    - **sambashare**: A directory for sharing data between the MRI and the local machine's sambashare directory.
  - **msit_materials**: Contains materials and resources specific to the MSIT, including event files.
  - **nfb_materials**: Holds resources for neurofeedback tasks, including images.
  - **rifg_materials**: Contains materials related to RIFG tasks, including images and event files.
  - **scripts**: A collection of Python and shell scripts used for executing various tasks, data handling, and other functionalities within the project, including GUI-related scripts and other utility scripts.


