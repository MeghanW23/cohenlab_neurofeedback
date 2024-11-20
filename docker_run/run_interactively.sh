settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"

sudo docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
  -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
  meghanwalsh/nfb_docker:latest \
  /bin/bash