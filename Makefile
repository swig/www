USERNAME=wsfulton
DRY_RUN=

help:
	@echo "Simple makefile to create the web pages and publish to the web server"
	@echo "Targets:"
	@echo "  htmlfiles - create .html files from .ht files"
	@echo "  makedocs - copy files from trunk working copy to local directory ready for publishing to web server"
	@echo "  rsync - publish local files to web server"
	@echo "  rsync-dry-run - dry run of above"
	@echo "  updateweb - both htmlfiles and rsync targets"
	@echo "  updateweb-dry-run - dry run of above"
	@echo "  release - htmlfiles and makedocs and rsync targets"
	@echo "For the rsync target, use the USERNAME variable to specify your SF username, eg"
	@echo "  make rsync USERNAME=xyz"
	@echo "Use the dry-run targets to see what will get synchronised to the web server"

updateweb: htmlfiles rsync

updateweb-dry-run: htmlfiles rsync-dry-run

htmlfiles:
	python makeweb.py

rsync:
	rsync $(DRY_RUN) --verbose -r --checksum --chmod=ug+w,ugo+r --delete-excluded --exclude .git --exclude "*.sw?" --exclude "*.bak" --exclude "*.ht" --exclude "*.ph" --exclude "default.*" --exclude Makefile --exclude makeweb.py --rsh="ssh" . $(USERNAME),swig@web.sourceforge.net:/home/groups/s/sw/swig/swigweb

rsync-dry-run:
	$(MAKE) rsync DRY_RUN=--dry-run 

release: htmlfiles makedocs rsync

makedocs:
	rm -rf Release
	mkdir -p Release
	cp ../trunk/ANNOUNCE Release/
	cp ../trunk/CHANGES Release/
	cp ../trunk/CHANGES.current Release/
	cp ../trunk/COPYRIGHT Release/
	cp ../trunk/LICENSE* Release/
	cp ../trunk/RELEASENOTES Release/
	cp ../trunk/README Release/
	rm -rf Doc2.0
	cp -rf ../trunk/Doc/Manual Doc2.0
