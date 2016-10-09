Contents
========

Lecture 1: Some Good Programming Practices
------------------------------------------

Lecture 2: Hands On 1
---------------------

Lecture 3: Python
-----------------

Lecture 4: Hands On 2
---------------------

Lectures 5-8: Cantab Guest Stars & Hands On with More Good Practices
--------------------------------------------------------------------

Lecture 9: On Algorithms and Optimisation
-----------------------------------------

Lecture 10: Hands On
--------------------

Lecture 11: Parallel Programming
--------------------------------

Lecture 12: Hands On
--------------------

Lecture 13: More Parallel Programming and Prototyping in Python
---------------------------------------------------------------

Lecture 14: Hands On
--------------------

Lecture 15: I/O and Visualisation
---------------------------------

Lecture 16: Hands On
--------------------

First we need to set up a working environment
=============================================

Log on to *beehive.maths.cam.ac.uk* using ssh: open a terminal and run
----------------------------------------------------------------------

`ssh CRSID@beehive.maths.cam.ac.uk` where `CRSID` is obviously your CRSID.

Once there clone the course git repo:
-------------------------------------

`git clone git://git.csx.cam.ac.uk/damtp-ipcc/HPC_course_student`

Go to the newly created directory
---------------------------------

`cd HPC_course_student`

Load the *ipyparallel* module for parallel computations
-------------------------------------------------------

`module load ipyparallel`

And start the *jupyter notebook*:
---------------------------------

``` {.bash}
  jupyter  notebook --no-browser --NotebookApp.nbserver_extensions='{"ipyparallel.nbextension":True}' \
  --NotebookApp.contents_manager_class='notedown.NotedownContentsManager'
```

Note down the port jupyter listens on and start ssh tunnel
----------------------------------------------------------

-   The port can be found from its output. Look for a line like

``` {.bash}
  [I 23:51:59.881 NotebookApp] The Jupyter Notebook is running at: http://localhost:8888/
```

-   Here the port number is `8888` (which is the default but only the first user will be able to use that).
-   Then start the ssh tunnel with

``` {.bash}
  ssh -N -L JUPYTERS_PORT:localhost:JUPYTERS_PORT CRSID@beehive.maths.cam.ac.uk
```

Now open a browser and surf to [http://localhost:JUPYTERS\_PORT/](http://localhost:JUPYTERS_PORT/)
