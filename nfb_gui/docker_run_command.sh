#!/bin/bash
SETTINGSPATH="$1"
USER="$2"

docker run --rm -it \
-p 5998:5998 \
-e DISPLAY=:98 \
-e HOST_IP="$(ipconfig getifaddr en0)" \
-e USER="${USER}" \
-e PATH_TO_RUN_GUI_SCRIPT="$(python "$SETTINGSPATH" docker GUI_RUN_SCRIPT -s)" \
-e GUI_POM_PATH="$(python "$SETTINGSPATH" docker GUI_POM_PATH -s)" \
-e GUI_DIR="$(python "$SETTINGSPATH" docker GUI_DIR -s)" \
-v $(python "$SETTINGSPATH" PROJECT_DIRECTORY -s):/workdir \
meghanwalsh/nfb_java_gui:latest \
"$(python "$SETTINGSPATH" docker GUI_STARTUP_SCRIPT -s)" 