#!/usr/bin/python
# Make the SWIG web-pages
#
# Okay. Yet another bogus rewrite of Barry's work

import string
import glob
import os
import time
import stat
import subprocess

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

# Check that /usr/bin/curl exists (required by magpierss)
subprocess.check_output(["/usr/bin/curl", "--version"])

files = glob.glob("*.ht")

for f in files:
    makepage(f, "html")

files = glob.glob("*.ph")

# The .ph files create .php files which used to run on the web server.
# All external access from the web server is now blocked (the RSS news feed is blocked).
# Instead we use php to generate the html and then upload html static pages to the server.
for f in files:
    base = os.path.splitext(f)[0]
    php_filename = base + ".php"
    html_filename = base + ".html"
    if os.path.exists(php_filename):
        os.remove(php_filename)
    if os.path.exists(html_filename):
        os.remove(html_filename)
    makepage(f, "php")
    html_string = subprocess.check_output(["php", php_filename])
    # TODO Python 3 reports: write() argument must be str, not bytes 
    # html_file = open(html_filename, "wb")
    html_file = open(html_filename, "w")
    html_file.write(html_string)
    print("Wrote {}".format(html_filename))
