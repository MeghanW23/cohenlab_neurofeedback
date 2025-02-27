#!/bin/bash
Xvfb :98 -screen 0 1024x768x24 &
export DISPLAY=:98
x11vnc -display :98 -geometry 1024x768 -forever  -verbose -nopw -rfbport 5998 &
java SimpleGUI
