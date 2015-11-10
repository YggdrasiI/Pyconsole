#!/bin/bash
#
#Start GridMusic without gui
####################################

# Input handling
Func="settingPiano"
test -z "$1" || Func="$1" 

# Normalize path. GRID_MUSIC_ROOT will be used to find GridMusic/tests in Keykit
THIS_DIR=$(pwd)
export GRID_MUSIC_ROOT="${THIS_DIR%/scripts}"

# Setup variables
source ${GRID_MUSIC_ROOT}/scripts/environment.sh
export DISPLAY=""

# Kill running instance of keykit
killall $KEYKIT

# Connect with midi sequenzer after short delay
# Note that Keykit call this command by it self, too (see GridMusic/start.k )
${GRID_MUSIC_ROOT}/scripts/connect_alsa.sh ZynAddSubFX 2 &

# Swtich into directory with keyrc.k
cd $KEYROOT
$KEYROOT/bin/${LOWKEYKIT} contrib/GridMusic/start.k -c "kinect(\"$Func\")" 
