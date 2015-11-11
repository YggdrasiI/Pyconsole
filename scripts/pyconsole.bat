
@echo off

rem Variables begin with X to not mess up 
rem a environment variable used bey Keykit itself.
SET XKEYROOT=I:\Olaf\keykit\key77b_win
SET XKEYKIT=key.exe
SET XLOWKEY=lowkey.exe

SET THIS_DIR=%cd%

rem cd /d %XKEYROOT%
rem %XKEYROOT%\bin\%XLOWKEY% contrib/Pyconsole/pyconsole.k -c "pyconsole()" 


cd /d %XKEYROOT%
bin\%XKEYKIT% contrib/Pyconsole/pyconsole_win.k 
rem bin\%XKEYKIT% ../contrib/Pyconsole/pyconsole.k  -c "while(1){sleeptill(Now+1b)}"

cd /d %THIS_DIR%
rem Batch variable stored outsid of script... Lol
rem SET KEYPATH=
