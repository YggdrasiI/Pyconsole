#!/bin/bash
# Setup environment variables for Keykit

export KEYROOT=/opt/kinect/keykit/

# Linux
export KEYKIT=key_alsa
export LOWKEYKIT=${KEYKIT}

# Windows
# export KEYKIT=key.exe
# export LOWKEYKIT=lowkey.exe

# Set KEYPATH to parse Pyconsole files at startup.
# Alternativily, you can place '#include contrib/Pyconsole/start.k'
# into the keyrc.k file, see below.
DEFAULT_KEYPATH=".:${KEYROOT}/lib:${KEYROOT}/liblocal" # could be differ on Windows?!
THIS_DIR=$(pwd)
export KEYPATH="${DEFAULT_KEYPATH}:${THIS_DIR%/scripts}:${KEYPATH}"

# Copy lib/keyrc.k into KEYROOT if file not exists
# Pyconsole assumes that it is installed under
# contrib/Pyconsole
if [ ! -e ${KEYROOT}/keyrc.k ] ; then
	echo "keyrc.k not found in ${KEYROOT}! Copy default keyrc.k from lib subdirectory..."
	cp ${KEYROOT}/lib/keyrc.k ${KEYROOT}
fi

