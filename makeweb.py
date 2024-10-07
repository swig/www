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
import re
import sys
import feedparser # install using: 1) sudo apt install python3-feedparser or 2) pip3 install feedparser

if sys.version_info[0:2] < (3, 0):
    raise RuntimeError("Python 3 required")

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

def grab_rss_newsfeed(rss_limit, html_file):
    url = "https://sourceforge.net/p/swig/news/feed?limit={}".format(rss_limit) # Project news releases (including full text of news items)
    feed = feedparser.parse(url)
    html_file.write(b"<dl>")
    count = 0
    for newsitem in feed.entries:
        count = count + 1
        publish_date = time.strftime("%Y/%m/%d", newsitem.published_parsed)
        link = newsitem.link
        title = newsitem.title
        description = newsitem.description
        # print("processing entry {} {}".format(count, title))
        line = '<p><dt><b>{}</b> - <a href="{}">{}</a></dt><dd>{}</dd></dt></p>'.format(publish_date, link, title, description)
        html_file.write(bytes(line, encoding="utf-8"))
    html_file.write(b"</dl>\n")


files = glob.glob("*.ht")

for f in files:
    makepage(f, "html")

files = glob.glob("*.ph")

# The .ph files used to create .php files which used to run on the web server.
# All external access from the web server is now blocked (the RSS news feed is blocked).
# Instead we create .tmp files prior to creating .html files and then upload html static pages to the server.
for f in files:
    base = os.path.splitext(f)[0]
    tmp_filename = base + ".tmp"
    html_filename = base + ".html"
    if os.path.exists(tmp_filename):
        os.remove(tmp_filename)
    if os.path.exists(html_filename):
        os.remove(html_filename)
    makepage(f, "tmp")

    html_file = open(html_filename, "wb")
    tmp_file = open(tmp_filename, "rb")
    for line in tmp_file:
        if b"<?python" in line:
            pattern = re.compile(r"<\?python rss_limit=(\d+)\?>")
            stripped_line = line.strip().decode('utf-8')
            match = pattern.match(stripped_line)
            if not match:
                raise RuntimeError("Incorrectly formatted '<?python' line in {}: '{}'".format(f, stripped_line))
            rss_limit = int(match.group(1))
            grab_rss_newsfeed(rss_limit, html_file)
        else:
            html_file.write(line)
    html_file.close()

    print("Wrote {}".format(html_filename))
