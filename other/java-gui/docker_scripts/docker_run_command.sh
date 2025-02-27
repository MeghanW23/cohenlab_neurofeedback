#!/bin/bash

xhost + 
docker run --rm -it -p 5998:5998 -e DISPLAY=:98 -v $(pwd):/workdir -v /tmp/.X11-unix:/tmp/.X11-unix meghanwalsh/nfb_java_gui:1.0 /workdir/simple_gui_startup.sh

