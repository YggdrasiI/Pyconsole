# Recive messages via OSC messages
# See python/keykit.py for usage.

#include contrib/Pyconsole/base_functions.k

# Load stuff from GridMusic
#include contrib/GridMusic/start.k

# Default server value
PYCONSOLE_PORT = 3330
#PYCONSOLE_HOSTNAME = "0.0.0.0" # Bad on windows
PYCONSOLE_HOSTNAME = "127.0.0.1"

# Note: Keykit internal variables for this data are:
#  KeyKitHost, Hostname, KeyKitPort, KeyKitRemotePort

# Global pointer to pyconsole object
# Target of osc_printf, see below.
Pyconsole = -1

# Flag to enable a few debugging messages. 
# Could be set by 
# /keykit/pyconsole/verbose OSC message, too.
Pyconsole_verbose = 0

# Filename for !log command.
Pyconsole_logfile = "pyconsole.log"

# Enable workaround, see pyconsole_win.k
Pyconsole_windows_fix = 0

# Maximal string length in osc send message. Longer messages
# will be splitted. The maximal udp package length depends
# of your network settings. Too long messages could be cutted.

#Pyconsole_max_payload_len = 512
# 512 is to big for pythonosc...
# Error in dispatcher.py, line 183
#    packet = osc_packet.OscPacket(data)
#
# Could not parse packet ('Found incorrect datagram, ignoring it',
# ParseError('Could not parse datagram index out of range'))


Pyconsole_max_payload_len = 300


# Call this function to use pyconsole
function pyconsole(port, hostname){

	#include contrib/Pyconsole/base_functions.k
	if( nargs() < 2 ) hostname = PYCONSOLE_HOSTNAME
	if( nargs() < 1 ) port = PYCONSOLE_PORT 
	
	#enable_input("in 1")
	enable_output()

	pycon = new osc_console(port, hostname)
	if( Graphics == 0 ){
		Local_print("Press Ctrl+C to exit.")
		wait(pycon.get_osc_tid())
		while (1) {
			sleeptill(Now+2b)
			break
		}
		deleteobject(pycon);
		Local_printf("Quit pyconsole...\n")
	}else{
		Local_print("Press Esc to exit.")
		while (1) {
			c = Root.waitforconsolekey()
			if ( ascii(c) == 27 ) {
				break
			}
			Local_print("ignore", c);
			sleeptill(Now+2b)
		}
		deleteobject(pycon);
		Local_printf("Quit pyconsole...\n")
	}
}


#####################################################
# Internal stuff

# Dummy handler, see below
function ignore_non_fatal_errors() { }

# Own interrupt function, unused
function no_interrupt(){ }

# Backup original printf handler
Local_printf = nullfunc
#Local_consoleprintf = nullfunc
#Local_focus = -1

function Local_print(...) {
	sep = ""
	for ( n=0; n<nargs(); n++ ) {
		Local_printf("%s%s",sep,string(argv(n)))
		sep = " "
	}
	Local_printf("\n")
}

# printf replacement for remote printing
# Every call of print() in Keykit invoke this
# function at least twice. 
# At the end it will be called with a final "\n".
# We wait with the osc sending till this last "\n"
# recive. This does not work for print("\n").
# If mutliple task write out data only a few "\n" should be feed up?!
Osc_send_cache = ""
function osc_printf(...) {
	if( Pyconsole != -1 ){
		s = sprintf(...)

		if( s == "\n" && Osc_send_cache != "" ){
			to_send = Osc_send_cache
			Osc_send_cache = ""
			Pyconsole.send(to_send)
			if( Pyconsole_verbose > 0 ) Local_printf("Send '" + to_send + "'")
		}else{
			Osc_send_cache += s
		}
	}else{
		Local_printf(...)
	}
}


# Flag to omit recursion in error func.
Pyconsole_sending_err = 0

# Error handler. (Note that this will be
# handled taskwise.
function onerrorfunc(s,obj){
	if( nargs() < 2 ){
		return()
	}
	# Sending failed?! Print out local
	if( Pyconsole_sending_err > 0  || Pyconsole == -1){
		Pyconsole_sending_err = 0
		Local_printf(s)
		return(-1)
	}

	Pyconsole_sending_err = 1
	#obj.send(s, "/keykit/pyconsole/err")
	Pyconsole.send(s, "/keykit/pyconsole/err")
	Pyconsole_sending_err = 0
	return(0)
}

# Task loop for my Consout, unused
function my_consoutloop() {
	while ( 1 ) {
		c = get(Consoutfifo)
		#c = get(Pyconsole_out)
		#Local_printf(",%s",string(c))
		realmidi('g',Now)
	}
}
#consoutloop = my_consoutloop

class osc_console {
	method init(port, hostname) {
		if( nargs() < 2 ) hostname = PYCONSOLE_HOSTNAME
		if( nargs() < 1 ) port = PYCONSOLE_PORT

		$.osclistenport = port
		$.oschostname = hostname
		$.oscsendtarget = ["port"=(port+1), "server"="localhost"]
		$.open_tasks = [] # task id = key value, unused

		$.Hist = []
		$.Histindex = 0
		$.History = 0
		$.Modir = 0

		Local_printf = printf
		if( Pyconsole_windows_fix == 1 ){
			# without foucsed object in the keykit window,
			# key.exe uses a blocking popup for printing.
			# Thus, we disable local printing in this
			# case completely.
			# Note that pyconsole_win.k already changed
			# Graphics to 0 here... This variable can not
			# be used as indicator.
			Local_printf = nullfunc
		}
		#Local_consoleprintf = consoleprintf

		printf = osc_printf
		Pyconsole = $

		# Overwrite default Errorfunc to omit program exit on
		# errors. Without this remapping malformed input quit
		# Keykit in console mode.
		Errorfunc = ignore_non_fatal_errors

		#Intrfunc = no_interrupt

		s = string($.osclistenport)+"@"+$.oschostname
		$.oscf = open(s,"rA","osc_listen")
		if ( $.oscf < 0 ) {
			Local_print("Unable to listen on ", s, " !?")
			$.osctid = -1
		} else {
			Local_print("Listening for OSC on ", s, " ...")
			# start loop for mmtt osc messages
			$.osctid = task $.osctask()
		}
		$.lastosc = 0 # unused

		# Send out information about (re)-start of the backend.
		$.send("Pyconsole started.", "/keykit/pyconsole/start")
	}

	method delete {
		if($.oscf > -1){
			close($.oscf)
			$.oscf = -1
		}
		kill($.osctid)
		$.osctid = -1

		# Restore previous handler
		if( Pyconsole_windows_fix == 0 ){
			printf = Local_printf
		}
		#consoleprintf = Local_consoleprintf
		if( Pyconsole == $){
			Pyconsole = -1
		}
		#Local_printf("Delete called\n")
	}

	method handle_message(d){
		# print(d[0])
		if( d[0] == "/keykit/pyconsole/in" ){
			if( Pyconsole_verbose > 0 ) Local_print("execute ", d[1])

			# Blocking evaluation
			# $.interpreter(d[1])
			# or
			# Unbocking evaluation
			tid = task $.interpreter(d[1])

			lock($)
			$.open_tasks[tid] = 1
			unlock($)
		}else if( d[0] == "/keykit/pyconsole/target" ){
			lock($)
			$.oscsendtarget["server"] = string(d[1])
			$.oscsendtarget["port"] = integer(d[2])
			if( Pyconsole_verbose > 0 ){
				Local_print("Set pyconsole target to",
					string($.oscsendtarget["port"])+"@"+$.oscsendtarget["server"])
			}
			unlock($)
		}
		else if( d[0] == "/keykit/pyconsole/verbose" ){
			Pyconsole_verbose = integer(d[1])
		}
		else if( d[0] == "/keykit/pyconsole/lsdir" ){
			if( Pyconsole_verbose > 0 ){
				Local_print("lsdir path: ",string(d[1]))
			}
			files = lsdir(string(d[1]))
			# Long strings could be split into multiple packages
			# ^,$ are used to mark begin and end of string
			array_string = sprintf("^%s$",string(files))
			if( Pyconsole_verbose > 0 ){
				Local_print("lsdir result: ",array_string)
			}
			task $.send(array_string, "/keykit/pyconsole/lsdir")
		}
	}

	method osctask() {
		while ( (d=get($.oscf)) != Eof ) {

			# Bundled OSC messages leads to array structure, unsed
			if( typeof(d[0]) == "array" ){
				dnr = d["elements"]
				# Assume index enumeration 0,1,...
				for( i=0 ; i<dnr ; i++){
					$.handle_message(d[i])
				}
			}else{
				$.handle_message(d)
			}

			lock($)
			$.lastosc = Now
			unlock($)
		}
	}

	# Interpreter copied from loops.k::interploop.
	method interpreter(cmd) {
		if ( cmd == Eof ){
			exit(0)
		}
		if ( cmd == Interrupt ) {
			if( Pyconsole_verbose > 0 ) Local_print("<INTERRUPT>")
			return()
		}
		if ( cmd < 0 ) {
			return()
		}

		# Map error message handling (FOR THIS TASK!)
		onerror(onerrorfunc, $)

		# $.History processing (revu et augmenté...)
		if ( substr(cmd,1,1)=="!") {
			theCmd = ""
			if (cmd=="!!") {
				if ($.Histindex > 0)
				{
					lock($)
					$.Histindex--
					theCmd = $.Hist[$.Histindex]
					unlock($)
				}
				else
				{
					# cons.printf("no history yet...\n")
					print("no history yet...\n")
					theCmd = ""
				}
			}
			else if (cmd=="!") { 				# liste

				if ($.Histindex > 0){
					s = ""
					for(hi = 0; hi < $.Histindex; hi++){
						# cons.printf("%d: %s\n",hi,$.Hist[hi])
						s += sprintf("%d: %s\n",hi,$.Hist[hi])
					}
					print(s)
				}else{
					# cons.printf("no history yet...\n")
					print("no history yet...\n")
				}
				theCmd = ""
			}
			else if (cmd=="!!!") { 						# remise à zéro
				lock($)
				$.Histindex = 0
				unlock($)
				theCmd = ""
			}
			else if ((cmd=="!log") && $.Histindex > 0) {	# sauvegarde (KKlog.txt)
				$.normalize_logname()

				logf = open(Pyconsole_logfile,"w")
				for(hi = 0; hi < $.Histindex; hi++){
					put(logf, sprintf("%d: %s\n",hi,$.Hist[hi]))
				}
				close(logf)
				# cons.printf("%s\n",">>> $.History sauvegardée sous "+$.HFName)
				s = sprintf("%s\"%s\".\n", ">>> $.History saved in Pyconsole_logfile=",
					Pyconsole_logfile)
				print(s)
				theCmd = ""							
			}
			else {
				which = split(cmd,"!")
				which = integer(which[0])
				if (which < 0){
					which = $.Histindex + which
				}
				if (which >= 0 && which <= $.Histindex) {
					theCmd = $.Hist[which]
				}
			}
			# if ( Inputistty && (theCmd != "") )
			# cons.printf("%s\n",">>> "+theCmd)
			cmd = theCmd
		}


		words = split(cmd," ")
		if ( sizeof(words) == 0 ){
			return()
		}

		lock($)
		$.Hist[$.Histindex++] = cmd
		unlock($)

		if ( words[0] == "print" ) {
			rest = substr(cmd,6)
			cmd = "print("+rest+")"
			words = split(cmd," ")
		}
		if (words[0] == "::") {
			lock($)
			$.Modir = 1-$.Modir		# bascule du mode direct 
			unlock($)
			cmd = "cmd"
		}
		else if ((substr(cmd,1,1) == ":")||($.Modir)) {	
			rest = substr(cmd,2-$.Modir)
			if (substr(rest,1,1) != "# ")
			{
				cmd = "print("+rest+")"
				words = split(cmd," ")
			}
		}
		if ( sizeof(split(cmd,"=")) > 1
		|| substr(cmd,1,5)=="print"
		|| words[0] == "delete"
		|| words[0] == "#define"
		|| words[0] == "#include" )
		{
			eval cmd
		}
		else {
			Cmd___tmp = 0
			eval "Cmd___tmp = " + cmd
			if ( typeof(Cmd___tmp) == "phrase" ) {
				t = realmidi(Cmd___tmp,Now)
				registop(t)
				# Local_print("Ret: ",Cmd___tmp)
			}
		}
	}


	# Send string to keykit_console.py.
	# TODO: buffer + bundle messages (bundles are defined in TUIO standard)
	method send(s, path){
		if( nargs() < 2 ) path="/keykit/pyconsole/out"

		s_len = sizeof(s)
		while( s_len > Pyconsole_max_payload_len ){
			# Split text to omit oversized tcp packages?!
			sBegin = substr(s, 1, Pyconsole_max_payload_len)
			s = substr(s, 1+Pyconsole_max_payload_len, s_len-Pyconsole_max_payload_len)
			s_len -= Pyconsole_max_payload_len
			$.send(sBegin, path)
		}

		t = string($.oscsendtarget["port"])+"@"+string($.oscsendtarget["server"])
		f = open(t,"wb","osc_send")
		a = [0=path,1=s]
		if( Pyconsole_verbose > 0 ) Local_print("Sending OSC message:", a)
		mdep("osc","send",f,a)
		close(f)
	}

	method get_osc_tid(){
		return($.osctid)
	}

	# Only allow .txt or .log extension as overwrite protection.
	method normalize_logname(){
		l = Pyconsole_logfile
		if( l ~~ "^[^ \n\t\r]*[.]log$" || l ~~ "^[^ \n\t\r]*[.]txt$" ) return()
		Pyconsole_logfile = l + ".log"
	}
}

