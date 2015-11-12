#!/usr/bin/python
"""
Search library files of keykit for #name, #usage and #desc lines to
generate help strings for this console.
"""

import sys
import os
import glob
import re
# from keykit_language import *
import pdb


def get_file_paths(path):
    if not path[-2:] == ".k":
        path += "/*.k"
    k_files = glob.glob(os.path.normpath(path))
    print("%d Files found." % len(k_files))
    return k_files

""" Search for #[X], } and, (function|class) and store line numbers.
    Then, look ahead for each function line if there was any description.
"""


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


def joinLinesByBraces(lines):
    # Join lines to generate lines with
    # balanced braches.
    il = len(lines)-1
    lines.append("")
    while il > -1:
        l = lines[il] = lines[il].strip()
        m = lines[il+1] = lines[il+1].strip()
        if("#name" in l[:5] or
           "#usage" in l[:6] or
           "#desc" in l[:5]
           ):
            pass
        elif(len(l) > 0 and l[0] == "#"):
            # Remove all comments
            lines[il] = ""
        elif(m.count("(") < m.count(")")
             or m.count("{") < m.count("}")
             or m.count("[") < m.count("]")
             ):
            lines[il] += " "+m
            lines[il+1] = ""

        il -= 1
    return lines


def remove_tab_and_newlines(lines):
    for i, l in enumerate(lines):
        l = l.replace("\t", " ")
        if len(l) > 0 and l[-1] == "\n":
            l = l[:-1]
        lines[i] = l
    return lines


def analyse_k_file(path):
    print(path)
    f = open(path)
    lines = f.readlines()
    f.close()

    # Try to detect relative path in releaton
    # to the keykit directory.
    lib_path = path.strip()
    while lib_path[0:2] == "..":
        lib_path = lib_path[3:]
    if "contrib" in lib_path:
        lib_path = lib_path[lib_path.find("contrib"):]
    elif "lib" in lib_path:
        lib_path = lib_path[lib_path.find("lib"):]

    lines = remove_tab_and_newlines(lines)

    lines = joinLinesByBraces(lines)

    search_keywords = [
        ("#name ", "n"),
        ("#usage ", "u"),
        ("#desc ", "d"),
        ("function ", "f"),
        ("class", "c"),
    ]

    positions = {-1: "}"}
    il = 0
    for l in lines:
        ls = l.strip()+" "
        bFound = False
        for a, b in search_keywords:
            if a in ls[:len(a)]:
                positions[il] = b
                bFound = True
                break
        if not bFound:
            if "}" in ls:
                positions[il] = "}"
                bFound = True
        il += 1

    # Now go backward through the dict
    doc = {}
    ils = positions.keys()
    ils.sort(reverse=True)
    for pos, linenum in enumerate(ils):
        pType = positions[linenum]
        if pType == "f":
            docElem = DocElement("function", lib_path, linenum)
            func = getFunctionName(lines[linenum])
            # Default doc element vaules
            docElem.name = func["name"]
            docElem.usage = func["name"]+"("+", ".join(func["args"])+")"
            pos2 = pos+1
            while pos2 < len(ils):
                linenum2 = ils[pos2]
                if positions[linenum2] in ["}", "f", "c"]:
                    break
                if positions[linenum2] == "n":
                    docElem.name = lines[linenum2][
                        lines[linenum2].find(" ") +
                        1:]
                if positions[linenum2] == "u":
                    docElem.usage = lines[linenum2][
                        lines[linenum2].find(" ") +
                        1:]
                if positions[linenum2] == "d":
                    docElem.desc = lines[linenum2][
                        lines[linenum2].find(" ")+1:] + "\n" + docElem.desc
                pos2 += 1

            doc[pos] = docElem
            pos = pos2+1
        else:
            pass

    return doc


def getFunctionName(codeline):
    l = codeline.strip()
    l = l[l.find("function")+8:]
    l = l.replace("{", ")")  # for fname{}
    l = l[:l.find(")")]
    l = l.strip()
    token = re.split("[(,)]", l)
    token = [t.strip() for t in token]
    ret = {"name": token.pop(0), "args": token}
    return ret


def getClassConstructor(codeline):
    pass

if __name__ == '__main__':
    try:
        path = sys.argv[1]
    except IndexError:
        print("Path to *k-files required.")
        exit(-1)

    bWrite = True
    try:
        out_filename = sys.argv[2]
    except IndexError:
        bWrite = False
        out_filename = "keykit_library.py"

    # Get list of files if path to folder given
    k_files = get_file_paths(path)
    #k_files = [k_files[0]]

    docs = []
    for k in k_files:
        docs.extend(analyse_k_file(k).values())

    # Sorting by name
    docs.sort(key=lambda el: el.name.lower())

    if bWrite:
        out_file = open(out_filename, "w")

        out_file.write(
            "try:\n\tlib_dict\nexcept NameError:\n\tlib_dict = dict()\n\n")
        out_file.write("lib_dict['"+path+"'] = [\n")
        for docElem in docs:
            out_file.write(docElem.printLibCode())

        out_file.write("]\n\n")
        out_file.close()
    else:
        for docElem in docs:
            print(docElem)
            print("")
