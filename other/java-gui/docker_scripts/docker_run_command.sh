xhost + 
docker run -it \
-v /Users/meghan/cohenlab_neurofeedback:/workdir \
-e DISPLAY=host.docker.internal:0 \
-e LIBGL_ALWAYS_SOFTWARE=1 \
-p 5901:5901 \
-v /tmp/.X11-unix:/tmp/.X11-unix \
vnc-container:latest /bin/bash

# --entrypoint /workdir/docker_run/run_gui.sh \
