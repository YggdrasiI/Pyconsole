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
        # Remove this func from the other arrey
        # to omid duplicates
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
