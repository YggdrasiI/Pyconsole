
@echo off

rem Variables begin with X to not mess up 
rem a environment variable used bey Keykit itself.
SET XKEYROOT=I:\Olaf\keykit\key77b_win
SET XKEYKIT=key.exe
SET XLOWKEY=lowkey.exe

SET THIS_DIR=%cd%

cd /d %XKEYROOT%
rem Desired solution, but does not work:
rem bin\%XKEYKIT% ../contrib/Pyconsole/pyconsole.k  -c "pyconsole()"
rem Workaround:
bin\%XKEYKIT% contrib/Pyconsole/pyconsole_win.k 

cd /d %THIS_DIR%
rem Unset variables. Otherwise they leave the scope of the script...
rem SET XKEYPATH=
SET XKEYROOT=
SET XKEYKIT=
SET XLOWKEY=
SET THIS_DIR=
