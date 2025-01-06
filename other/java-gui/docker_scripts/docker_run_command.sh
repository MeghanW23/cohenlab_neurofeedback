xhost + 
docker run -it \
-v /Users/meghan/cohenlab_neurofeedback:/workdir \
-e DISPLAY=host.docker.internal:0 \
-v /tmp/.X11-unix:/tmp/.X11-unix \
java_gui:latest /bin/bash

# --entrypoint /workdir/docker_run/run_gui.sh \
