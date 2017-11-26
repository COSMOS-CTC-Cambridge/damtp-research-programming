# Use this to release: git checkout master && git pull && git checkout student && git pull && git push && make release && git push git@github.com:juhaj/damtp-research-programming.git student:master
ORGFILES=course.org plans.org slides.org todo.org \
	modules/algorithms.org \
	modules/debugging.org \
	modules/introduction.org \
	modules/io_viz.org \
	modules/mpi.org \
	modules/optimisation.org \
	modules/practices.org \
	modules/practices2.org \
	modules/prototyping.org \
	modules/python.org \
	modules/requirements_for_environment.org \
	modules/shell.org \
	modules/sshetal.org \
	modules/unfinished.org \
	modules/start.org
MDFILES_ALL=modules/introduction.md \
	modules/practices.md \
	modules/practices2.md \
	modules/python.md \
	modules/algorithms.md \
	modules/mpi.md \
	modules/prototyping.md \
	modules/io_viz.md \
	modules/optimisation.md \
	modules/requirements_for_environment.md \
	modules/shell.md \
	modules/sshetal.md \
	modules/unfinished.md \
	modules/debugging.md 
MDFILES=modules/introduction.md \
	modules/shell.md \
	modules/sshetal.md \
	modules/practices.md \
	modules/practices2.md \
	modules/python.md \
	modules/mpi.md \
	modules/algorithms.md \
	modules/prototyping.md \
	modules/io_viz.md
SRCFILES=$(shell grep ':tangle "' modules/*.org|sed 's/\(.*:tangle "\)\([^"]*\)\(.*\)/\2/'|sort -u|sed 's|^../||')
PDFFILES=
PNGFILES=modules/images/boundary_conditions.png modules/images/ghosts.png modules/images/MPI_subarray.png modules/images/git_dag_1.png modules/images/git_dag_2.png modules/images/git_dag_3.png modules/images/git_dag_4.png modules/images/git_dag_5.png modules/images/git_dag_6.png modules/images/git_dag_7.png modules/images/git_dag_8.png modules/images/git_dag_9.png  modules/images/domain_decomp_strong_scaling.png modules/images/python_package_structure.png


DELETEFILESONRELEASE = $(filter-out Makefile,$(wildcard *))

BRANCH=$(shell git symbolic-ref -q --short HEAD)

.PHONY: all checkbranch changebranch export processfiles release 

all: release

export: ${MDFILES}

release: | checkbranch changebranch processfiles
	rm -fr ${ORGFILES}
	find -name '*.org'|grep -v README.org|xargs rm -f
	rm -rf APC524 GitSlides modules/MyRepo.orig modules/ServerRepo
	git add -A
	git status
	git commit --message="Released at $(shell date --iso-8601=seconds)"

checkbranch:
	# refuse to do anything unless on student branch
ifneq (student, ${BRANCH})
	$(error You must be on the branch "student" to release)
endif

changebranch:
	# remove everything in the student branch and get a copy of master on it
	#git checkout student
	git rm -fr --ignore-unmatch -- ${DELETEFILESONRELEASE}
	git clean -d --force
	git checkout origin/master -- .
	git pull
	git checkout origin/master -- .

processfiles: ${MDFILES} ${SRCFILES} ${PNGFILES} ${PDFFILES}
	python3 codes/python/domain_decomp_scaling.py modules/images/domain_decomp_scaling.png

${SRCFILES} ${PNGFILES}: ${MDFILES}

%.md: %.org
	# pandoc fails to process ditaa, otherwise fine: pandoc --from org --to markdown_github --output=$@ $<
	# the next line will do the trick but with the annoying side-effect that one has to load the whole emacs startup thingy
	# TODO!!! FIXME: the (sit-for 5) waits for 5 units of time because we have no way of waiting for pandoc to finish before exiting emacs!
	# TODO!!! FIXME: this only works wuth --user juhaj and SOME magic SOMEWHERE in ~juhaj...
	/usr/bin/emacs -nw --batch --user $(shell whoami) $< --eval '(org-mode)' --eval '(setq org-confirm-babel-evaluate nil)' --eval '(org-babel-tangle)' --eval '(org-pandoc-export-to-markdown_github)' --eval '(sit-for 5)'
	ipython3 codes/python/exportcleanup.py -- $@

%.pdf: %.org
	ln -s modules/images images
	/usr/bin/emacs -nw --batch --user $(shell whoami) $< --eval '(org-mode)' --eval '(setq org-confirm-babel-evaluate nil)' --eval '(org-babel-tangle)' --eval '(org-pandoc-export-to-latex-pdf)'
	rm -rf images

cleanSRC:
	rm -f ${SRCFILES}
	rm -f ${MDFILES} ${PNGFILES}

clean: cleanSRC
	@find -name '*.tex' -o -name '*.pyc' -o -name '*.pyx' -o -name '*.pyxc' -o -name '*~' -o -name '*.pdf' -o -name '*.md' |grep -v APC|xargs echo
