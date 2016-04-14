""" Osc client for Keykit """
import cmd
import sys
import re
import os.path

if sys.platform[0:3] == "win32":
    import pyreadline as readline
else:
    import readline  # For history, do not remove

from OSC import OSCClient, OSCMessage, OSCClientError
from socket import gethostname
from time import sleep

# For reply's
from OSC import OSCServer
from threading import Thread

# Constants
from keykit_language import *

################################################
# Attention, the console is not password protected
# Non-local IPs open your whole system!
################################################

# Default values for connection
PYCONSOLE_PORT = 3330
# PYCONSOLE_HOSTNAME = "0.0.0.0" # Invalid on windows
PYCONSOLE_HOSTNAME = "127.0.0.1"

# MY_HOSTNAME = "0.0.0.0"  # Invalid on windows
MY_HOSTNAME = "127.0.0.1"  # or
# MY_HOSTNAME = gethostname()  # or
# MY_HOSTNAME = "192.168.X.X"

# Makes ANSI escape character sequences (for producing colored terminal
# text and cursor positioning) work under MS Windows.
# Note that colouring does not work in Git bash (Win), but Cmd.exe.
USE_COLORAMA = True

# Storage file for history
PYCONSOLE_HIST_FILE = ".pyconsole.history"

MY_PROMPT = ''
# MY_PROMPT = 'key> '

################################################

if USE_COLORAMA:
    from colorama import init, Fore, Back, Style
    init()
    ColorOut = Fore.BLUE
    ColorWarn = Fore.RED
    ColorReset = Style.RESET_ALL
else:
    ColorOut = ""
    ColorWarn = ""
    ColorReset = ""


class KeykitShell(cmd.Cmd):
    intro = """
    Welcome to the Keykit shell. Type help or ? to list commands.
    Connect to local keykit server with 'connect port'.
    Exit shell with 'bye'.
    """

    remote_server_adr = (PYCONSOLE_HOSTNAME, PYCONSOLE_PORT)
    local_server_adr = (MY_HOSTNAME, PYCONSOLE_PORT + 1)

    prompt = ''

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, args, kwargs)
        self.client = None
        self.server = None
        self.run = False
        # Start client and server with default values
        self.init()

    def init(self):
        # Client
        if(self.client is not None):
            self.client.close()
        self.client = OSCClient()
        try:
            self.client.connect(self.remote_server_adr)
        except ValueError:
            warn("Connectiong failed. Invalid port?")

        # Server
        if self.server is not None:
            self.server.stop()
            self.server_thread.join()
        self.server = Server(self.local_server_adr)
        self.server_thread = Thread(target=self.server.start)
        self.server_thread.start()

        # Inform keykit programm to use this as target
        try:
            self.client.send(OSCMessage("/keykit/pyconsole/target",
                                        list(self.local_server_adr)))
        except OSCClientError:
            warn("Sending of /target message failed. Pyconsole.k offline?")

        self.run = True

    def is_run(self):
        """ True between self.init() and self.close() calls. """
        return self.run

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    # ----- internal shell commands -----
    def do_connect(self, arg):
        """Connect to OSC-Server:                       connect [PORT] [HOSTNAME]

        Default PORT: %i
        Default HOSTNAME: %s
        """
        words = arg.split(' ')
        if len(words) > 1:
            self.remote_server_adr = (str(words[1]), int(words[0]))
        elif len(words) > 0:
            self.remote_server_adr = (self.remote_server_adr[0], int(words[0]))

        self.local_server_adr = (
            self.local_server_adr[0],
            self.remote_server_adr[1] + 1)
        self.init()

    do_connect.__doc__ %= (remote_server_adr[1], remote_server_adr[0])

    def do_verbose(self, arg):
        """Set verbose level variable of pyconsole.k:    verbose [0|1]"""
        if arg == "":
            arg = "1"
        try:
            self.client.send(
                OSCMessage("/keykit/pyconsole/verbose", [int(arg)]))
        except OSCClientError:
            warn("Sending failed")

    def do_bye(self, arg):
        """Close keykit shell window and exit:          bye

        It mutes the output of keykit, too.
        """
        warn('Quitting keykit shell.')
        # self.send("stop()")
        self.send("alloff()")
        self.close()
        return True

    '''
    def do_exit(self, arg):
        """Close keykit shell window and exit:  exit"""
        return self.do_bye(arg)

    def do_quit(self, arg):
        """Close keykit shell window and exit:  quit"""
        return self.do_bye(arg)
    '''

    loopVarIdx = 0

    def do_loop(self, arg):
        """Start test loop to check asynchron beheaviour."""

        # It is important to use different loop variable names for each call!
        i = chr(65+self.loopVarIdx)
        self.loopVarIdx = (self.loopVarIdx + 1) % 50
        s = '''for ( i%s=0; i%s<20; i%s++) { printf("l");
        for(j%s=0;j%s<i%s;j%s++){printf("o")}; print("p");
        sleeptill(Now+%s) }''' % (i,
                                  i,
                                  i,
                                  i,
                                  i,
                                  i,
                                  i,
                                  "2b")
        s = s.replace("\t", "")
        self.default(s)

    def do_test(self, arg):
        """Send test commands to keykit backend."""
        # self.do_loop("")
        self.default("print(\"Send irregular line\")")
        self.default("i = 0/0")

    def default(self, line):
        """Send input as keykit command (OSC message)"""
        self.send(line)
        # Restore prompt
        sys.stdout.write("%s" % (MY_PROMPT))

    def do_help(self, args):
        """%s"""
        if args == "":
            cmd.Cmd.do_help(self, args)
            # Apend commands with irregular python function names
            print("Keykit help")
            print("===========")
            print(self.do_khelp.__doc__)
            print("Further commands")
            print("================")
            print("[keykit cmd] ! !! !log ![num] [phrase]??\n")
        elif args == "!":
            print("List history of Keykit commands.")
        elif args == "!!":
            print("Repeat last Keykit command.")
        elif args == "??" or args == "[phrase]??":
            print("Syntax for phrase filtering:\n"
                  " [phrase] { condition-with-?? }"
                  " ?? will replaced with each note in the original phrase.\n"
                  " Example:\n"
                  " 'c,d,e,f,g' {??.pitch > 'e'} would be equal to 'ft288,g'\n"
                  "")
        elif args == "!log":
            print(
                "Write history of commands into logfile.\n" +
                "The variable Pyconsole_logfile controls the name," +
                "but should ends with .log or .txt.")
        elif args[0] == "!":
            print("![num] Repeat num-th command of history.")
        else:
            cmd.Cmd.do_help(self, args)

    do_help.__doc__ %= (cmd.Cmd.do_help.__doc__)

    def do_khelp(self, args):
        """khelp [regex pattern] lists matching library functions/important variables.

        If a more detailed description exists the entry will be
        marked with '*'.
        Patterns with an unique result show the description.
        Note: The lookup table is big, but incomplete.
        """

        kname = args.strip()
        if kname == "":
            kname = ".*"
        kname = "^"+kname+"$"
        bRegexOk = True
        try:
            re_name = re.compile(kname, re.IGNORECASE)
        except:
            bRegexOk = False
            warn("Can not compile regular expression.")
            return

        lElems = []
        if bRegexOk:
            lElems.extend([i for i in KEYKIT_LIB_FUNCTIONS
                           if re.search(re_name, i["name"])
                           is not None])
            lElems.extend([i for i in KEYKIT_LIB_CLASSES
                           if re.search(re_name, i["name"])
                           is not None])
            lElems.extend([i for i in KEYKIT_LIB_OTHER
                           if re.search(re_name, i["name"])
                           is not None])

        l = ["%s%s" % (el["name"],
                       "*" if el["desc"] != "" else "")
             for el in lElems]
        if(len(l) == 0):
            warn("No Keykit function/class/etc found for %s" % (kname,))
        elif(len(l) > 20):
            print(keykit_library_abc(l))
        elif(len(l) > 2):
            print(" ".join(l))
        elif(len(l) > 1):
            # The used regex ignores the case. Check if the matches
            # only differs by the case and print out help for both matches.
            # Assumption: Three keywords with the same lowercase never exists.
            if( lElems[0]["name"].lower()
                    == lElems[1]["name"].lower() ):
                print(keykit_library_help(lElems[0]))
                print(keykit_library_help(lElems[1]))
            else:
                print(" ".join(l))
        else:
            print(keykit_library_help(lElems[0]))

    def do_EOF(self, line):
        warn("Ctrl+D pressed. Quitting keykit shell.")
        self.close()
        return True

    def close(self):
        self.run = False
        if(self.client is not None):
            self.client.close()
        if self.server is not None:
            self.server.stop()
            # self.server_thread.join()

    def send(self, s):
        try:
            self.client.send(OSCMessage("/keykit/pyconsole/in", [s]))
        except OSCClientError:
            warn("Sending of '%s' failed" % (s,))

    def update_lsdir(self, text, timeout):
        #import pdb; pdb.set_trace()
        # sleep(timeout)
        dirname = os.path.dirname(text)
        basename = os.path.basename(text)
        if len(dirname) == 0:
            dirname = "."
        self.server.keykit_lsdir = None
        try:
            self.client.send(OSCMessage("/keykit/pyconsole/lsdir", [dirname]))
        except OSCClientError:
            warn("Sending of '%s' failed" % (s,))

        while timeout > 0 and self.server.keykit_lsdir is None:
            timeout -= 0.1
            sleep(0.1)
        if self.server.keykit_lsdir is not None:
            # Default readline beheaviour
            # return [i[0] for i in self.server.keykit_lsdir
            #        if i[0].startswith(basename)]

            # Add readline workarounds
            # Include Path separator for folders
            ret = ["%s%s" % (i[0], os.path.sep if i[1] else "")
                    for i in self.server.keykit_lsdir
                    if i[0].startswith(basename)]
            # Omit adding of closing quotes, see
            # https://github.com/ipython/ipython/issues/1172
            if len(ret) == 1 and ret[0][-1] == os.path.sep:
                ret.append(ret[0]+" ")

            # Close path of files if only one element is available
            # Readline completes with " on its own, too. (This depends 
            # on the list of delimters). The last expression should prevent double adding of ".
            if(len(ret) == 1 and ret[0][-1] != os.path.sep and
                    os.path.dirname(text) != ''):
                ret[0] += '"'
            return ret

        return []

# -----------------------------------------


class Server():

    """Listener to collect results of Keykit server.

    (Adaption of OSC package example.)
    """

    def __init__(self, server_adr):
        self.server = OSCServer(server_adr)
        self.server.socket.settimeout(3)
        self.run = True
        self.timed_out = False

        # funny python's way to add a method to an instance of a class
        # import types
        # self.server.handle_timeout = types.MethodType(
        #   self.handle_timeout, self.server)
        # or
        self.server.handle_timeout = self.handle_timeout

        # Handler
        self.server.addMsgHandler("/quit", self.quit_callback)
        self.server.addMsgHandler("/keykit/pyconsole/out", self.print_callback)
        self.server.addMsgHandler("/keykit/pyconsole/err", self.err_callback)
        self.server.addMsgHandler(
            "/keykit/pyconsole/start",
            self.print_callback)
        self.server.addMsgHandler("/keykit/pyconsole/lsdir", self.dir_callback)

    def handle_timeout(self, server=None):
        self.timed_out = True

    def each_frame(self):
        # clear timed_out flag
        self.timed_out = False
        # handle all pending requests then return
        while not self.timed_out and self.run:
            self.server.handle_request()
            # Line reached after each socket read
            sleep(.05)

    def start(self):
        # print("Wait on client input...")
        sys.stdout.write("%s" % (MY_PROMPT))
        sys.stdout.flush()
        while self.run:
            self.each_frame()
            # Line reached after each socket timeout
            sleep(1)

    def stop(self):
        self.run = False
        # Invoke shutdown. Socket still wait on timeout...
        try:
            import socket
            self.server.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass

        self.server.close()

    # Callbacks
    def quit_callback(self, path, tags, args, source):
        self.run = False

    def print_callback(self, path, tags, args, source, textColor=ColorOut):
        current_input = readline.get_line_buffer()

        # Add Tab at every input line
        out = args[0].replace("\n", "\n\t")

        # Delete current input, insert output and add input again.
        # \r : Carriage return, \033[K : Delete everything after the cursor.
        sys.stdout.write("\r\033[K")
        sys.stdout.write(
            "\t%s%s%s\n%s%s" %
            (textColor,
             out,
             ColorReset,
             MY_PROMPT,
             current_input))
        sys.stdout.flush()

    def err_callback(self, path, tags, args, source):
        """ Same as print_callback but mark output as error. """
        self.print_callback(path, tags, args, source, ColorWarn)

    def dir_callback(self, path, tags, args, source):
        """ Store current working dir for tab completion.
            This is mainly releated to chdir() and lsdir().
        """
        lsdir_string_part = args[0]
        if lsdir_string_part[0] == "^":
            self.keykit_lsdir_string = lsdir_string_part
        else:
            self.keykit_lsdir_string += lsdir_string_part

        if self.keykit_lsdir_string[-1] == "$":
            try:
                lsdir = []
                # Convert string into list of files. Second argument flags
                # directories.
                # Example string:  ^["foldername"=1,"filename"=0]$
                re_entries = '".+?"=[01][,\]]'
                entries = re.finditer(re_entries, self.keykit_lsdir_string)
                for entry in entries:
                    sname = entry.group()[1:-4]
                    bFolder = entry.group()[-2] == "1"
                    lsdir.append((sname, bFolder))

                self.keykit_lsdir = lsdir
            except:
                sys.stderr.write("(dir_callback) Unable to fetch folder content.")
                self.keykit_lsdir = []


# Setup tab completion
class Completer:

    def __init__(self, completer=None, shell=None, bBind=True):
        self.prefix = None
        self.shell = shell
        self.completer = \
            self.complete_advanced if completer is None else completer
        if bBind:
            readline.parse_and_bind('tab: complete')
            readline.set_completer(self.complete)
            # Use default limiters but remove '-'
            # `~!@#$%^&*()-=+[{]}\|;:'",<>/?
            self.default_delims = readline.get_completer_delims()
            readline.set_completer_delims(self.default_delims.replace("-", ""))

    def complete(self, prefix, index):
        if prefix != self.prefix:
            # New prefix. Find all words that start with this prefix.
            self.matching_words = self.completer(prefix, index)
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

    def complete_simple(self, text, state):
        """Re-uses the lists the vim syntax file."""
        l = [i for i in KEYKIT_FUNCTIONS if i.startswith(text)]
        l.extend([i for i in KEYKIT_STATEMENTS if i.startswith(text)])
        l.extend([i for i in PYCONSOLE_CONSTANTS if i.startswith(text)])
        return l
        # if(state < len(l)):
        #    return l[state]
        # return None

    def complete_advanced(self, text, state):
        """Uses the output of the parser keykit_gen_library.py."""
        l = []

        # Completion of paths
        l.extend(self.complete_path(text, state))

        if len(l) == 0:
            l.extend([i["name"] for i in KEYKIT_LIB_FUNCTIONS
                      if i["name"].startswith(text)])
            l.extend([i["name"] for i in KEYKIT_LIB_CLASSES
                      if i["name"].startswith(text)])
            l.extend([i["name"] for i in KEYKIT_LIB_OTHER
                      if i["name"].startswith(text)])

        return l
        # if(state < len(l)):
        #    return l[state]
        # return None

    def complete_path(self, text, state):
        """ Search input line for several function names and expand
        arguments which are knows as file/path arguments.
        The search for the function name does not respect nesting, etc.
        """
        line_beginning = readline.get_line_buffer()[:readline.get_begidx()]
        line_beginning = line_beginning[max(0,line_beginning.rfind(";")):]
        if "(" not in line_beginning:
            return []

        """ Expand file paths for several functions. """
        candidates = [i for i in KEYKIT_FILE_RELEATED_FUNCTIONS
                      if i[0] in line_beginning]
        if len(candidates) == 0:
            return []

        for candidate in candidates:
            re_split_args = "([^=]*=)?\s*%s\s*\(([^,]+,){%d}" % candidate
            if re.search(re_split_args, line_beginning) is not None:
                # We can not use 'text' due the default delims setting.
                # It would be too short.
                text2 = readline.get_line_buffer()
                text2 = text2[text2.rfind('"')+1:]
                return self.shell.update_lsdir(text2, 3)
                break

        return []


def warn(s):
    print(ColorWarn+s+ColorReset)

try:
    lib_dict
except NameError:
    lib_dict = dict()

KEYKIT_LIB_FUNCTIONS = []
KEYKIT_LIB_CLASSES = []
KEYKIT_LIB_OTHER = []


def load_keykit_library():
    """Loads the structure generated by keykit_gen_library.py."""
    import keykit_bltin
    lib_dict.update(keykit_bltin.lib_dict)
    import keykit_library
    lib_dict.update(keykit_library.lib_dict)

    # create list of function names
    for folder in lib_dict.values():
        # KEYKIT_LIB_FUNCTIONS.extend(folder)
        for doc in folder:
            if doc["type"] == "function":
                KEYKIT_LIB_FUNCTIONS.append(doc)
            if doc["type"] == "variable":
                KEYKIT_LIB_OTHER.append(doc)


def keykit_library_help(el):
    """Parses one element of above structure."""
    source = ""
    out = "\n%11s: %%s%%s%%s%%*s\n%11s: %%s\n%11s: %%s\n" % (
        "Name", "Usage", "Description"
    )
    if el["filename"] is not None:
        if el["fileline"] > -1:
            source = "(%s:%i)" % (el["filename"], int(el["fileline"]))
        else:
            source = "(%s)" % (el["filename"],)

    desc = el["desc"] if el["desc"] is not "" else "-"
    return out % (ColorOut, el["name"], ColorReset,
                  (60-len(el["name"])),
                  source,
                  el["usage"],
                  desc)


def keykit_library_abc(elems):
    """Split elements into separate chunks for first character."""

    # Combine 'x' and 'X' fields
    elems.sort(key=lambda el: el.lower())

    char = elems[0][0].lower()
    n = 0
    s = char.upper()+"\n"
    for el in elems:
        if el[0].lower() == char:
            n += 1
            if n > 4:
                s += "\n"
                n = 0

            s += "%15s%s " % (el, "" if el[-1] == "*" else " ")
        else:
            char = el[0].lower()
            n = 0
            s += "\n%s\n" % (char.upper(),)
            s += "%15s " % (el,)
    return s


def start():
    shell = KeykitShell()
    completer = Completer(shell=shell)

    # Load history
    try:
        readline.read_history_file(PYCONSOLE_HIST_FILE)
    except IOError:
        warn("Can't read history file")

    # Load help system in background thread
    doc_thread = Thread(target=load_keykit_library)
    doc_thread.start()

    # Start Input loop
    while shell.is_run():
        try:
            shell.cmdloop()
        except KeyboardInterrupt:
            # Just restart cmd loop. Qutting was shifted to Ctrl+D...
            shell.intro = ""
            warn("^C")
        except TypeError:
            warn("Type error. Quitting keykit shell.")
            shell.close()

    # Write history
    try:
        readline.set_history_length(100000)
        readline.write_history_file(".pyconsole.history")
    except IOError:
        warn("Can't write history file")

if __name__ == '__main__':
    start()
