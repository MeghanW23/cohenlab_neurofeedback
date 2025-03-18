#!/bin/bash
ssh meghan@${ipconfig getifaddr en0} 'open /Applications/TigerVNC\ Viewer\ 
1.14.1.app/'
mvn exec:java -Dexec.mainClass="com.cohenlab.App"

