#!/usr/bin/python
# Make the SWIG web-pages
#
# Okay. Yet another bogus rewrite of Barry's work

import string
import glob
import os
import time
import stat

def makepage(filename, extension):
    name, suffix = os.path.splitext(filename)
    f = open("default.html")
    page = f.read()
    f.close()

    # Read in the body file
    f = open(filename)
    body = f.readlines()
    f.close()
    title = body[0]
    body = "".join(body[1:])
    page = page.replace("$title", title + "  ")
    page = page.replace("$body", body)

    # Read in the corner file
    try:
        f = open(name+".corner")
        corner = f.read()
        f.close()
    except IOError:
        try:
            f = open("default.corner")
            corner = f.read()
            f.close()
        except:
            corner = ""
    
    page = page.replace("$corner", corner)

    # Read in the top file
    try:
        f = open(name+".top")
        top = f.read()
        f.close()
    except IOError:
        try:
            f = open("default.top")
            top = f.read()
            f.close()
        except:
            top = ""
    
    page = page.replace("$top", top)

    # Read in the side file
    try:
        f = open(name+".side")
        side = f.read()
        f.close()
    except IOError:
        try:
            f = open("default.side")
            side = f.read()
            f.close()
        except:
            side = ""
    
    page = page.replace("$side", side)

    # Read in the footer file
    try:
        f = open(name+".footer")
        footer = f.read()
        f.close()
    except IOError:
        try:
            f = open("default.footer")
            footer = f.read()
            f.close()
        except:
            footer = ""

    page = page.replace("$footer", footer)

    mtime = os.stat(filename)[stat.ST_MTIME]
    mstr = time.ctime(mtime)

    page = page.replace("$mtime", mstr);

    # Write out the page
    f = open(name+"."+extension, "w")
    f.write(page)
    f.close()
    print("Wrote {}.{}".format(name, extension))

files = glob.glob("*.ht")

for f in files:
    makepage(f, "html")

files = glob.glob("*.ph")

for f in files:
    makepage(f, "php")
