# On windows i've got a few strange bugs.
# 1. lowkey.exe can not open osc/tcp ports. 
# 2. key.exe does not handle -c argument if the program
#    is called by cmd.exe, but for sh-shell.
# 3. -c Argument conflicts with Graphic = 1?!
# => This wrapper simulates the -c argument of the *.sh 
# scripts by hand

#include contrib/Pyconsole/pyconsole.k

function autostart(){
	# This stops key.exe from imideatly quitting after startup. (cmd.exe)
	# Moreover, the window will be closed if the python shell sends
	# exit(). Probably because some background thread/task won't start
	# for Graphics = 0.
	Graphics = 0

	#keyrc()
	Pyconsole_windows_fix = 1
	pyconsole()
}

autostart()
