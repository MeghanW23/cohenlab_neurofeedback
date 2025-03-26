#!/bin/bash
# ssh ${USER}@${HOST_IP} 'open /Applications/TigerVNC\ Viewer\ 1.14.1.app/'
mvn exec:java -Dexec.mainClass="com.cohenlab.App" && exit