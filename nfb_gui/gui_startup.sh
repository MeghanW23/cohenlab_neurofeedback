#!/bin/bash
Xvfb :98 -screen 0 700x800x24 > "$GUI_XVFB_LOG" 2>&1 &
x11vnc -display :98 -geometry 700x800 -forever  -verbose -nopw -rfbport 5998 > "$GUI_X11_LOG" 2>&1 &

cd "$GUI_DIR"

"${PATH_TO_RUN_GUI_SCRIPT}"

exit