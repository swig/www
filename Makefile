USERNAME=wsfulton
DRY_RUN=
WORKTREE=../swig

help:
	@echo "Simple makefile to create the web pages and publish to the web server"
	@echo "Targets:"
	@echo "  htmlfiles - create .html files from .ht files"
	@echo "  makedocs - copy Doc/Manual files from main git source repository working tree to local directory ready for publishing to web server"
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
	rsync $(DRY_RUN) --verbose -r --checksum --chmod=ug+w,ugo+r --delete-excluded --exclude .git --exclude .gitignore --exclude "*.sw?" --exclude "*.bak" --exclude "*.ht" --exclude "*.ph" --exclude "default.*" --exclude Makefile --exclude "*.py" --exclude "*.book" --exclude "survey/*.csv" --exclude "survey/swigsurvey" --exclude "survey/README.txt" --rsh="ssh" . $(USERNAME),swig@web.sourceforge.net:/home/groups/s/sw/swig/swigweb

rsync-dry-run:
	$(MAKE) rsync DRY_RUN=--dry-run 

release: htmlfiles makedocs rsync

makedocs:
	rm -rf Release
	mkdir -p Release
	cp $(WORKTREE)/ANNOUNCE Release/
	cp $(WORKTREE)/CHANGES Release/
	cp $(WORKTREE)/CHANGES.current Release/
	cp $(WORKTREE)/COPYRIGHT Release/
	cp $(WORKTREE)/LICENSE* Release/
	cp $(WORKTREE)/RELEASENOTES Release/
	cp $(WORKTREE)/README Release/
	rm -rf Doc4.1
	cp -rf $(WORKTREE)/Doc/Manual Doc4.1
	rm Doc4.1/*.py
	rm Doc4.1/*.bak
	rm Doc4.1/chapters
	rm Doc4.1/README
