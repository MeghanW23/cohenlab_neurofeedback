#!/bin/bash

docker run --rm -it \
-p 5998:5998 \
-e DISPLAY=:98 \
-v $(pwd):/workdir \
-v /Users/meghan/cohenlab_neurofeedback:/projectDir \
meghanwalsh/nfb_java_gui:latest \
/bin/bash
