#!/bin/bash
SETTINGSPATH="$1"
USER="$2"
MRI_MONITOR_WIDTH="$3"
MRI_MONITOR_HEIGHT="$4"
MRI_MONITOR_Y_OFFSET="$5"

docker run --rm -it \
-p 5998:5998 \
-e DISPLAY=:98 \
-e HOST_IP="$(ipconfig getifaddr en0)" \
-e USER="${USER}" \
-e PATH_TO_RUN_GUI_SCRIPT="$(python "$SETTINGSPATH" docker GUI_RUN_SCRIPT -s)" \
-e GUI_POM_PATH="$(python "$SETTINGSPATH" docker GUI_POM_PATH -s)" \
-e GUI_DIR="$(python "$SETTINGSPATH" docker GUI_DIR -s)" \
-e GUI_XVFB_LOG="$(python "$SETTINGSPATH" docker GUI_XVFB_LOG -s)" \
-e GUI_X11_LOG="$(python "$SETTINGSPATH" docker GUI_X11_LOG -s)" \
-e GUI_NFB_LOGO="$(python "$SETTINGSPATH" docker GUI_NFB_LOGO -s)" \
-e MASK_DIR="$(python "$SETTINGSPATH" docker ROI_MASK_DIR_PATH -s)" \
-e SAMBASHARE_DIR_PATH="$(python "$SETTINGSPATH" docker SAMBASHARE_DIR_PATH -s)" \
-e RIFG_SCORE_LOG_DIR="$(python "$SETTINGSPATH" docker RIFG_SCORE_LOG_DIR -s)" \
-e NFB_SCORE_LOG_DIR="$(python "$SETTINGSPATH" docker NFB_SCORE_LOG_DIR -s)" \
-e MSIT_SCORE_LOG_DIR="$(python "$SETTINGSPATH" docker MSIT_SCORE_LOG_DIR -s)" \
-e NFB_LOG_DIR="$(python "$SETTINGSPATH" docker NFB_LOG_DIR -s)" \
-e RIFG_LOG_DIR="$(python "$SETTINGSPATH" docker RIFG_LOG_DIR -s)" \
-e MSIT_LOG_DIR="$(python "$SETTINGSPATH" docker MSIT_LOG_DIR -s)" \
-e MRI_MONITOR_WIDTH="$MRI_MONITOR_WIDTH" \
-e MRI_MONITOR_HEIGHT="$MRI_MONITOR_HEIGHT" \
-e MRI_MONITOR_Y_OFFSET="$MRI_MONITOR_Y_OFFSET" \
-v $(python "$SETTINGSPATH" PROJECT_DIRECTORY -s):/workdir \
meghanwalsh/nfb_java_gui:latest \
"$(python "$SETTINGSPATH" docker GUI_STARTUP_SCRIPT -s)" 