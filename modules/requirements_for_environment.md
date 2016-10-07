Study environment needs
=======================

PETSc
-----

-   3.7

virtualenv
----------

-   assume installed in

pip
---

-   8.1.2

petsc4py
--------

-   3.7

ipyparallel
-----------

-   5.0.1

jupyter
-------

-   1.0.0

notedown
--------

-   1.5.0

bash<sub>kernel</sub>
---------------------

-   0.4.1
-   

nbextensions
------------

-   <https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip>

ipywidgets
----------

-   4.1.1 (!!!)

Try:
----

-   Install PETSc
-   
-   
-   
-   
-   you need to run jupyter at least once now, lest the next install fails with a missing jupyter share directory
-   generate (default) config:
-   
-   Enable bash kernel:
-   Finally add `c.NotebookApp.contents_manager_class ` 'notedown.NotedownContentsManager'= and `c.NotebookApp.server_extensions.append('ipyparallel.nbextension')` to `${HOME}/.jupyter/jupyter_notebook_config.py`
-   and run … or add those on command line:

``` {.bash}
  jupyter notebook --no-browser --NotebookApp.contents_manager_class='notedown.NotedownContentsManager'
  --NotebookApp.nbserver_extensions=='["pyparallel.nbextension"]'
```

-   create ipyparallel profile called "mpi":
-   make sure it defaults to MPI by adding (or inserting) the line to
-   also give the cluster the "training<sub>cluster0</sub>" name by inserting the line
    -   this has to be the same name as in the examples, otherwise connecting to the cluster will fail!
-   for non-desktop-class machines you also want or replace 2 with something else sensible: the default is number cores on the machine --- again failing to look at cpuset...
-   make sure environment variable points to where the course repo was cloned/copied into
-   start the cluster:
-   start jupyter with the repo root as the current working directory:
-   Devel environment needs

All the above (for teseting if not anything else)
-------------------------------------------------

ox-pandoc
---------

-   install from melpa.org/packages using emacs's package
-   ox-pandoc install MAY screw up org-mode (it did for me), fix with
-   you WILL NEED TO export your md files using
    -   it would be nice to know how to put this into a makefile!

pandoc
------

-   install using your favourite OS package manager

write in org-mode, export with org-pandoc-export-to-markdown<sub>github</sub>
-----------------------------------------------------------------------------

-   you need `ditaa` or
-   and you need to tell emacs to "compile" ditaa diagrams: `M-x
       customize-variable` and `org-babel-load-languages`, then add `ditaa` to the list
-   Release Procedure

1.  pull from juha's private PETSc to PETSc<sub>codes</sub> branch
2.  merge PETSc<sub>codes</sub> and trunk
3.  
4.  export all org files to md using org-pandoc-export-to-markdown<sub>github</sub>
5.  clean up the nested lists in the md files
6.  tangle the sources in every org file using org-babel-tangle
7.  push generated sources,md files, pngs etc to the release repo (or branch?)
8.  push remaining non-generated sources to the release repo (or branch?)
9.   the release

PROBLEMS
========

1.  pandoc export screws up lists within lists
2.  pandoc export does not generate a toc
