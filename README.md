## Project Overview
Attention-deficit/hyperactivity disorder (ADHD) is a complex condition often treated with stimulant medications, which have proven effective in managing symptoms like inattention and impulsivity but can cause side effects. The question remains whether non-pharmacological interventions, such as neurofeedback, can replicate or enhance the benefits of stimulants in individuals with ADHD.  Additionally, functional magnetic resonance imaging (fMRI) studies in ADHD research have often been hindered by unaccounted motion artifacts, leading to potential inaccuracies in measuring brain activity. Our research aims to address these gaps by improving the methods used to correct for motion in neuroimaging studies and by exploring the potential of neurofeedback as an alternative or complementary treatment for ADHD.
### Our research has two objectives:
#### (1) Address the Impact of Motion on fMRI Results Involving Individuals with ADHD: 
We will investigate and address the impact of motion artifacts in fMRI research, particularly in ADHD studies where motion has previously been unmeasured or inadequately accounted for. By incorporating new technology to better capture and correct for motion, and by repeating experiments with this improved capability, we aim to refine our understanding of how motion affects neuroimaging results. 

#### (2) Address the Feasibility of Neurofeedback as a Method to Replicate the Effects of Stimulants in ADHD
Our study will explore whether neurofeedback can replicate or enhance the effects of stimulant medications in individuals with ADHD. By comparing brain activity and performance on attention tasks during neurofeedback and stimulant conditions, we aim to determine if neurofeedback can serve as an alternative or complement to stimulants in managing ADHD symptoms. This investigation will contribute to the literature by evaluating the potential of neurofeedback to replicate or amplify the benefits typically associated with stimulant treatments, without the side effects associated with stimulant drugs.
By addressing the impact of motion artifacts and investigating the effects of neurofeedback compared to stimulant medications, our study seeks to refine neuroimaging techniques and expand the understanding of ADHD treatment options. If neurofeedback can replicate or amplify the effects of stimulants on brain activity and attention, it may offer a promising, non-invasive treatment with fewer side effects. Ultimately, this research has the potential to advance both methodological practices in ADHD research and therapeutic approaches for individuals with the condition.

## Setup 
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
  
  ```rifg_task.py```: Implementation of the RIFG task, including task logic and execution.
  
  ```output_logs/```: Directory containing log files from the RIFG task sessions.

```run_docker_container.sh```
Script for launching the Docker container. It sets up the environment and starts the application within the container.

```startup_docker.sh```
Initialization script for setting up the Docker environment and starting necessary services or configurations before running the main Docker container.

