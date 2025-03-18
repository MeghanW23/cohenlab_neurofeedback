#!/bin/bash
ssh meghan@192.168.1.233 'open /Applications/TigerVNC\ Viewer\ 1.14.1.app/'
mvn exec:java -Dexec.mainClass="com.cohenlab.App"

