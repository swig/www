USERNAME=wsfulton
DRY_RUN=

help:
	@echo "Simple makefile to create the web pages and update/synchronise to the real web server"
	@echo "Targets: updateweb makeweb release rsync updateweb-dry-run rsync-dry-run"
	@echo "For the rsync target, use the USERNAME variable to specify your SF username, eg"
	@echo "  make rsync USERNAME=xyz"
	@echo "Use the dry-run targets to see what will get synchronised to the web server"

updateweb: makeweb rsync

updateweb-dry-run: makeweb rsync-dry-run

makeweb:
	python makeweb.py

rsync:
	rsync $(DRY_RUN) --verbose -r --checksum --chmod=ug+w,ugo+r --delete-excluded --exclude CVS --exclude .svn --exclude "*.sw?" --exclude "*.bak" --exclude "*.ht" --exclude "default.*" --exclude Makefile --exclude makeweb.py --rsh="ssh" . $(USERNAME)@shell.sf.net:/home/groups/s/sw/swig/swigweb

rsync-dry-run:
	$(MAKE) rsync DRY_RUN=--dry-run 

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
