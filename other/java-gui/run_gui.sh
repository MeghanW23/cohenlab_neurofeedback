#!/bin/bash

current_user=$(whoami)
settings_script_path="/Users/${current_user}/cohenlab_neurofeedback/tasks_run/scripts/settings.py"

CONDA_INSTALLATION_SCRIPT=$(python "$settings_script_path" LOCAL_CONDA_INSTALLATION_SCRIPT -s)
source "$CONDA_INSTALLATION_SCRIPT"

conda activate java_env
if [ $? -eq 1 ]; then 
    echo "Error activating the java env."
    exit
fi 
if [ -z "$JAVA_HOME" ]; then
    JAVA_HOME="$(/usr/libexec/java_home)"
    if [ ! -d "$JAVA_HOME" ]; then 
        echo -e "\nCould not find your Java home directory via: 'JAVA_HOME=\$(/usr/libexecrerer/java_home)'."
        echo "Is Java installed on your machine?" 
        echo -e "If Java is installed, please set JAVA_HOME as an environment variable before running this script.\n"
        exit 0
    else 
        export JAVA_HOME
    fi
fi

if ! command -v mvn &> /dev/null; then 
    echo "Maven installation cannot be found. Please install before running."
    exit 0
fi

# Make Env Vars from the Settings Variables 
export GUI_PROJECT_DIR="$(python3 ${settings_script_path} GUI_PROJECT_DIR -s)"
export GUI_SRC_DIR="$(python3 ${settings_script_path} GUI_SRC_DIR -s)"
export GUI_IMAGES_DIR="$(python3 ${settings_script_path} GUI_IMAGES_DIR -s)"
export GUI_MAIN_DIR="$(python3 ${settings_script_path} GUI_MAIN_DIR -s)"
export NEUROFEEDBACK_LOGO_IMAGE="$(python3 ${settings_script_path} NEUROFEEDBACK_LOGO_IMAGE -s)"
export MSIT_SCORE_LOG_DIR="$(python3 ${settings_script_path} MSIT_SCORE_LOG_DIR -s)"
export RIFG_SCORE_LOG_DIR="$(python3 ${settings_script_path} RIFG_SCORE_LOG_DIR -s)"
export NFB_SCORE_LOG_DIR="$(python3 ${settings_script_path} NFB_SCORE_LOG_DIR -s)"
export MVN_POM_FILE="$(python3 ${settings_script_path} MVN_POM_FILE -s)"
export NFB_N_TRIALS_ODD_BLOCK="$(python3 ${settings_script_path} NFB_N_TRIALS_ODD_BLOCK -s)"
export NFB_N_TRIALS_EVEN_BLOCK="$(python3 ${settings_script_path} NFB_N_TRIALS_EVEN_BLOCK -s)"
export ERROR_IMAGE="$(python3 ${settings_script_path} ERROR_IMAGE -s)"

# Step 1: Clean the project
echo "Cleaning project..."
mvn -f "$MVN_POM_FILE" clean

# Step 2: Compile the project
echo "Compiling project..."
mvn -f "$MVN_POM_FILE" compile

# Step 3: Run the project
echo "Running project..."
# mvn -f "$MVN_POM_FILE" exec:java -Dexec.mainClass="com.cohenlabnfb.App"
# mvn -f "$MVN_POM_FILE" exec:java -Dexec.mainClass="com.cohenlabnfb.App" -Dsun.java2d.opengl=false
# Step 3: Run the project
echo "Running project..."
mvn -f "$MVN_POM_FILE" exec:java \
    -Dexec.mainClass="com.cohenlabnfb.App" \
    -Dsun.java2d.opengl=true \
    -Dawt.useSystemAAFontSettings=on \
    -Dswing.aatext=true