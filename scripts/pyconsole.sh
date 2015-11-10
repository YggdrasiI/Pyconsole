#!/bin/bash
#
# Start server backend for python console
####################################

# Input handling
Func="pyconsole(3330)"
test -z "$1" || Func="pyconsole($1)" 

# Normalize path. GRID_MUSIC_ROOT will be used to find Pyconsole/tests in Keykit
THIS_DIR=$(pwd)
export GRID_MUSIC_ROOT="${THIS_DIR%/scripts}"

# Setup variables
source ${GRID_MUSIC_ROOT}/scripts/environment.sh
export DISPLAY=""

# Kill running instance of keykit
killall $KEYKIT

# Swtich into directory with keyrc.k
cd $KEYROOT
$KEYROOT/bin/$KEYKIT contrib/Pyconsole/pyconsole.k -c "$Func" 
