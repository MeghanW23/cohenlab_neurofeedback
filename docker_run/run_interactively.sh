settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"

sudo docker run -it \
  -p 5999:5999 \
  -e TZ="$(python "$settings_script_path" TZ -s)" \
  -e DISPLAY=:99 \
  -e USER="$USER" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
  -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
  --entrypoint /bin/bash \
  meghanwalsh/nfb_docker:latest