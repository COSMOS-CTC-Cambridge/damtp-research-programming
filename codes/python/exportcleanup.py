#!/usr/bin/env python3

import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("files", type=str, metavar="file(s)", nargs="+", help="Source file to fix.")
args = parser.parse_args()

for infn in args.files:
    with open(infn,"r") as inf: indata=inf.readlines()
    for lineidx,inline in enumerate(indata[:-1]):
        '''If previous line was "[\s]+-.*", current line is "[\s]+" and next is again
        "[\s]+-.*" we want to remove current line from output'''
        if (lineidx == 0):
            outdata = [indata[0]]
        else:
            if (re.match("^[\s]+$", inline)):
                if (re.match("^[\s]*-[\s].*", indata[lineidx-1])):
                    if (re.match("^[\s]*-[\s].*", indata[lineidx+1])):
                        continue
            elif (re.search("![[]][(]file:", inline)):
                inline=inline.replace("file:","")
            outdata.append(inline)
    open(infn,"w").writelines(outdata)
