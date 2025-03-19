#!/bin/bash
SETTINGSPATH="$1"
USER="$2"

docker run --rm -it \
-p 5998:5998 \
-e DISPLAY=:98 \
-e HOST_IP="$(ipconfig getifaddr en0)" \
-e USER="${USER}" \
-v $(python "$SETTINGSPATH" PROJECT_DIRECTORY -s):/workdir \
meghanwalsh/nfb_java_gui:latest \
"$(python "$SETTINGSPATH" docker GUI_STARTUP_SCRIPT -s)" 