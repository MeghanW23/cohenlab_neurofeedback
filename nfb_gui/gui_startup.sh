#!/bin/bash
Xvfb :98 -screen 0 800x800x24 > "xvfb.log" 2>&1 &
x11vnc -display :98 -geometry 800x800 -forever  -verbose -nopw -rfbport 5998 > "x11vnc.log" 2>&1 &