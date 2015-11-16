#!/usr/bin/python
"""
Search library files of keykit for #name, #usage and #desc lines to
generate help strings for this console.
"""

import sys
import os
import glob
import re


class DocElement:

    def __init__(self, elType="function", filename=None, fileline=-1):
        self.elType = elType
        self.filename = filename
        self.fileline = fileline
        self.name = ""
        self.desc = ""
        self.usage = ""

    # Write out dict with all information
    def printLibCode(self, prefix="\t"):
        s = prefix+"{\n"
        s += prefix+"\t\"type\": \""+self.elType+"\",\n"
        s += prefix+"\t\"name\": \""+self.name.strip()+"\",\n"
        s += prefix+"\t\"usage\": \"\"\""+self.usage.strip()+"\"\"\",\n"
        s += prefix+"\t\"filename\": \""+str(self.filename)+"\",\n"
        s += prefix+"\t\"fileline\": "+str(self.fileline)+",\n"
        s += prefix+"\t\"desc\": \"\"\""+self.desc.strip()+"\"\"\",\n"
        s += prefix+"},\n"
        return s

    def __str__(self):
        # self.cut_newlines()
        # Print overview
        source = ""
        if self.filename is not None:
            if self.fileline > -1:
                source = "(%s:%i)" % (self.filename,
                                      int(self.fileline))
            else:
                source = "(%s)" % (self.filename,)

        return "Name: %s%*s\nUsage: %s\nDescription: %s" % (self.name,
                                                            (60-len(self.name)),
                                                            source,
                                                            self.usage,
                                                            self.desc)


def gen_bltin():
    doc = {}
    for fusage in bltin_usage:
        func = getFunctionName(fusage)
        # Remove this func from the other array
        # to omit duplicates.
        try:
            bltin_fnames.remove(func["name"])
        except ValueError:
            pass

        docElem = DocElement("function", "bltin.c")
        docElem.name = func["name"]
        docElem.usage = func["name"]+"("+", ".join(func["args"])+")"
        # docElem.usage = fusage
        docElem.desc = ""

        doc[len(doc)] = docElem

    # Handle variables
    for varname,vardesc in bltin_variables:
        # Remove this func from the other array
        # to omit duplicates.
        try:
            bltin_fnames.remove(varname)
        except ValueError:
            pass

        docElem = DocElement("variable", "sym.c")
        docElem.name = varname
        docElem.usage = varname + " = [new value]"
        docElem.desc = vardesc
        doc[len(doc)] = docElem

    # Handle rest without usage strings
    for fname in bltin_fnames:
        if fname[0].upper() == fname[0]:
            docElem = DocElement("variable", "bltin.c")
            docElem.name = fname
            docElem.usage = fname+" = ?"
            docElem.desc = "Global variable"
        else:
            docElem = DocElement("function", "bltin.c")
            docElem.name = fname
            docElem.usage = fname+"(?)"
            docElem.desc = ""

        doc[len(doc)] = docElem


    return doc


def getFunctionName(codeline):
    l = codeline.strip()
    # l = l[l.find("function")+8:]
    l = l.replace("{", ")")  # for fname{}
    l = l[:l.find(")")]
    l = l.strip()
    token = re.split("[(,)]", l)
    token = [t.strip() for t in token]
    ret = {"name": token.pop(0), "args": token}
    return ret


# Data
bltin_fnames = [
    "typeof", "sizeof", "oldnargs", "argv", "midibytes", "substr", "subbytes",
    "rand", "error", "printf", "readphr", "exit", "oldtypeof", "split", "cut",
    "string", "integer", "phrase", "float", "system", "chdir", "tempo",
    "milliclock", "currtime", "filetime", "garbcollect", "funkey", "ascii",
    "midifile", "reboot", "refunc", "debug", "nullfunc", "pathsearch",
    "symbolnamed", "limitsof", "sin", "cos", "tan", "asin", "acos", "atan",
    "sqrt", "pow", "exp", "log", "log10", "realtime", "finishoff", "sprintf",
    "get", "put", "open", "fifosize", "flush", "close", "taskinfo", "kill",
    "priority", "onexit", "onerror", "sleeptill", "wait", "lock", "unlock",
    "object", "objectlist", "windowobject", "screen", "setmouse", "mousewarp",
    "browsefiles", "color", "colormix", "sync", "oldxy", "Redrawfunc",
    "Resizefunc", "Colorfunc", "popup", "rekeylib", "Exitfunc",
    "Errorfunc", "Rebootfunc", "Intrfunc", "coreleft", "prstack", "phdump",
    "lsdir", "attribarray", "fifoctl", "mdep", "midi", "bitmap", "objectinfo"
    # "help", only a stub. Removed to omit doubling of keywords.
]
bltin_usage = [
    "sizeof(anything)", "limitsof(phrase)", "prstack()", "phdump()",
    "taskinfo(\"list\"), taskinfo(\"id\"), or taskinfo(tid, type)",
    "typeof(anything)", "string(n)", "integer(n)", "float(n)", "phrase(n)",
    "sin(n)", "cos(n)", "tan(n)", "asin(n)", "acos(n)", "atan(n)", "sqrt(n)",
    "exp(n)", "log(n)", "log10(n)", "pow(x, y)", "readphr(fname)",
    "pathsearch(file [, path])", "ascii(integer-or-string)",
    "ascii(integer-or-string)",
    "midifile(filename) or midifile(array, filename)",
    "split(phrase-or-string)", "cut(phrase, type, ... )",
    "midibytes(byte1, byte2, byte3...)", "nargs()",
    "argv( argnum [, argnum2] )",
    "realtime( phrase [, time [, repeat [, monitor] ] ] )",
    "sleeptill( time )", "wait( tid )", "lock(name [, test] )",
    "unlock(name)", "finishoff()", "kill(tid)", "priority(task, priority)",
    "onexit(function)", "onerror(function)", "substr(string, start, length)",
    "subbytes(MIDIBYTES-phrase, start, length)", "system(cmd)",
    "filetime(cmd)", "currtime()", "milliclock()", "rand(n1 [, n2])",
    "garbcollect()", "funkey(function-key-num, function-to-call)",
    "symbolnamed(string)", "windobject(objectid, [type])", "sync()",
    "setmouse(type)", "mousewarp(x, y)", "xy(x, y) or xy(x0, y0, x1, y1)",
    "attribarray(s)", "color(n)", "colormix(n, r, g, b)", "get(fifo)",
    "put(fifo, data)", "flush(fifo)",
    "fifoctl(fifo, cmd [, arg]) or fifoctl(\"default\", cmd, arg)",
    "midi(\"input\", \"close\", midi_port_number)",
    "midi(\"input\", \"open\", midi_port_number)",
    "midi(\"input\", \"isopen\", midi_port_number)",
    "midi(\"input\", \"list/open/close/isopen\", midi_port_number)",
    "midi(\"output\", \"close\", midi_port_number)",
    "midi(\"output\", \"open\", midi_port_number)",
    "midi(\"output\", \"isopen\", midi_port_number)",
    "midi(\"output\", \"list/open/close/isopen\", midi_port_number)",
    "midi(\"portmap\", \"inport\", chan, \"outport\")", "bitmap(keyword, ...)",
    "fifosize(fifo)", "close(fifo)", "objectlist()",
    "objectinfo(object, type)", "objectinfo(object, type)"]

# Variable names from sym.c. Description partially from keyvar.xml
# ("name", "description"),
desc_note = "Value for note type."
desc_action = "Values of action() types."
desc_mouse = "Value for setmouse() and sweep()."
desc_cut = "Value for cut()."
desc_menudo = "Value for menudo()."
desc_draw = "Value for draw()."
desc_window = "Value for window()."
desc_style = "Value for style()."
desc_kill = "Value for kill()."
bltin_variables = [
    ("Abortonerr", "When set to 1, KeyKit will abort when an error occurs. The default is 0."),
    ("Abortonint", "When set to 1, KeyKit will abort when an interrupt is received. The default is 1."),
    ("Arraysort", "When set to 1, the index values in the \"for ( i in arr )\" statement will be processed in sorted order. The default is 0, so that the order of index values is not sorted."),
    ("Autoresize", "When set to 1, resizing the main KeyKit window will result in the proportionate resizing of all the individual tool windows. Default is 0, so that making the main window bigger will get you more space for new tools rather than just making the existing tools bigger."),
    ("Bendoffset", "This number controls the vertical offset of the beginning of pitch-bend controller lines in the Misc window. Default is 64."),
    ("Bendrange", "This number controls the relative size of pitch-bend controller lines in the Misc window. Default is 16384."),
    ("Chancolors", ""),
    ("Checkcount", "This controls the frequency of garbage collection activities. Default is 20."),
    ("Clicksperclock", "When Sync!=0, this is the number of KeyKit clicks per MIDI clock. Default is 1."),
    ("Clicks", "The number of clicks per beat. Default is 96."),
    ("Clocksperclick", "When Sync!=0, this is the number of MIDI clocks per KeyKit click. Default is 1. To avoid confusion when adjusting Clicksperclock and Clocksperclick you should ensure that at least one of those two variables has a value of 1."),
    ("Colornotes", ""),
    ("Colors", "This is the number of colors (including black and white) available."),
    ("Consecho", ""),
    ("Consechofifo", ""),
    ("Consinfifo", ""),
    ("Consolefifo", "The automatically-opened fifo that can be used to read characters from the console."),
    ("Consoutfifo", ""),
    ("Consupdown", ""),
    ("Current", "This phrase contains all currently-depressed notes."),
    ("Debug", ""),
    ("Debugdraw", ""),
    ("Debugfifo", ""),
    ("Debuggesture", ""),
    ("Debuginst", ""),
    ("Debugkill", ""),
    ("Debugkill1", ""),
    ("Debugmalloc", ""),
    ("Debugmidi", ""),
    ("Debugmouse", ""),
    ("Debugoff", ""),
    ("Debugrun", ""),
    ("Debugwait", ""),
    ("Defoutport", ""),
    ("Defpriority", "This is the default priority of new tasks (though normally, tasks inherit the priority of the task that spawns them)."),
    ("Defrelease", ""),
    ("Devmidi", ""),
    ("Directinput", ""),
    ("Dirseparator", "This string is the machine-dependent value that separates directory entries within a pathname. For example, on Unix, it is \"/\"."),
    ("Dragquant", "This number is used to quantize the dragging of notes with the Group tool."),
    ("Drawcount", ""),
    ("Echoport", ""),
    ("Eof", "This value is returned when you do a get() on a closed (or nonexistent) fifo."),
    ("Erasechar", ""),
    ("Errorfunc", "The function specified by this pointer is automatically called when a non-fatal execution error occurs."),
    ("Fakewrap", ""),
    ("Filter", "The value of this variable is a collection of bitflags that determines what MIDI messages are filtered out of received MIDI input. Macros for the bit values that can be set in the value of Filter are: CHANPRESSURE, CONTROLLER, PROGRAM, PRESSURE, PITCHBEND, SYSEX, POSITION, SONG, STARTSTOPCONT, and CLOCK. Default value is 0, i.e. nothing is filtered."),
    ("Font", "This string is the name of the font to be used. Default is machine-dependent, and some machines may completely ignore it."),
    ("Forceinputport", ""),
    ("Grablimit", ""),
("Graphics", "This number is non-zero whenever graphics mode is enabled."),
("Icon", ""),
("Initconfig", ""),
("Inputistty", ""),
("Interrupt", ""),
("Inverse", ""),
("Isofuncwarn", ""),
("Keypath", "This string is the list of directories in which to search for KeyKit function libraries. Default is machine-dependent, usually computed on the fly by the executable, though you can override it by defining a KEYPATH environment variable. Note: if you change Keypath after KeyKit has started executing, you need to call the rekeylib() function in order to rescan all the directories for their keylib.k files - otherwise the change will be ineffective."),
("Keyroot", ""),
("Killchar", ""),
("Loadverbose", "If non-zero, the dynamic loading of each KeyKit function is announced. Default is 0."),
("Lowcore", "When the amount of free memory falls below this number, warnings begin to be issued to encourage exiting. Default is 50000."),
("Machine", "This string holds the machine type (e.g. \"win\", \"unix\", \"amiga\")."),
("Maxatonce", "This controls how many simultaneously-depressed notes can be handled on MIDI input. Default value is 256."),
("Menujump", "If non-zero, moving the mouse into a menu's scroll bar will cause the menu to immediately jump to that position. Otherwise, scroll bar movement is only relative. Default is 0. If you have trouble interacting with the scroll bar, try setting this to 1."),
("Menuscrollwidth", "This number controls the width of the scroll bar in scrolling menus. Default is 20. If you have trouble getting on the scroll bar, increase this value."),
("Menusize", "This is the default maximum number of items in a pop-up menu. When a menu becomes larger than this, it will display a scroll bar. Default is 12."),
("Menuymargin", ""),
("Mergefilter", "If non-zero (and if Merge is non-zero), this value is a bitmask used to determine which channels are not merged from MIDI input to MIDI output. For example, if the value of Mergefilter is 41&lt;&lt;4, then channel 5 will not be merged. Any number of bits in Mergefilter can be set."),
("Merge", "If non-zero, MIDI input is merged into MIDI output. Default is 1."),
("Mfformat", "The value of this variable is the type (0,1,2) of the last MIDI file read with midifile()."),
("Mfsysextype", ""),
("Midififo", "The automatically-opened fifo that can be used to read notes from MIDI input."),
("Midifilenoteoff", ""),
("Midiinfifo", ""),
("Midioutfifo", ""),
("Midithrottle", ""),
("Millicount", ""),
("Millires", ""),
("Milliwarn", ""),
("Minbardx", ""),
("Monitorfifo", ""),
("Mousedisable", ""),
("Mousefifo", ""),
("Mousefifolimit", ""),
("Mousefifo", "The automatically-opened fifo that can be used to read events from the mouse. The items read from this fifo are arrays - the index values are \"button\", \"x\", and \"y\"."),
("Mousemoveevents", ""),
("Musicpath", "This string is the list of directories in which to search for music files. Default is machine-dependent."),
("Noval", ""),
("Nowoffset", ""),
("Now", "The current time, in clicks."),
("Nullval", ""),
("Numinst1", ""),
("Numinst2", ""),
("Objectoffset", ""),
("Offsetfilter", "If non-zero (and if Offsetpitch is non-zero), this value is a bitmask used to determine which channels are not pitch-shifted. For example, if the value of Offsetfilter is 1&lt;&lt;9, then channel 10 will not be affected. (And, in fact, 1&lt;&lt;9 is the default value of Offsetfilter.) Any number of bits in Offsetfilter can be set."),
("Offsetpitch", "If non-zero, all scheduled MIDI output will be pitch-shifted by the value of Offsetpitch."),
("Offsetportfilter", ""),
("Onoffmerge", ""),
("Optimize", ""),
("Panraster", ""),
("Pathseparator", "This string is the character that separates the components of Keypath. Default is \":\"."),
("Phraseflashnotes", "If this value is non-zero, notes within phrase windows are flashed as they are played. Default is 1. If your CPU is too busy, setting this to 0 can help a bit."),
("Prepoll", ""),
("Printend", ""),
("Printsep", ""),
("Printsplit", "When long phrase values are printed, they are broken up on separate lines (each line terminated with a backslash), and Printsplit is the number of characters on each line. The default value is 77. To disable splitting of lines entirely, set Printsplit to 0."),
("Recfilter", ""),
("Recinput", ""),
("Recorded", "This phrase collects all MIDI input (when Record is non-zero)."),
("Record", "When non-zero, recording of MIDI input is enabled. Default is 1."),
("Recsched", "When non-zero, scheduled MIDI output is included in the Recorded phrase. Default is 0."),
("Recsysex", ""),
("Redrawignoretime", ""),
("Resizefix", ""),
("Resizeignoretime", ""),
("Saveglobalsize", ""),
("Showbar", "The number of clicks between vertical measure bars. Default is 4b."),
("Showsync", ""),
("Showtext", ""),
("Slashcheck", ""),
("SubstrCount", ""),
("Sweepquant", "This number is used to quantize the sweeping of areas with sweep() and gridsweep()."),
("Sync", "If non-zero, time is advanced from clocks on MIDI input instead of being driven by the computer's clock. This allows synchronization with other MIDI devices (e.g. a drum machine or sequencer). Default is 0."),
("Taskaddr", ""),
("Tempotrack", ""),
("Textscrollsize", ""),
("Throttle", "This determins how many KeyKit instructions (internal interpreted instructions, not KeyKit statements) are executed per each check for realtime activity. Default value is 100."),
("Throttle2", ""),
("Trace", ""),
("Usewindfifos", ""),
("Version", "This string is the KeyKit version number (e.g. \"6.0a\")."),
("Volstem", "If non-zero, ``volume stems'' are displayed on notes. Default is 0."),
("Volstemsize", "This number controls the relative scale of volume stems. Default is 4."),
("Warningsleep", ""),
("Warnnegative", ""),
("Windowsys", ""),
# These are values for nt.type, also used as bit-vals for the value of Filter.
("MIDIBYTES", desc_note),
("NOTE", desc_note),
("NOTEON", desc_note),
("NOTEOFF", desc_note),
("CHANPRESSURE", desc_note),
("CONTROLLER", desc_note),
("PROGRAM", desc_note),
("PRESSURE", desc_note),
("PITCHBEND", desc_note),
("SYSEX", desc_note),
("POSITION", desc_note),
("CLOCK", desc_note),
("SONG", desc_note),
("STARTSTOPCONT", desc_note),
("SYSEXTEXT", desc_note),
# Values for action() types.  The values are intended to not
# overlap the values for interrupt(), to avoid misuse and
# also to leave open the possibility of merging the two.
("BUTTON1DOWN", desc_action),
("BUTTON2DOWN", desc_action),
("BUTTON12DOWN", desc_action),
("BUTTON1UP", desc_action),
("BUTTON2UP", desc_action),
("BUTTON12UP", desc_action),
("BUTTON1DRAG", desc_action),
("BUTTON2DRAG", desc_action),
("BUTTON12DRAG", desc_action),
("MOVING", desc_action),
# values for setmouse() and sweep()
("NOTHING", desc_mouse),
("ARROW", desc_mouse),
("SWEEP", desc_mouse),
("CROSS", desc_mouse),
("LEFTRIGHT", desc_mouse),
("UPDOWN", desc_mouse),
("ANYWHERE", desc_mouse),
("BUSY", desc_mouse),
("DRAG", desc_mouse),
("BRUSH", desc_mouse),
("INVOKE", desc_mouse),
("POINT", desc_mouse),
("CLOSEST", desc_mouse),
("DRAW", desc_mouse),
# values for cut()
("NORMAL", desc_cut),
("TRUNCATE", desc_cut),
("INCLUSIVE", desc_cut),
("CUT_TIME", desc_cut),
("CUT_FLAGS", desc_cut),
("CUT_TYPE", desc_cut),
("CUT_CHANNEL", desc_cut),
("CUT_NOTTYPE", desc_cut),
# values for menudo()
("MENU_NOCHOICE", desc_menudo),
("MENU_BACKUP", desc_menudo),
("MENU_UNDEFINED", desc_menudo),
("MENU_MOVE", desc_menudo),
("MENU_DELETE", desc_menudo),
# values for draw()D ,
("CLEAR", desc_draw),
("STORE", desc_draw),
("XOR", desc_draw),
# values for window()
("TEXT", desc_window),
("PHRASE", desc_window),
# values for style()
("NOBORDER", desc_style),
("BORDER", desc_style),
("BUTTON", desc_style),
("MENUBUTTON", desc_style),
("PRESSEDBUTTON", desc_style),
# values for kill() signals
("KILL", desc_kill),
]

if __name__ == '__main__':

    bWrite = True
    try:
        out_filename = sys.argv[1]
    except IndexError:
        bWrite = False
        out_filename = "keykit_bltin.py"

    docs = gen_bltin().values()

    # Sorting by name
    docs.sort(key=lambda el: el.name.lower())

    if bWrite:
        out_file = open(out_filename, "w")

        out_file.write(
            "try:\n\tlib_dict\nexcept NameError:\n\tlib_dict = dict()\n\n")
        out_file.write("lib_dict['build-in'] = [\n")
        for docElem in docs:
            out_file.write(docElem.printLibCode())

        out_file.write("]\n\n")
        out_file.close()
    else:
        for docElem in docs:
            print(docElem)
            print("")
