#!/bin/bash
settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"

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
export GUI_JAVA_FILES_DIR="$(python3 ${settings_script_path} GUI_JAVA_FILES_DIR -s)"
export GUI_CLASSPATH="$(python3 ${settings_script_path} GUI_CLASSPATH -s)"
export NEUROFEEDBACK_LOGO_IMAGE="$(python3 ${settings_script_path} NEUROFEEDBACK_LOGO_IMAGE -s)"
export MSIT_LOG_DIR="$(python3 ${settings_script_path} MSIT_LOG_DIR -s)"
export RIFG_LOG_DIR="$(python3 ${settings_script_path} RIFG_LOG_DIR -s)"
export NFB_LOG_DIR="$(python3 ${settings_script_path} NFB_LOG_DIR -s)"
export MVN_POM_FILE="$(python3 ${settings_script_path} MVN_POM_FILE -s)"


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