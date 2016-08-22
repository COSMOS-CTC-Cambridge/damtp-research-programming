ORGFILES=course.org plans.org slides.org todo.org modules/algorithms.org modules/io_viz.org modules/optimisation.org modules/practices.org modules/prototyping.org modules/python.org modules/requirements_for_environment.org modules/shell.org modules/mpi.org modules/unfinished.org
MDFILES=course.md modules/algorithms.md modules/io_viz.md modules/optimisation.md modules/practices.md modules/prototyping.md modules/python.md modules/requirements_for_environment.md modules/shell.md modules/mpi.md modules/unfinished.md
SRCFILES=codes/python/distributed_computing_interactive.py codes/python/ipyparallel_and_mathematica.py codes/python/mixed_mode_mapreduce.py codes/python/mpi_hello_world.py codes/python/profile_example.py
PNGFILES=modules/images/boundary_conditions.png modules/images/ghosts.png modules/images/MPI_subarray.png
DELETEFILESONRELEASE = $(filter-out Makefile,$(wildcard *))

BRANCH=$(shell git symbolic-ref -q --short HEAD)

.PHONY: all release checkbranch changebranch processfiles

all: release

release: | checkbranch changebranch processfiles
	rm -r ${ORGFILES}
	find -name '*.org'|xargs rm
	rm -rf APC524 GitSlides modules/MyRepo.orig modules/ServerRepo
	git add -A
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

processfiles: ${MDFILES} ${SRCFILES} ${PNGFILES}
	python3 codes/python/domain_decomp_scaling.py modules/images/domain_decomp_scaling.png

${SRCFILES} ${PNGFILES}: ${MDFILES}

%.md: %.org
	# pandoc fails to process ditaa, otherwise fine: pandoc --from org --to markdown_github --output=$@ $<
	# the next line will do the trick but with the annoying side-effect that one has to load the whole emacs startup thingy
	# TODO!!! FIXME: the (sit-for 5) waits for 5 units of time because we have no way of waiting for pandoc to finish before exiting emacs!
	# TODO!!! FIXME: this only works wuth --user juhaj and SOME magic SOMEWHERE in ~juhaj...
	/usr/bin/emacs -nw --batch --user $(shell whoami) $< --eval '(org-mode)' --eval '(org-babel-tangle)' --eval '(org-pandoc-export-to-markdown_github)' --eval '(sit-for 5)'
	ipython3 codes/python/exportcleanup.py -- $@

cleanSRC:
	rm ${SRCFILES} ${MDFILES} ${PNGFILES}

clean: cleanSRC
	@find -name '*.tex' -o -name '*.pyc' -o -name '*~' -o -name '*.pdf' -o -name '*.md' |xargs echo
