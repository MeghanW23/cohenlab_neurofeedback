This repository outlines the study protocol examining the impact of fMRI neurofeedback, aiming to replicate stimulant effects, and in-scanner motion on behavioral changes and task performance in ADHD, conducted by Alexander Cohen's Lab of Translational Neuroimaging at Boston Children's Hospital.

## Project Overview
Attention-deficit/hyperactivity disorder (ADHD) is a complex condition often treated with stimulant medications, which have proven effective in managing symptoms like inattention and impulsivity but can cause side effects. The question remains whether non-pharmacological interventions, such as neurofeedback, can replicate or enhance the benefits of stimulants in individuals with ADHD.  Additionally, functional magnetic resonance imaging (fMRI) studies in ADHD research have often been hindered by unaccounted motion artifacts, leading to potential inaccuracies in measuring brain activity. Our research aims to address these gaps by improving the methods used to correct for motion in neuroimaging studies and by exploring the potential of neurofeedback as an alternative or complementary treatment for ADHD.
### Our research has two objectives:
#### (1) Address the Impact of Motion on fMRI Results Involving Individuals with ADHD: 
We will investigate and address the impact of motion artifacts in fMRI research, particularly in ADHD studies where motion has previously been unmeasured or inadequately accounted for. By incorporating new technology to better capture and correct for motion, and by repeating experiments with this improved capability, we aim to refine our understanding of how motion affects neuroimaging results. 

#### (2) Address the Feasibility of Neurofeedback as a Method to Replicate the Effects of Stimulants in ADHD
Our study will explore whether neurofeedback can replicate or enhance the effects of stimulant medications in individuals with ADHD. By comparing brain activity and performance on attention tasks during neurofeedback and stimulant conditions, we aim to determine if neurofeedback can serve as an alternative or complement to stimulants in managing ADHD symptoms. This investigation will contribute to the literature by evaluating the potential of neurofeedback to replicate or amplify the benefits typically associated with stimulant treatments, without the side effects associated with stimulant drugs.
By addressing the impact of motion artifacts and investigating the effects of neurofeedback compared to stimulant medications, our study seeks to refine neuroimaging techniques and expand the understanding of ADHD treatment options. If neurofeedback can replicate or amplify the effects of stimulants on brain activity and attention, it may offer a promising, non-invasive treatment with fewer side effects. Ultimately, this research has the potential to advance both methodological practices in ADHD research and therapeutic approaches for individuals with the condition.
## Setup 
1. Clone the Repo: ```git clone https://github.com/MeghanW23/cohenlab_neurofeedback```
   
2. In Repo Dir, Make the Docker Building Script Executable: ```sudo chmod +x build_docker.sh```
   
3. Run the Docker Building Script: ```./build_docker.sh```
   
4. Set up XQuartz.
   1. XQuartz will forward graphical output from the Docker container to the local machines' display through the X11 protocol.
   2. Download XQuartz from the [official website](https://www.xquartz.org/).
   3. Open ```Applications``` > ```Utilities``` > ```XQuartz```. Alternatively, you can search for "XQuartz" using Spotlight and launch it from there.
   4. Open XQuartz, then go to ```XQuartz``` in the menu bar and select ```Preferences```.
   5. In the ```Settings``` tab, ensure "Allow connections from network clients" is checked.
   6. In the ```Input``` tab, ensure both "Follow system keyboard layout" and "Enable key equivalents under X11" are checked
   7. In the ```Output``` tab, ensure both "Full Screen Mode" and "Auto-show menu bar in full-screen mode" are checked.
   8. To run a docker container, run the script ```run_docker_container.sh```: ```./run_docker_container.sh```

5. To run the rIFG task, you must ensure that:
      1. You have a second monitor connected that will serve as a stand-in for the MRI screen. 
      2. Your second monitor is registered in the script (see Meghan)
      If above is true, run the rIFG task by entering ```rifg``` into the container command line.

6. As scripts are made/edited, more setup info will be added. 

   
## File Structure 
```Dockerfile```
Defines the setup instructions for creating the Docker environment required to run the neurofeedback project. This file specifies the base image, dependencies, and configurations necessary for the containerized application.

```README.md```
Provides an overview of the project, including objectives, methodology, and setup instructions.

``build_docker.sh``
A script to build the Docker image from the Dockerfile. It automates the process of creating a Docker image with the necessary dependencies and configurations for the project.

```docker-compose.yml```
Configuration file for Docker Compose. This file defines the services, networks, and volumes required for running the project.

```local_scripts/```
A directory containing local Python scripts used for testing scripts locally. Each sub-directory belongs to one person.

```old_material/```
Contains outdated or previous versions of project files.

```requirements.txt```
Lists the Python dependencies needed for the project.

```run_docker/```
Directory containing Python scripts and resources for running specific tasks related to the project.

```run_docker/rifg_task/```
Subdirectory with resources and scripts for the RIFG task.

  - ```rifg_task.py```: Implementation of the RIFG task, including task logic and execution.
    
  - ```output_logs/```: Directory containing log files from the RIFG task sessions.

```run_docker_container.sh```
Script for launching the Docker container. It sets up the environment and starts the application within the container.

```startup_docker.sh```
Initialization script for setting up the Docker environment and starting necessary services or configurations before running the main Docker container.

