USERNAME=wsfulton

help:
	echo "Simple makefile to create the web pages and update/synchronise to the real web server"
	echo "Targets: updateweb makeweb release rsync"

updateweb: makeweb rsync

makeweb:
	python makeweb.py

rsync:
	rsync -r --exclude .svn --exclude *.swp --rsh="ssh" . $(USERNAME)@shell.sf.net:/home/groups/s/sw/swig/swigweb

release: makeweb makedocs rsync

makedocs:
	mkdir -p Release
	cp ../trunk/ANNOUNCE Release/
	cp ../trunk/CHANGES Release/
	cp ../trunk/CHANGES.current Release/
	cp ../trunk/LICENSE Release/
	cp ../trunk/NEW Release/
	cp ../trunk/README Release/
	cp ../trunk/TODO Release/
	rm -rf Doc1.3
	cp -rf ../trunk/Doc/Manual Doc1.3
