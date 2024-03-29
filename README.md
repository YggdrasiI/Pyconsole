   Python based shell for Keykit
========================================

## Description

OSC-Server to recive Keykit commands and send the output back
to the sender.
The script is designed to be used as CLI script, but can
also be started in the Keykit window.

It should be used together with the Python CLI frontend.

Author: Olaf Schulz, Nov 2015
Licence: LGPL


## Install instructions

1. Place this folder (Pyconsole) into [Keykit root dir]/contrib/.
2. (Linux/etc.) Open scripts/environment.sh and adapt KEYROOT and KEYKIT to
   your environment.
   (Windows) Open scripts/pyconsole.bat and adapt the Path to
   your Keykit installation.
3. (Windows) Look into python/README how to install the pyreadline package.
   Check if key.exe/lowkey.exe will be blocked by your firewall.


## Bugs

- In the GUI-Mode does the redirection of the output ('stdout')
  not work.
- In the CLI-Mode does the redirection of errors ('stderr')
  not work.
- (Windows) It does not work with lokwey. The open()-Function
  of Keykit fails!
- (Windows) Do not select the Keykit window. That blockades the server.


## Start

1. Run pyconsole() in your Keykit window or call
   scripts/pyconsole.sh (Linux) or
   scripts/pyconsole.bat (Windows) to start the Server.

2. Start `make run` or `python3 -m pykeykit`


## Tested with

- Linux (x86, x86_64, armv6l armv7) with Keykit 7.7b + Python 3.8.x
  Compiling patches for Keykit can be found on
  https://github.com/YggdrasiI/GridMusic/tree/master/keykit_patches

- Windows 7 with cmd.exe or Git Bash Shell (https://git-scm.com/download/win)
  + Keykit 7.7b + Python 2.7.x (older version)
