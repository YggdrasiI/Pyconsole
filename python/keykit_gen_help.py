#!/usr/bin/python
"""
Search library files of keykit for #name, #usage and #desc lines to
generate help strings for this console.
"""

import cmd
import sys
import os
import glob
from keykit_language import *

def get_file_paths(path):
    if not path[-2:] == ".k":
        path += "/*.k"
    k_files = glob.glob( os.path.normpath(path) )
    print("%d Files found." %len(k_files) )
    return k_files

""" Search for #[X], } and, (function|class) and store line numbers.
    Then, look ahead for each function line if there was any description.
"""
def analyse_k_file(path):
    print(path)
    f = open(path)
    lines = f.readlines()
    f.close()

    positions = {-1 : "}"}
    il = 0
    for l in lines:
        if "#name" in l.strip()[:5]:
            positions[iL] = "n"
        if "#usage" in l.strip()[:6]:
            positions[iL] = "u"
        if "#desc" in l.strip()[:5]:
            positions[iL] = "d"
        if "function" in l.strip()[:8]:
            positions[iL] = "f"
        if "class" in l.strip()[:5]:
            positions[iL] = "c"
        if "}" in l.strip()[:1]:
            positions[iL] = "}"
        il += 1

    # Now go backward throuh the dict
    ils = positions.keys().sort(reverse=True)
    for pos,linenum in enumerate(ils):
        pType = positions[linenum]
        if pType == "f" or pType == "c":
            # Reset string buffer
            fname = "function "+"Todo"
            fdecs = "None"
            fusage = "None"
            pos2 = pos-1
            while( pos2>0 ):
                linenum2 = ils[pos2]
                if positions[linenum2] == "}":
                    break
                if positions[linenum2] == "n":
                if positions[linenum2] == "u":
                if positions[linenum2] == "d":

if __name__ == '__main__':
    try:
        path = sys.argv[1]
    except IndexError:
        print("Path to *k-files required.")
        exit(-1)

    k_files = get_file_paths(path)
    analyse_k_file( k_files[0] )
