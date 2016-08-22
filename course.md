Intro
=====

HPC What it is and what is it good for?
---------------------------------------

-   traditionally two categories:
    -   capacity/throughput: problems can be solved without HPC but need to solve so MANY that HPC is necessary to give the capacity
    -   capability: cannot solve any other way
-   HPC involves a lot of software development
    -   very few fields can enjoy off-the-shelf programs
-   solving (and simulating, but that's just an equation to solve) very difficult and very large (sets of) equations
-   processing very large sets of data (larger than even most Big Data)

This course will
----------------

-   cover basic software development practices
-   guide you in creating efficient programs
    -   COSMOS IPCC can help
    -   MODAL program now 100\(\times\) faster than before
    -   another cosmology code more than 10\(\times\) faster (actually the original was so slow it never finished, which gives just a lower limit of 10×)
    -   Fixing file-writing routine in yet another two codes to get 20x and 5x speedups.
    -   not only saves researchers' time but also allows more science to be done with the same resource (supercomputer)
    -   Can save a lot of time with very little effort!
-   have a look at how to account for constraints imposed by the computer itself (unlike in normal desktop programming)
-   provide transferable skills: big data, software development, and programing skills are all sought after by industry as well as the obvious problem solving skills

Some unique things about HPC:
-----------------------------

-   rarely need to worry about memory consumption: distributed parallel processing allows access to more
-   very rapidly changing requirements and continuous development
    -   this resembles AGILE software development in companies
-   need to worry about the computer hardware
    -   embedded software development shares this need and is also concerned by the speed and efficiency
-   this course will build the basics of these transferable skills and apply them to large scale problems
    -   the assumption is that whatever you're doing is way too big for your laptop/desktop

Course Material
---------------

All the material is available on line as a git repository (which you will know how to use after the course if you don't already do): `git
clone git://git.csx.cam.ac.uk/damtp-ipcc/HPC_course_student`

Shell
=====

The Unix Command Line
---------------------

-   This course uses the unix command line *shell* a lot and it's the de-facto interface to high performance computers
-   We'll use \`ssh\` to access a shell on a remote supercomputer
-   You can choose you favourite shell, all our examples use *bash*
-   The next magic cell sets up the environment and directories etc in a directory `training/tmp` in your home directory. It will be totally wiped in the process: if you run this outside the training accounts of this course, please be careful.

``` {.bash}
  cd
  rm -rf ${HOME}/training/tmp
  mkdir -p ${HOME}/training/tmp
  cd ${HOME}/training/tmp
  for x in 0 1 2 3 4 5 6 7 8 9
  do
    touch examplefile$x
  done
  for x in 0 1 2 3
  do
    mkdir exampledirectory$x
  done
  touch exampledirectory1/examplefileA .hiddenexample1
  echo "Text in a file" > examplefile3
  echo DONE.
```

Shell, part 1: The First Commands
---------------------------------

### Listing files and directories

-   produce a simple, locale sorted list of files

``` {.bash}
  ls
```

-   list "hidden" files, too

``` {.bash}
  ls -a
```

-   give detailed information (we'll learn to interpret it later)

``` {.bash}
  ls -l
```

-   list only `examplefile1` and the contents of `exampledirectory1` directory

``` {.bash}
  ls -l examplefile1 exampledirectory1
```

-   a full usage help; works with almost all commands

``` {.bash}
  ls --help
```

-   When you need to operate on lots of files, use *glob patterns* like this

``` {.bash}
  echo example*
```

``` {.bash}
  echo examplefile[0-8]
```

-   Do yourself a favour and avoid "special" characters in filenames: TODO!!! `` ()[]{} &*$?\|#'"` ``
-   Yes, that is a space in there!
-   All of these work if you *escape* them correctly, but it is complicated:

``` {.bash}
  touch horriblen\ame1 horriblen\\ame2 horrible\\name3 horri\\blename4 horrible\ example5
```

-   and it gets even worse if you try to write a script and process this programmatically
-   besides `\` can give you nasty surprises:

``` {.bash}
  ls horr*
```

-   oops...

``` {.bash}
  rm horrible\name3 horrible example5
```

-   but only `/` is really forbidden in file names: you just cannot have it in a file name

### Making Directories

-   directory is just a special type file
    -   initially a directory is like an empty file
    -   creating one is equally simple

``` {.bash}
  mkdir exampledirectory10
```

-   there are other kinds of special files, too: *sockets*, *device nodes*, *symbolic links*, etc

### Changing to a different Directory

Go to directory called `exampledirectory1`

``` {.bash}
  cd exampledirectory1
```

-   and back to where you were

``` {.bash}
  cd ..
```

-   that `..` refers to the directory containing current directory
-   current directory is referred to with `.`
    -   hence `..` and `./..` are the same thing

Shell, part 2: Managing Directories and Files
---------------------------------------------

### the directory tree

-   image of dirtree TODO!!!
-   where are we in the tree?

``` {.bash}
  pwd
```

### Copying Files

-   copy `examplefile1` to `examplefile11`

``` {.bash}
  cp examplefile1 examplefile11
```

-   and `examplefile1` to `exampledirectory2/` with its original name

``` {.bash}
  cp examplefile1 exampledirectory2/
```

-   or with a new name

``` {.bash}
  cp examplefile1 exampledirectory2/newname
```

-   this is equivalent to move followed by copy or vice versa (but has different semantics)
-   a more sophisticated copying tool is called *rsync*

``` {.bash}
  rsync -a exampledirectory2/ exampledirectory12/
```

-   limitation: the above can only create one directory level, i.e. `rsync -a exampledirectory2/ exampledirectory12/exampledirectory13/` will fail

### Moving Files

-   just like copying

``` {.bash}
  mv examplefile11 exampledirectory3/
```

-   let's move it back to current directory but with a new name

``` {.bash}
  mv exampledirectory3/examplefile11 ./newname
```

-   remember, directories are files, so can `cp`, `rsync`, `mv` directories just as well as files
-   but be careful: `cp|mv|rsync directory dest` behaves differently depending on whether `dest` exists or not
-   be extra careful: all these commands overwrite destinations without warning

### Removing Files and directories

-   remove a file

``` {.bash}
  rm examplefile9
```

-   but directories cannot be removed unless they are empty

``` {.bash}
  rmdir exampledirectory1
```

-   so remove the contents first

``` {.bash}
  rm exampledirectory1/*
  rmdir exampledirectory1
```

-   there is a way to do this with one command, but people have removed all their files with it by accident...

Shell, part 3: Working with Files from the Command Line
-------------------------------------------------------

### Displaying the contents of a file on the screen

-   for small files

``` {.bash}
  cat examplefile3
```

-   but this is not useful for big files as they'll scroll off the screen, better one is `less examplefile3` or `more examplefile3` if `less` is unavailable

### Searching the contents of a file

-   find "This" from a `examplefile3`

``` {.bash}
  grep -E "This" examplefile3
```

-   or use a *regular expression* or *regex* to match any string with capital "T" followed after any number (including zero) characters by "s"

``` {.bash}
  grep -E "T.*s" examplefile3
```

-   or "T" followed ... by "x"

``` {.bash}
  grep -E "T.*x" examplefile3
```

-   `man grep` for more details on what a `regex` is

### STDIO and friends

-   It is often useful to capture the output of a program or send input programmatically to a program: redirection!
-   all programs have three non-seekable files open: standard input where user types in, standard output where program writes normal output, and standard error where program is supposed to write error messages
-   normally called *stdin*, *stdout* and *stderr*
-   redirect stdout with "\>"

``` {.bash}
  ls > examplefile12
```

-   no output: it went to `examplefile2`:

``` {.bash}
  cat examplefile12
```

-   can also redirect stdin to a file using redirection: this provides input to `grep example` from a file

``` {.bash}
  grep example < examplefile12
  grep directory < examplefile12
```

-   Can also combine these without going via files: *pipes*; note that the following only "pipes" stdout

``` {.bash}
  ls | grep example
```

-   A more complicated case with stderr ("2\>") redirected to `/dev/null` (a black hole):

``` {.bash}
  ls i_do_not_exist examplefile1 2> /dev/null | grep example
```

-   now errors go to where stdout goes ("&1" means "same as stdout")

``` {.bash}
  ls i_do_not_exist examplefile1 2>&1 | grep file
```

-   can also swap them around: now stderr is redirected to stdout (2\>&1) but stdout is then redirected to `/dev/null` ("1\>/dev/null"), so pipe ("|") only gets stderr now

``` {.bash}
  ls i_do_not_exist examplefile1 2>&1 1>/dev/null | grep file
```

-   order matters: this sends everything to `/dev/null`

``` {.bash}
  ls i_do_not_exist examplefile1 1>/dev/null 2>&1 | grep file
```

Shell, part 4: Permissions, Processes, and the Environment
----------------------------------------------------------

### Securing your files

-   Basic permissions are for *owner*, *group*, *other*.
-   `r` means read, `w` write, `x` execute (or "change into" for directories)

``` {.bash}
  ls -la
```

-   Careful! Prmissions on directory control new file creation and deletion, so can "steal" files! (Just demonstrating the sequence, the original file is already owned by the training user.)

``` {.bash}
  mv examplefile3 3elifelpmaxe
  cat 3elifelpmaxe > examplefile3
  rm 3elifelpmaxe
```

-   For shared directories, use `getfacl` and `setfacl` but they have limitations: only files originally created in the directory inherit the ACL, files moved there from elsewhere will need further action.
-   ACLs are the only practical way of setting up shared directories
-   Give group `users` read access and user `z300` read-write access to `exampledirectory3` and make sure subsequent files and directories created there have similar permissions:

``` {.bash}
  setfacl --default --modify u::rw exampledirectory3
  setfacl --default --modify g::r exampledirectory3
  setfacl --modify u:z300:rw exampledirectory3
  setfacl --modify g:users:r exampledirectory3
```

### Managing processes

-   list your own processes controlled by current (pseudo) terminal

``` {.bash}
  ps
```

-   or list all processes and threads

``` {.bash}
  ps -elfyL
```

-   or processes in a parent-child tree

``` {.bash}
  ps -eflyH
```

-   another way to print the tree; fancy, but not very useful compared to above

``` {.bash}
  pstree
```

-   two interactive views of processes, including their CPU utilisation

``` {.bash}
  top -b -n1
```

-   there is also `htop` on most modern machines
-   You can execute processes "in the background"

``` {.bash}
  sleep 7 &
  sleep 5 & kill -SIGSTOP $!
  sleep 3
  echo 'in a real terminal you could stop a process with C-z and then check what you have in the background (either running or stopped)'
  jobs -l
  echo 'transfer a process to background'
  bg 2
  echo 'check it'
  jobs -l
  echo 'and move one back to the foreground'
  fg 1
  echo 'normally you get rid of the foreground process with C-c but now we just waited'
```

-   Primitive communication between processes is done using *signals*

``` {.bash}
  jobs -l
  wait
  sleep 72 &
  sleep 36 &
  sleep 3 &
  echo 'Send SIGSTOP to the second one'
  kill -SIGSTOP %2
  echo 'Check what happened.'
  jobs -l
  echo 'Send SIGTERM to the first process'
  kill -SIGTERM %1
  echo 'Check'
  jobs -l
  echo 'Ok, so now it had terminated. Send SIGKILL to the second process'
  kill -SIGKILL %2
  echo 'Check'
  echo 'Wait for %3 to finish'
  jobs -l
  wait
```

-   the notorius segmentation fault or segmentation violation or segfault for short causes the kernel to send the `SIGSEGV` signal to the offending process
-   some batch job systems on supercomputers will send `SIGUSR1`, `SIGUSR2`, `SIGXCPU` or `SIGTERM` when your job is about to run out of its allocated time slot
-   COSMOS will send `SIGTERM` first, followed by `SIGKILL` if you don't quit peacefully

### Shell startup and environment

-   When you log in, `bash` will execute several *script* files; basically lists of commands
    -   system startup files
    -   personal ones in `~/.bash_profile` (login sessions) or `~/.bashrc` (other sessions)
    -   edit as you see fit, but be careful: mistakes can lead to inability to log in!
-   *Environment variables* control how `bash` behaves; most important ones are

    `PATH`  
    list of colon-separated directory names to look, in order, for commands typed in the prompt

    `HOME`  
    your home directory, also available as --- under certain conditions

-   Useful UNIX commands
    -   check the value of a variable PATH

``` {.bash}
  echo ${PATH}
```

-   check where (in `PATH`) command `ls` lives

``` {.bash}
  which ls
```

-   easiest way to give a long list of parameters to a program

``` {.bash}
  find exampledirectory12 -name 'example*1' -print0 |xargs -0 ls -l
```

Examples / Practicals / Exercises (these go to cookbook, too)
-------------------------------------------------------------

-   Remove file called `foo bar`.
-   Remove file called `-rf`.
-   Remove file called `nasty $SHELL`,
-   Remove LaTeX compilation by-products (i.e. files ending in `.log` and `.aux`) in a directory hierarchy which is 10 levels deep (hint: `find`).
-   List all executable files in the current directory, including "hidden" ones.
-   List of directories in the current directory.
-   Write a shell script which outputs "`filename` is older" if `filename` is older than your `~/.bashrc` and "`filename` is newer" it it is not older.
-   Create yourself an ssh private-public-keypair and set up key based authentication with your training account on `microcosm.damtp.cam.ac.uk`.
-   You should pick one and learn the tricks of at least one text-editor to make your life easier on the terminal. This course does not cover that but popular choices are `emacs` and `vim`; emacs has a good built-in tutorial which you can easily access the first time you start it.

### Further resources

*here for example*

The Compiler
------------

-   what is it
-   why need one
-   examples, with last one taking forever to compile because the file is so big (but no -ipo as that will take long even with modular code): how to sort that out
-   Good Programming Practices and basic tools

Git
---

### Preliminary steps

-   Edit - set up your name and email address

``` {.bash}
  git config --global user.email "smith@univerisity"
  git config --global user.name "John Smith"
  git config --global core.edior "/usr/bin/vim"
```

-   uses environment variable and if that is not set

### Work on commits

#### Start from scratch: 

``` {.bash}
  # Copy pristine snapshot
  rm -rf MyRepo MyRepo2
  mkdir MyRepo
  cp -r MyRepo.orig/program{.c,} MyRepo
  cd MyRepo
  git init
```

#### Add first files

``` {.bash}
  git add program.c
```

#### Check what we are going to commit 

``` {.bash}
  git status
```

-   Working Directory
-   Stagin area - place to prepare commits

#### Ignore unwanted files

``` {.bash}
  echo program > .gitignore
  echo '*.o' >> .gitignore
  git add .gitignore
  git status
```

#### Actual commit

``` {.bash}
  git commit -m 'Initial commit'
```

-   good commit messages

#### Check the last commit

``` {.bash}
  git show
```

#### Shortcuts

-    - all changed files (deletion is considered a change!)
-   

``` {.bash}
  cp ../MyRepo.orig/program.c.2 program.c
  git commit -m 'Second commit' program.c
```

#### Check the history of the current commit

``` {.bash}
  git log
```

Including changes

``` {.bash}
  git log -p
```

#### Fixing commits

``` {.bash}
  cp ../MyRepo.orig/program.c.3 program.c
  git commit -m 'Fixed second commit' -a --amend
```

``` {.bash}
  git log -p
```

#### Compare two commits

``` {.bash}
  git diff HEAD~1 HEAD
```

#### Changes between commit and working tree

``` {.bash}
  cp ../MyRepo.orig/program.c.4 program.c
  git diff HEAD~
```

#### Changes between working tree and staging area

``` {.bash}
  git diff
```

``` {.bash}
  git add program.c
  git diff
```

#### Changes between staging area and HEAD

``` {.bash}
  git diff --cached
```

#### Simple gui

-   

### Branches

#### See available branches

``` {.bash}
  git branch
```

#### Create new branch

``` {.bash}
  git checkout -b MyBranch
```

#### <span id="merge"></span>Merge another commit to the branch

-   
-   trivial merge (fast-forward): if the current commit is an ancestor of the merged one the note denoting branch is moved and no new commit is created
-   "proper" merge - new commit is created with two parents
-   conflicts happen and need to be resolved before conflicting file can be committed again

``` {.bash}
  git commit -m "Define MAXLEN on branch" -a
```

``` {.bash}
  git checkout master
  cp ../MyRepo.orig/program.c.5 program.c
  git commit -m "Define MAXLEN on master" -a
```

``` {.bash}
  git merge MyBranch
  cat program.c
  cp ../MyRepo.orig/program.c.5 program.c
  git add program.c
  git commit -m 'Merge commit'
```

-   If you want to stop the merging procedure:

### Collaboration with others

#### Clone repository

``` {.bash}
  cd ..
  rm -rf MyRepo
  git clone ServerRepo MyRepo2
```

#### Remote branches

-   remotes/\<name\>/... - by default \<name\> is : the state of the remote repository as it was last seen

``` {.bash}
  git branch -a
```

#### Update remote branches

-   
-    --- remove all remote-tracking references

#### Push your changes

-   
-   Sometimes push failes because someone else updated the branch in the meantime. You need then to fetch the changes, merge them and try to push again.
    -   however
        -   
        -   
    -   will produce merge with the "wrong" order of parents. To prevent it after fetch:
        -   
        -   
-   python

Please read the official [python tutorial](https://docs.python.org/2/tutorial/) (also have a look at [version 3 tutorial](https://docs.python.org/3/tutorial/index.html) to see how things will change in the future) to make sure your python is up to speed. In particular, you will should understand the basic syntax, modules, meaning of whitespece, how to use utf-8 encoding, how to deal with ' and " and linefeeds in strings.

Other useful features are operator overloading: `2*3+1==7`, but

``` {.python}
  'little bunny'+2*' foo'=='little bunny foo foo'
```

Slicing of arrays and strings
-----------------------------

This will be used heavily, so a few interactive examples TODO!!! some more array slicing examples and non-symmetric shapes and so forth. Check z301's notebook for details!

``` {.python}
  x="string"
  x
```

``` {.python}
  x[0]
```

``` {.python}
  x[-1]
```

``` {.python}
  x[2:-2]
```

numpy has some extra slicing features
-------------------------------------

First, let's see what a numpy array looks like: this is a 2x3x4 array.

``` {.python}
  import numpy
  skewed = numpy.random.random((2,3,4))
  skewed
```

We will use `array` in our examples later, we will initially create it as follows

``` {.python}
  array = numpy.arange(0,27)
  array
```

but now we give it a new shape

``` {.python}
  array=array.reshape(3,3,3)
  array
```

-   this is a slice

``` {.python}
  array[-1,:,1:]
```

-   and striding is also possible, and combining the two:

``` {.python}
  array[::2,:,2:0:-1]
```

-   numpy arrays have point-wise operator overloads:

``` {.python}
  array + array
```

``` {.python}
  array * array
```

-   nearly any imaginable mathematical function can operate on an array element-wise:

``` {.python}
  array ** 0.5
```

``` {.python}
  numpy.sinh(array)
```

-   but numpy matrices are bona fide matrices:

``` {.python}
  matrix=numpy.matrix(array[0,:,:])
  matrix*matrix
```

-   numpy matrices have all the basic operations defined, but not necessarily with good performance
-   for prototyping they're fine
-   **performance can be exceptional if numpy compiled suitably**
-   if you import `scipy` you have even more functions

``` {.python}
  import scipy
  import scipy.special
  scipy.special.kn(2,array)
```

-   I should say that

``` {.python}
  import scipy.fftpack
  scipy.fftpack.fftn(array)
```

-   performance of the FFT routines also depends on how everytihng was compiled
-   and theoretical physicists may find it amusing that numpy can do Einstein summation (and more)

``` {.python}
  numpy.einsum("iii", array)
```

``` {.python}
  numpy.einsum("ij,jk", array[0,:,:], array[1,:,:])
```

``` {.python}
  numpy.einsum("ijk,ljm", array, array)
```

Control flow statements
-----------------------

``` {.python}
  if (1>0):
    print("1 is indeed greater than 0")
  elif (1==0):
    print("Somehow 1 is equal to 0 now")
  else:
    print("Weird, 1 is somehow less than 0!")
```

``` {.python}
  for i in [0,1,2,3]:
    print(str(i))
  for i in range(4):
    print(str(i))
  for i in xrange(4):
    print(str(i))
```

``` {.python}
  for i in range(0,4): print(str(i))
```

``` {.python}
  print [i for i in range(0,4)]
  print [str(i) for i in range(0,4)]
  for i in range(4): print str(i)+","
  print ','.join([str(i) for i in range(0,4)])
```

-   there are others, but we won't use them

Section 5 of the tutorial is a must read
----------------------------------------

Section 9 describes python's classes and is a must, too
-------------------------------------------------------

But we will use classes as containers only, nothing fancy. TODO!!! decorators

CANTAB

Profiling
=========

-   You've got a well designed, parallel, scalable code, but it still takes way too long to run.
-   Please do use good programming practices as those will make optimising (and profiling) a lot easier

Profiling Your Code
-------------------

### First Look: Function Level Overview

-   Always find your "hot spots" before starting to optimise
    -   The hot spot is often not where you think it is
-   In Python, there is a built-in tool `cProfile` we can use
    -   For C/Fortran you can use TODO!!! URLS!!! HPCToolkit, TAU, or if you have Intel compatible hardware, Intel VTune
-   Example code initialises the data, computes the Laplacian, takes a Fourier Transform, adds a little to each variable, transforms back, and writes to disc

``` {.python}
  import numpy
  import scipy
  import scipy.fftpack 
  import cProfile
  import time as timemod

  def Init(sizes):
      return 

  def Laplacian(data, lapl, d):
      for ii in range(1,data.shape[0]-1):
          for jj in range(1,data.shape[1]-1):
              for kk in range(1,data.shape[2]-1):
                  lapl[ii,jj,kk] = (
                      (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])/(d[0]*d[0]) +
                      (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])/(d[1]*d[1]) +
                      (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])/(d[2]*d[2]))
      return

  def Init(size):
      d=numpy.array([0.1,0.1,0.1])
      data=numpy.random.random([size]*3)
      lapl=numpy.zeros_like(data)
      return {"data": data, "laplacian": lapl, "lattice_spacing": d}

  def Fourier(data):
      return scipy.fftpack.fftn(data)

  def AddLittle(data):
      for ii in range(0,data.shape[0]):
          for jj in range(0,data.shape[1]):
              for kk in range(0,data.shape[2]):
                  data[ii,jj,kk] = data[ii,jj,kk] + 1./numpy.pi
      return

  def IFourier(data):
      return scipy.fftpack.ifftn(data)

  def WriteToFile(data):
      data.tofile("ihopethisfiledoesnotexist.dat", sep=" ")
      return

  def RunProfile(size):
      variables = Init(size)
      Laplacian(variables["data"], variables["laplacian"], variables["lattice_spacing"])
      fftdata=Fourier(variables["data"])
      AddLittle(fftdata) # pass-by-reference, so OUR fftdata WILL CHANGE
      finaldata=IFourier(fftdata)
      WriteToFile(finaldata)

  SIZE=100
  cp=cProfile.Profile()
  start = timemod.clock()
  cp.runcall(RunProfile, SIZE)
  end = timemod.clock()
  print("cProfile gave total time of {time} s and the following profile.".format(time=end-start))
  cp.print_stats(sort="time")
```

-   that was a bit long, wasn't it?
    -   that code is intentionally *BAD*
    -   unfortunately we need it to be bad to see effects of our optimisation later on!
-   TODO!!! Laplacian, but err... compute intensify it?

### Second Look: Line Level Profile

-   So, `Laplacian` is our most time-consuming part of the code: how do we optimise it?
    -   the first step in this case will be easy but it will get harder as we proceed and
-   for larger routines you would like to have a line-by-line profile
    -   this is easy to do with C, C++ and Fortran: all the tools mentioned above can give a line-by-line profile
    -   not so for python: there is [line<sub>profiler</sub>](https://github.com/rkern/line_profiler) or [pprofile](https://github.com/vpelletier/pprofile) and a slightly different approach: [pyvmmonitor](http://www.pyvmmonitor.com/)
    -   some large routines can and perhaps should be split into smaller ones, thus removing the need to profile line-by-line

### Third Look: Hardware Utilisation

-   Digging even deeper, one may want to know why a particular code provides so few operations / second compared to what google says the CPU can do
-   Let's look what kind of performance our `Laplacian` achieves

``` {.python}
  import pstats
  p=pstats.Stats(cp)
  Ltime=[p.stats[x] for x in p.stats if x[2]=="Laplacian"][0][2]
  LGF=(SIZE-2)**3*15
  print("Laplacian executed in {time} at {GFps} GF/s".format(time=Ltime, GFps=LGF/Ltime/1e9))
```

-   One should also consider other hardware utilisation issues, like memory bandwidth and latency
    -   We'll have a look at some of those next

### Note

The profiler modules are designed to provide an execution profile for a given program, not for benchmarking purposes (for that, there is timeit for reasonably accurate results). This particularly applies to benchmarking Python code against C code: the profilers introduce overhead for Python code, but not for C-level functions, and so the C code would seem faster than any Python one.

Optimisation
============

What is good and what is bad
----------------------------

-   no good metric:
    -   a very optimised implementation of a bad algorithm may still be more time consuming than an unoptimised implementation of a good algorithm
    -   what to measure: GF/s, % peak, cache misses, ...?
-   still to some extent useful to measure e.g. %peak
    -   if near theoretical peak, no point in trying to optimise more
    -   anything over 20% peak in a kernel is good
    -   measuring GF/s can compare different implementations of the same algorithm (or your progress in optimising it)
        -   **pitfall**: GF can change with optimisations and especially with compiled languages you might not even know
-   eventually we are interested in the runtime, so that's a good measure of progress

Language Differences
--------------------

-   one often hears arguments about language A being faster than language B
    -   rubbish
    -   language A may be better suited than others for achieving good in problem X but there's no overall winner
-   another often repeated claim is interpreted languages are slow
    -   rubbish again
    -   well written python is actually quite optimal and not to be shied away from!
    -   python WILL CACHE intermediate results
        -   performance can fluctuate wildly if doing repetitive tasks, like gathering performance statistics
        -   performance analysis is hard as repeating the same computation will use the cache and doing just one iteration has natural variation and overheads
        -   can be alleviated by using relatively big problems
        -   can eat more memory than you think (but won't run out)
    -   main issue with python is *it cannot do OpenMP*
        -   but it has its own tools: *multiprocessing* and *handythread*, which works almost as
        -   python combined with *cython* can automatically generate (hopefully) fast C/C++ extensions which can then use OpenMP
        -   we'll have a look at cython later
    -   other solutions for python include
        -   `scipy.weave` which is a JIT solution and no (easy) way to pre-compile and save the module, but generates very fast code
        -   `pypy` is another JIT solution which is very actively maintained

Some Hardware Considerations
----------------------------

-   I/O will kill performance, avoid as much as you can
    -   7200 rpm is not that much if you need to read/write a million times
        -   expectation value of 1/14400 min latency every time you access the disc
        -   a million writes
        -   that's about an hour! Of just waiting!
    -   Regardless of how much you actually read/write. If you do it in one go, you'll get away with one wait.
    -   OS filesystem and hard disc caches alleviate this, but cannot completely hide the effect and
        -   for reads they are **almost completely powerless** to help you!
    -   SSD is much better than HDD but the effect is still there
    -   interleave I/O with other tasks if you can
    -   printing to standard output is also very slow, so avoid excessive printing
-   Interconnect Latency
    -   affects a NUMA machine like COSMOS as well as distributed memory machines (clusters)
-   Interconnect Bandwidth
    -   easier to measure, and deal with than latency
    -   at least an order of magnitude slower than memory, so avoid
-   Memory subsystem performance
    -   NUMA causes issues even on single socket these days
    -   CPU's memory controller always operates on a *page* of memory
        -   sizes vary between 4kB, 2MB, 1GB
    -   78.6 GB/s (Broadwell) vs 915.2 GF/s gives 95 F/double!!!
    -   latency is an even bigger bugbear and much harder to measure/control
    -   caches help overcome both
        -   but introduce a degree of unpredictability
    -   cache is multi-level, only last level can keep up with core; prefetching
    -   set-associative
        -   M addresses map to the same set
        -   2<sup>N</sup> -way set associative cache N of M (\>\>2<sup>N</sup>) addresses in cache
        -   cache collision happens when CPU needs to cache \>2<sup>N</sup> addresses mapping to the same set
        -   cache collisions explain many unexpected performance decreases, especially when one has a an array with a dimension equal to some power of two
        -   typical value of N \< 10
    -   see [this](https://en.wikipedia.org/wiki/CPU_cache) for good read on caches
-   other on-core issues that have to do with parallelism
    -   *false sharing* affects many unsuspecting OpenMP parallelisations
        -   TODO!!! Try to demonstrate with a small code
    -   page ownership can also surprise in a NUMA machine if owner is not where expected
        -   very hard to control and hardware dependent, but usually **last writer** to a page owns it
        -   but determining what belongs to which page is difficult (except for big malloc()ed arrays)
-   in-core
    -   how to load a cache line
    -   branch misprediction
        -   [here](http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array) is an example
        -   function calls are effectively branch misses
    -   pipeline stall
    -   pipeline flush

First Shot at Optimising the Laplacian
--------------------------------------

-   Recall the triple for-loop in the Laplacian above? It was the hot spot.
-   We'll forget about the other bits for now (we could not optimise the FFTs anyway)

``` {.python}
  def Laplacian2(data, lapl, d):
      lapl = (
          (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/(d[0]*d[0]) +
          (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/(d[1]*d[1]) +
          (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/(d[2]*d[2]))
      return

  LGF=(SIZE-2)**3*15

  def RunOne(prof, func, *args):
      prof.runcall(func, *args)

  def GetLtime(prof):
      p=pstats.Stats(prof)
      Ltime=[p.stats[x] for x in p.stats if x[2].startswith("Laplacian")][0][2]
      return Ltime

  def RunSome(funcs):
      variables = Init(SIZE)
      cp={}
      times={}
      for function in funcs:
          cp[function]=cProfile.Profile()
          RunOne(cp[function], eval(function), variables["data"], variables["laplacian"], variables["lattice_spacing"])
          times[function] = GetLtime(cp[function])
          print("{func} executed in {time} at {GFps} GF/s".format(func=function, time=Ltime, GFps=LGF/Ltime/1e9))
      print("Speedup between {f0} and {fN}: {slowfast}".format(slowfast=times[funcs[0]]/times[funcs[-1]],
                                                               f0=funcs[0], fN=funcs[-1]))
      if (len(times)>1):
          print("Speedup between {fNm1} and {fN}: {slowfast}".format(slowfast=times[funcs[-2]]/times[funcs[-1]],
                                                               fNm1=funcs[-2], fN=funcs[-1]))
      return (cp,times)

  results = RunSome(["Laplacian", "Laplacian2"])
```

-   **Rule \#1**: never use a `for` loop to operate on a numpy array

Node level optimisation: Use the Cores: multi- and manycore architectures
-------------------------------------------------------------------------

-   Python has something called *Global Interpreter Lock* (GIL) which makes threads almost useless for compute intensive tasks in python without relatively complicated tricks
    -   careful use of numpy arrays can avoid this
-   "Standard" way to use the cores in C/C++ is OpenMP
    -   these have no GIL, of course
    -   in this context OpenMP does nothing but multithread the code: sometimes better to do that manually
        -   e.g. when you need to call an OpenMP-parallelised library
            -   this "nesting" of OpenMP is supported but does limit your options
    -   cython can do that in python, too and we'll soon see how

TODO!!! I'm here C+Python = Cython: an optimised RHS
----------------------------------------------------

``` {.python}
  import numpy
  import cProfile
  import time as timemod

  def init_data(sizes):
      return numpy.random.random(sizes)

  def Laplacian(data, lapl, d):
      lapl = (
          (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/d[0]*d[1]*d[2] +
          (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/d[1]*d[0]*d[2] +
          (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/d[2]*d[0]*d[1])
      return

  def runone(func):
      d=numpy.array([0.1,0.1,0.1])
      data=init_data((400,400,400))
      lapl=numpy.zeros_like(data)
      cp=cProfile.Profile()
      start = timemod.clock()
      cp.runcall(func, data, lapl, d)
      end = timemod.clock()
      print("cProfile gave total time of {time} s and the following profile.".format(time=end-start))
      cp.print_stats()

  L=runone(Laplacian)
```

-   do not even try to do this in python without numpy: your runtime will go through the roof, oceans will dry, Sun will become a red giant, and quite probably the Universe suffer a heat death before your code returns (an over 100x speedup would not be unexpected)
-   but even with numpy this leaves room for improvement:
    -   it is still python with all the overhead an interpreted language implies
    -   it uses a single core only
    -   N.B. numpy's and scipy's BLAS and LAPACK routines (numpy.linalg, scipy.linalg) and possibly some others will use an external library to do the maths: if this library uses many cores, you get the benefit for free
-   an improved version using *cython*
    -   N.B. only ipython and jupyter can run this: normal python cannot
    -   we will deal with plain python later
-   a look at the code
    -   everything from `%%cython` to the next empty line will be saved to a tepmorary file, turned into a C code using cython and then compiled into a python module which is then imported
    -   when cython runs, it does not see our current namespace (it is a separate process), so we need to import whatever we use
    -   there is also a special `cimport` command, which imports "into C code"
    -   the `@cython` lines are *decorators* which affect how cython treats the following function: we want no bounds checking on our arrays and we want \(1/0\) to produce \(\infty\) instead of python's `ZeroDivisionError`
    -   this is more or less standard cython preamble
    -   notice also the type definitions in the function definition: **always** type **everything** in cython as if you do not, cython treats them as pytohn objects with all the performance penalty that implies
-   we'll also introduce the right datatypes: the `double` we used above just happens to be the same as an element of the `numpy.ndarray` we passed Laplacian

``` {.python}
  %load_ext Cython
  %%cython
  import cython,numpy
  cimport numpy
  @cython.boundscheck(False)
  @cython.cdivision(True)
  def cyLaplacian(object[double, ndim=3] data, object[double, ndim=3] lapl, object[double, ndim=1] d):
      lapl = (
          (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/d[0]*d[1]*d[2] +
          (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/d[1]*d[0]*d[2] +
          (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/d[2]*d[0]*d[1])
      return

  L=runone(cyLaplacian)
```

-   that was not an impressive result: the `double` we used above just happens to be the same as an element of the `numpy.ndarray` we passed Laplacian: perhaps that was the cause? Let us define them more correctly.

``` {.python}
  %load_ext Cython
  %%cython
  import cython,numpy
  cimport numpy
  DTYPE=numpy.float64
  ctypedef numpy.float64_t DTYPE_t
  @cython.boundscheck(False)
  @cython.cdivision(True)
  def cyLaplacian2(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d):
      lapl[1:-1,1:-1,1:-1] = (
          (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/d[0]*d[1]*d[2] +
          (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/d[1]*d[0]*d[2] +
          (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/d[2]*d[0]*d[1])
      return

  L=runone(cyLaplacian2)
```

-   that was not an impressive result: unfortunately as much as numpy likes array-operations, cython dislikes them
-   next we go back to explicit loops

``` {.python}
  %load_ext Cython
  %%cython
  import cython,numpy
  cimport numpy
  @cython.boundscheck(False)
  @cython.cdivision(True)
  def cyLaplacian3(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d):
      cdef int xmax = data.shape[0]
      cdef int ymax = data.shape[1]
      cdef int zmax = data.shape[2]
      cdef int ii, jj, kk
      for ii in range(1,xmax-1):
          for jj in range(1,ymax-1):
              for kk in range(1,zmax-1):
                  lapl[ii,jj,kk] = (
                      (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])/d[0]*d[1]*d[2] +
                      (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])/d[1]*d[0]*d[2] +
                      (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])/d[2]*d[0]*d[1])
      return

  L=runone(cyLaplacian3)
```

-   that's more like it, but can we do more? Without touching the code, not much, but we can see if the compiler can do better!
-   cython can be told to pass flags to the compiler as follows

``` {.python}
  %%cython --compile-args=-Ofast --compile-args=-march=ivybridge --compile-args=-fno-tree-loop-vectorize --compile-args=-fno-tree-slp-vectorize --compile-args=-fno-ipa-cp-clone --compile-args=-fno-unsafe-math-optimizations
  import cython,numpy
  cimport numpy
  DTYPE=numpy.float64
  ctypedef numpy.float64_t DTYPE_t
  @cython.boundscheck(False)
  @cython.cdivision(True)
  def cyLaplacian4(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d):
      cdef int xmax = data.shape[0]
      cdef int ymax = data.shape[1]
      cdef int zmax = data.shape[2]
      cdef int ii, jj, kk
      for ii in range(1,xmax-1):
          for jj in range(1,ymax-1):
              for kk in range(1,zmax-1):
                  lapl[ii,jj,kk] = (
                      (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])/d[0]*d[1]*d[2] +
                      (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])/d[1]*d[0]*d[2] +
                      (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])/d[2]*d[0]*d[1])
      return

  L=runone(cyLaplacian4)
```

-   the final code modification we do is to reduce the number of operations per loop iteration: the lattice constant products can be precomputed
    -   compiler will detect some such cases and move them out of the loop but it fails here

``` {.python}
  %%cython --compile-args=-Ofast --compile-args=-march=ivybridge --compile-args=-fno-tree-loop-vectorize --compile-args=-fno-tree-slp-vectorize --compile-args=-fno-ipa-cp-clone --compile-args=-fno-unsafe-math-optimizations
  import cython,numpy
  cimport numpy
  DTYPE=numpy.float64
  ctypedef numpy.float64_t DTYPE_t
  @cython.boundscheck(False)
  @cython.cdivision(True)
  def cyLaplacian5(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d):
      cdef int xmax = data.shape[0]
      cdef int ymax = data.shape[1]
      cdef int zmax = data.shape[2]
      cdef int ii, jj, kk
      cdef double d1d2bd0=1.0/d[0]*d[1]*d[2], d0d2bd1=1.0/d[1]*d[0]*d[2], d0d1bd2=1.0/d[2]*d[0]*d[1]
      for ii in range(1,xmax-1):
          for jj in range(1,ymax-1):
              for kk in range(1,zmax-1):
                  lapl[ii,jj,kk] = (
                      (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])*d1d2bd0 +
                      (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])*d0d2bd1 +
                      (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])*d0d1bd2)
      return

  L=runone(cyLaplacian5)
```

-   python's integers gracefully overflow, C integers wrap around: we get an even bigger speedup by telling cython to conform to the C style, not python: `@cython.wraparound(False)`

``` {.python}
  %%cython --compile-args=-Ofast --compile-args=-march=ivybridge --compile-args=-fno-tree-loop-vectorize --compile-args=-fno-tree-slp-vectorize --compile-args=-fno-ipa-cp-clone --compile-args=-fno-unsafe-math-optimizations
  import cython,numpy
  cimport numpy
  DTYPE=numpy.float64
  ctypedef numpy.float64_t DTYPE_t
  @cython.boundscheck(False)
  @cython.cdivision(True)
  @cython.wraparound(False)
  def cyLaplacian6(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d):
      cdef int xmax = data.shape[0]
      cdef int ymax = data.shape[1]
      cdef int zmax = data.shape[2]
      cdef int ii, jj, kk
      cdef double d1d2bd0=1.0/d[0]*d[1]*d[2], d0d2bd1=1.0/d[1]*d[0]*d[2], d0d1bd2=1.0/d[2]*d[0]*d[1]
      for ii in range(1,xmax-1):
          for jj in range(1,ymax-1):
              for kk in range(1,zmax-1):
                  lapl[ii,jj,kk] = (
                      (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])*d1d2bd0 +
                      (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])*d0d2bd1 +
                      (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])*d0d1bd2)
      return

  L=runone(cyLaplacian6)
```

-   the timings on my laptop

|function|best time (s)|
|--------|-------------|
|Laplacian|4.184|
|cyLaplacian|4.200|
|cyLaplacian2|4.364|
|cyLaplacian3|0.852|
|cyLaplacian4|0.845|
|cyLaplacian5|0.312|
|cyLaplacian6|0.240|
|cyLaplacian6openmp|0.309|

-   but that's just one core: bring in the others (the last line in the table)
    -   note that my timing includes thread creation overheads!

``` {.python}
  %%cython --compile-args=-Ofast --compile-args=-march=ivybridge --compile-args=-fno-tree-loop-vectorize --compile-args=-fno-tree-slp-vectorize --compile-args=-fno-ipa-cp-clone --compile-args=-funsafe-math-optimizations --compile-args=-fopenmp --link-args=-fopenmp
  import cython,numpy
  from cython.parallel import prange, parallel
  cimport numpy
  DTYPE=numpy.float64
  ctypedef numpy.float64_t DTYPE_t
  @cython.boundscheck(False)
  @cython.cdivision(True)
  @cython.wraparound(False)
  def cyLaplacian6openmp(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d):
      cdef int xmax = data.shape[0]
      cdef int ymax = data.shape[1]
      cdef int zmax = data.shape[2]
      cdef int ii, jj, kk
      cdef double d1d2bd0=1.0/d[0]*d[1]*d[2], d0d2bd1=1.0/d[1]*d[0]*d[2], d0d1bd2=1.0/d[2]*d[0]*d[1]
      with nogil, parallel(num_threads=2):
      for ii in prange(1,xmax-1, schedule="static"):
          for jj in range(1,ymax-1):
                    for kk in range(1,zmax-1):
                      lapl[ii,jj,kk] = (
                          (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])*d1d2bd0 +
                          (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])*d0d2bd1 +
                          (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])*d0d1bd2)
                  return

  runone(cyLaplacian6openmp)
```

### our RHS

-   Jacobian, too; remember the FD checks!

OpenMP/TBB
----------

Vector Unit and GPU: SIMD/MIMD
------------------------------

Choosing an Algorithm
=====================

Think Parallel
--------------

-   You wouldn't be on this course if you were dealing with tiny problems
-   Parallelism is *nested*: you should try to exploit all levels
-   Large problems take too long without parallel processing (numbers based on a 3.5 GHz Pentium F core from late 2004 and 22-core Broadwell-EP E5v4 at 2.2 GHz; Xeon Phi numbers are guesses for Knights Landing)
    -   The Time of the Serial is over: no serial performance increase worth mentioning since 2005!
        -   In fact highest performing parallel processors' serial performance is only 40% of the 2005 level
    -   Parallel performance increase over serial performance **per core** (and per Hz) since 2005: **32x**!
    -   Even if you can wait at least 32 times longer, others won't and will scoop your result
    -   This performance provided by *SIMD* vector processing unit(s)
        -   GPU and FPGA co-processors offer similar functionality but are outside the scope of this course
-   Second level of parallelism, *multicore* and *manycore*
    -   Gives another **10x** or so over 2005 performance
        -   Xeon Phi gives **30x**
    -   SIMD and multicore together give 200x (\(\ne\) 320x!) and Xeon Phi even 1000x!
-   This performance does not come for free
    -   Efficient use of SIMD needs careful programming
    -   Efficient many-/multicore somewhat easier, but
    -   Do not worry about it yet --- much can be gained from choosing a good library
    -   But do plan for it from the beginning:
-   Parallel processing should be part of program design
    -   You should choose a parallelisable algorithm
        -   Example: mergesort is easy to parallelise, heapsort is very inefficient in parallel
    -   It must be implemented such that it can exploit SIMD and many cores

Think Distributed --- Parallel Taken to the Extreme
---------------------------------------------------

### "The Third Level" of parallelism

-   Lash several, even millions, of machines (*nodes*) together using an *interconnect* to work together on the same problem
-   Distribute problem data across nodes, each node working on its part of the problem
    -   Embarrassingly parallel: nodes work on different problems (possibly same equation with different parameters)
        -   MapReduce/Hadoop
-   The 32x and 1000x above can "now" become much bigger, even 8 000 000x

Decrease time-to-solution: *strong scaling*
-------------------------------------------

-   assume an **ideal** world
-   now the inter-node communication becomes a bottle-neck: theoretical limit

<span class="label">Strong Scaling in an Ideal World</span>
``` {#fig:domain_decomp_strong_scaling .python}

```

![](images/domain_decomp_scaling.png)

-   **conclusion**: even in an ideal world strong scaling eventually gives no benefit
    -   related to Amdahl's Law which we will meet soon
-   often load balancing becomes an issue well before the natural limit hits you

Increase problem size past single node: *weak scaling*
------------------------------------------------------

-   No more universal limit, in principle just add nodes to get bigger problem sizes
-   **algorithm** limits the scaling now
    -   Notoriously bad: Fast Fourier Transform
        -   Needs to transmit **volume**: in strong scaling surface was enough to kill scaling...
        -   TODO!!! Fast Multipole Method can often help here
-   Load balancing is often problem here, too
    -   Most n-body codes suffer from this as even initially well balanced bodies tend to cluster and wreck the balance
    -   Task-based parallelism helps here, but often suffers from poor data locality: ways around that are complicated but exist
-   Choice of a good algorithm again very, very important

Ensure scalability first
------------------------

-   As a rule of thumb, think what happens if your problem becomes 1000000 times larger
-   It's the hardest to deal with afterwards
-   Write smart, well designed code, optmimise on-core performance later
    -   But expect it will change its scaling characteristics (c.f. <fig:domain_decomp_strong_scaling> --- the initial ratio will change)
-   So, for now, we'll write distributed parallel code and worry about on-node and in-core performance later
-   Fortunately, a good choice of scientific library will deal with most distributed computing issues
    -   On this course, we will use *PETSc* but there are others, like TODO!!!

Cookbook: TODO!!! example algorithms (though no code yet)
---------------------------------------------------------

Message Passing Interface
=========================

You will be able to run all these on your DAMTP desktop, too. You need to

1.  `module load ipyparallel`
2.  `ipcluster start -n 2 --engine=MPI --profile=mpi --cluster-id=training_cluster_0` [1]
3.  `python -m bash_kernel.install` (only if you want bash kernel as well as ipython)
4.  `jupiter notebook` --- this will also open the jupyter notebook in the default browser. Add `--no-browser` if you don't like that.

Parallel Processing
-------------------

-   processing, not necessarily computing, as the example will show

### Painting a heptagonal wall

Suppose we had a heptagonal wall. We want to paint seven vertical stripes on each side: red, orange, yellow, green, blue, indigo, and violet stripe. Furthermore, the order of the stripes must be the same on each section of the wall --- it would not look like a rainbow otherwise.

Our painting company is located on a loose union of seven independent island states in the middle of the ocean and since we need to keep all seven governments happy, we paint one side on each island, and ship them to the customer separately. How do we do this? The *parallel algorithm* is simple:

1.  Send instructions to each island. The instructions state the order of the colours and instructions to send pots of paint to (and receive from) the other islands in a particular fashion as described later. Every painter is assigned a colour to start with (and consequently also where along the horizontal length of the wall to paint that: recall that the colours must be in the order of the spectrum)
2.  Every painter on every island goes on to a paint shop to buy a pot of paint of their assigned colour.
3.  Every painter paints a stripe.
4.  Every painter looks at the instructions of where to mail their remaining paint, posts the paint and collects their new pot when it arrives, waiting idly until it does.
5.  Unless the whole wall is painted, go back to 3
6.  Ship the piece of the wall to the customer.

Now, you see how this becomes parallel computing: just change islands to computers, painters to processes etc. What is important to notice here is **all painters do exactly the same thing**: pick up paint, paint, mail paint, receive paint, repeat previous three until wall is painted and then ship the wall away. The algorithm is completely symmetric, just the initial values (first colour and as a consequence the whole sequence of colours) differ.

It is not strictly necessary to have a completely symmetric algorithm, but for the purposes of this course we will stick to symmetric algorithms where the only asymmetry is interaction with user: only one painter talks with to the company HQ or client.

**N.B.** In a parallel code, the meaning of "program" is often ambiguous: it may refer to one of the painters (more properly called *process*) or the whole parallel contraption. We will try to avoid this dual use by using *parallel code* for the whole and *process* for the individual painter.

### Relations between painters and processes

MPI has some precise meanings for words like *rank*, *communicator*, *point-to-point* message and *collective* message. There are other concepts for more complicated things, but we won't need them.

`rank`  
In our island example, each painter corresponds to an MPI *rank*; technically, a rank is a single process (program) running on a computer somewhere. Traditionally, each CPU core would run an identical process, possibly having `if`-statements to implement an asymmetric algorithm, but that is not always the case. On this course, all the ranks will always be identical in code (but not completely symmetric) and we leave it to the adventurous to figure out how to have different processes.

`communicator`  
This is **a** postal service: there may be multiple communicators in a single parallel code (and in fact there always are at least two) and these postal services might or might not service all the islands. The two always-present communicator server all island and an no islands other than the one they are on (i.e. the other can only be used to send mail to yourself). In general, a communicator covers any subset of the ranks, including all and the empty set (though I find the latter rather useless). Every message sent will be associated with precisely one communicator and the communicator defines the possible senders and receivers; who actually sends/receives and what is defined at the time of sending/receiving.

`point-to-point message`  
These originate from one rank within a communicator and are received by a rank (possibly the same!) within the same communicator. The pots of paint we sent were point-to-point messages.

`collective message`  
These messages involve every rank in the communicator. Depending of the type of collective, it could be one-to-all, all-to-one or all-to-all. If the customer in our example was part of the MPI code, the final shipping of the walls would be an all-to-one message (`MPI_Gather()` to be precise).

You might now wonder about the "if" in the last sentence: normally in a parallel code only diagnostic information is sent all-to-one, not final results as that would introduce a bottleneck: if all the walls were shipped to one of the islands, they would have a hard time sorting them all out in the port and storing them. A typical MPI code holds so much data in memory, that no single computer can do that, so sending it all to one rank is out of the question (and even if you could do it, please do not --- it is a bad practice and will come back to haunt you later).

### Load balance

Our example is very simple and has what is called perfect *load balance*: every painter has exactly the same amount of work to do. In our example this was very easy because of the high degree of symmetry in the algorithm and such algorithms are usually preferable to ones where such easy load balancing is not possible.

You will notice the above assumes the painters all take the same amount to time to paint and mail, this is the desired situation. This is usually the case as most clusters have identical computers. Of course, if one painter is slower, others will need to wait and we are better off if faster painters are given more work. However, this is not easy to manage at all and system designers appreciate this, so you will very rarely find systems where different computers would be of different speed. [2]

It is worth noting that unequal load balance can usually be ignored on small scale problems, but once the problem size grows, the load balance usually becomes worse and worse. This means many ranks just wait without doing anything productive: the painter waits for its next pot of paint. The painter may need to take a break to sleep and eat, but your computer doesn't.

### Data and Task Distributed Parallelism

The islands example is an example of *data distributed* parallelism. This is what MPI was originally designed for. The main reasons for distributing data are to be able to access more memory than any single computer has and to be able to bring more compute-power to bear on the problem, again more than any single computer can. Data distributed parallelism works well for this and it usually ensures almost perfect load balance as well: as long as data can be distributed evenly (and there rarely is a reason not to), every rank has the same amount of job to do, so all one needs to take care of is to use as symmetric an algorithm as possible.

Task Distributed parallelism is a distributed version of task based parallelism on a single computer: the problem is broken down into tasks. Our islands example could be broken down to 49 tasks: 7 stripes of 7 colours and on a single computer that works very well. However, once things get distributed to different computers we suddenly have data locality constraints: painter A on island 1 with blue paint cannot paint the wall on island 2. Something needs to move. In data distributed, the paint moves and this is ok: there is not that much paint to move; one could even just send a voucher to get paint from the local DIY store. However, with task distributed parallelism, the data (wall without blue stripe) on which to operate will not always be where the process (painter with blue paint) is and orchestrating the data movements in an efficient way is difficult. Very difficult. Extremely hard. Fiendish.

The solution is to have two types of tasks with dependencies between them: processing tasks and data movement tasks, but then one needs to keep track of the dependencies and still orchestrate everything. The dependencies will allow the data movement tasks to arranged to happen "in the background" so wall without blue stripe will be in transit to island 1 while painter A paints the previous wall.

There are two obvious and immediate problems with this. There always needs to be no less than one wall in transit, so in our islands example, using 7 painters would become pointless as at least one would always be without a wall to paint on. Of course, the walls could be split into individual colour sized chunks: now we have 49 pieces of wall and enough for everyone to have something to paint on while other pieces are in transit. However, it is not easy to determine the right task size because the time it takes for a wall to go from island 2 to island 1 must be less or equal to the time it takes painter A to paint the previous wall. This is hard to judge, determine and ensure.

Intel has developed a library called hStreams to help with this: once you have defined the tasks and their dependencies, it will optimise the communications and computations and orchestrate the tasks and their execution. However, one still needs to create a directed acyclic graph (DAG) complete with all the tasks and their dependencies.

### Let's Speed Up My Old Code

MPI is not well suited to speed up existing codes. There are two main reasons. First, if the algorithms used are parallel, using MPI will not give much advantage. Second, non-distributed codes are very often designed in a way which would imply collective all-to-one communications like sending all the walls to a single island.

Both of these are hard to change in an existing code and it is likely a redesign of the code is easier --- assuming one has followed good code development practices and can easily test the correctness of the respective codes.

Finally, one could imagine "just accelerating" the most time-consuming parts of the code; there are many ways of doing this: using an accelerator like a GPU or Xeon Phi, using OpenMP threading (we will cover that later), or MPI. However, they all must obey a universal equation known as *Amdahl's Law*.

Suppose a code is partly run in *serial* (as opposed to parallel) and another part in parallel and that there are no latencies or overheads in the parallel part, i.e. using N parallel workers cuts the time spent to 1/N. Now every parallel code has a serial part: if nothing other, at least the startup and shutdown of the code are invariably serial. Note that even though every worker reads their instructions in parallel, this does not count as a parallel part of the code in this sense as the time spent does not depend on the number of painters: it is duplicated rather than distributed work. With these very generous assumptions, Amdahl's Law can be states as follows. Suppose the serial part takes \(t_{s}\) units of time and parallel part with single worker takes \(t_{p}\), then with \(N\) parallel workers, we get *total* code runtime speedup \(s\) of

\begin{equation}
s = \frac{t_{s}+t_{p}}{t_{s}+\tfrac{t_{p}}{N}} \xrightarrow{N \to \infty} 1 + \frac{t_{p}}{t_{s}}.
\end{equation}

The ratio \(\frac{t_{p}}{t_{s}}\) is related to the `Comp/Comm` ratio we saw earlier, but more general: this includes not just communications, but initialisation (although parts of it are often parallel), control flow, etc. Hence, even under these favourable ideal assumptions, you cannot expect big speedups unless your \(t_{p}/t_{s}\) is rather very large and unfortunately this is rarely the case. In one of the examples in this course, the ratio is approximately 5, without accounting for the fact that some of the "parallel" parts are in fact serial in the same sense as the reading of the instructions is in our islands example. So the maximum speedup you can dream of is **6x**, i.e. do in one hour what used to take six.

Canonical example: MPI Hello World
----------------------------------

### In non-interative python

``` {.python}
  %%bash
  mpirun -np 23 python -c "$(echo 'import mpi4py
  from mpi4py import MPI
  size=MPI.COMM_WORLD.Get_size()
  print("Hello, World. I am rank "+
        "{rank: 0{len}d} of your MPI communicator of {size} ranks".format(
        rank=MPI.COMM_WORLD.Get_rank(),
        len=len(str(size)),
        size=size))
  ')"
```

There is no easy way to run interactive MPI jobs with python except with a module called `ipyparallel` which we will look at soon.

### In C++

``` {.shell}
  %%bash
  cat ../codes/cpp/hello.cpp
  mpicxx -o hello ../codes/cpp/hello.cpp
  mpirun -np 23 ./hello
```

### The ipyparallel module

As seen above, python and MPI is not as nice and interactive as python usually is; and a compiled language like C of course never is. We want to change that and the easiest (though still non-trivial) and nicest way to do this is to use a python module called ipyparallel. [3]

More details in [ipyparallel documentation](http://ipyparallel.readthedocs.io/en/stable/intro.html).

Using ipyparallel is like using any python module: `import ipyparallel` and off we go. However, it requires a bit of setup before it can be used. It has two parts: a backend called `ipcluster` which is where all the computation happens and where the MPI ranks and communicators live, and an `ipcontroller` which controls the backend as instructed by the user typing into the python prompt or by the python code being executed: ipyparallel can of course be used also non-interactively.

It is worth knowing that ipyparallel is not inherently an MPI code: MPI must be explicitly brought in somehow. It is quite possible to use ipyparallel without MPI, too, but then communication between backend workers is not possible: the painters cannot send pots to each other, every pot needs to be sent to the HQ (ipcontroller) and then back to painters. Needless to say, for a code requiring anything but trivial communication, this becomes a bottle neck very quickly even if the computational data (walls) were not sent around but just small bits of instruction or such (pots of paint or vouchers).

Also, when using MPI with ipyparallel, the ipcluster, the ipcontroller, and the user's python **do not share** any communicator. They are completely different MPI universes; in fact, the ipcontroller and user's python do not even need to have MPI brought in at all (but some things may be simpler to do if they have).

Let us initialise `ipyparallel` now. The first line just imports `ipyparallel` module like any module and the second line creates a "client" connection to the ipcontroller, i.e. gives us the ability to use the parallel workers. (The parameters to `Client()` are specific to the training setup --- on a DAMTP desktop you should not need them.)

``` {.python}
  import ipyparallel
  c = ipyparallel.Client(profile="mpi", cluster_id="training_cluster_0")
```

By default, `ipyparallel` has no modules imported and doing `import module` will only import `module` on to your interactive frontend. There are two typical ways of importing into the backends. The first will import to backends **only** and the second does both front and backends:

``` {.python}
  c[:].execute("import numpy").wait()
  if not("numpy" in dir()): print("No numpy here!")
  with c[:].sync_imports():
      import scipy
  if ("scipy" in dir()): print("scipy here!")
```

If you have ever done something like `ParallelMap[#+1&, Table[Random[], {i,1,18}]]` in mathematica, ipyparallel (without MPI) is designed for precisely this kind of stuff. In fact, you could do the same in ipyparallel very easily:

``` {.python}
  # We need to load numpy also on frontend
  import numpy
  c[:].map_sync(lambda x:x+1, numpy.random.random(18))
```

Now the slice `c[:]` simply chooses which workers to use. As usual an empty start- or end-point means "up to and including the first" or "up to and including the last". We could use just 2 with

``` {.python}
  c[:2].map_sync(lambda x:x+1, numpy.random.random(18))
```

or even from the middle of the range:

``` {.python}
  c[1:3].map_sync(lambda x:x+1, numpy.random.random(18))
```

We will soon learn that there are other ways to do this, too; most importantly, we will learn how to define functions which will always transparently execute on the parallel workers, i.e. they look and feel and are used like normal interactive python functions, but magic happens when they execute.

### In interactive python (ipyparallel)

``` {.python}
  import ipyparallel as ipp
  c = ipp.Client(profile="mpi", cluster_id="training_cluster_0")
  c.ids
  directview=c[:]
  directview.execute("import mpi4py").wait()
  directview.execute("from mpi4py import MPI").wait()
  res1=directview.apply_async(
      lambda : "Hello, World. I am rank "+
      "{rank: 0{len}d} of your MPI communicator of {size} ranks".format(
          rank=MPI.COMM_WORLD.Get_rank(),
          len=len(str(MPI.COMM_WORLD.Get_size())),
          size=MPI.COMM_WORLD.Get_size()))

  for output in res1.result: print(output)
```

Basic messaging calls (see individual man pages for descriptions)
-----------------------------------------------------------------

TODO!!! Add mpi4py equivalents!

`MPI_Allgather`  
concatenate same amount of data from all ranks and send result to all ranks

`MPI_Allgatherv`  
concatenate some amount of data from all ranks and send result to all ranks

`MPI_Allreduce`  
reduction operation with results sent to all ranks

`MPI_Alltoall`  
every rank send data to every rank (think of matrix transpose!)

`MPI_Barrier`  
everyone waits until everyone's here --- should never be needed

`MPI_Bcast`  
one-to-all

`MPI_Comm_rank`  
what's my rank

`MPI_Comm_size`  
how many ranks are there

`MPI_Finalize`  
we are done

`MPI_Gather`  
get same amount of data from every rank to a single one

`MPI_Gatherv`  
get some amount of data from every rank to a single one

`MPI_Init`  
let's start

`MPI_Irecv`  
basic non-blocking message receiving routine

`MPI_Isend`  
basic non-blocking message sending routine

`MPI_Reduce`  
reduction operation with results sent to a single rank

`MPI_Scatter`  
inverse of `MPI_Gather`

`MPI_Scatterv`  
inverse of `MPI_Gatherv`

`MPI_Type_create_struct`  
define a datatype which looks like a struct

`MPI_Type_create_subarray`  
define a datatype which looks like a subarray (can also be implemented with `MPI_Type_create_struct` but this is easier)

`MPI_Wait`  
wait for non-blocking messaging operations to finish

For simple Cartesian data distribution MPI has good support routines

`MPI_Dims_create`  
companion to `MPI_Cart_create`: determines optimal rank to Cartesian lattice layout

`MPI_Cart_coords`  
rank -\> (i,j,k)

`MPI_Cart_create`  
create a Cartesian MPI topology: the library knows which rank is "next to" which rank

`MPI_Cart_get`  
retrieve information about the topology

`MPI_Cart_rank`  
(i,j,k) -\> rank

`MPI_Cart_shift`  
who's rank's neighbour in given Cartesian direction

Map/Reduce with and without MPI
-------------------------------

-   runs one code for many essentially different data
-   many examples and tutorials generate input data on "master" process: avoid that
    -   it does not scale
    -   it is not how Map/Reduce works
    -   it restricts you to small problem sizes
    -   COSMOS is a special case where you can do a medium size problem that way
-   no communication during computation
-   we imported `MPI` to our workers above, so no need to do it again
-   but we now need numpy

``` {.python}
  directview.execute("import numpy")
```

This is our "reduce" bit in MPI and without. It does nothing but allocates a buffer `redsum` to receive results into and then calls one of the MPI reduction functions with the input data. As a result, rank 0 will have the result in the function-local variable `redsum` and the others will have their `redsum` untouched, i.e. the value is `numpy.nan` which we initialise to separate them from the reduced result. They all return their `redsum` to the caller.

The decorator `@directview.parallel()`, provided by ipyparallel, tells python this routine must run on the parallel workers and moreover it will chunk and split its input suitably for each worker. Note that the input parameter will **always** be a list, even though we expect just one element.

``` {.python}
  @directview.parallel(block=True)
  def greduce(localval):
      localval = numpy.array(localval)
      redsum = numpy.zeros_like(localval)*numpy.nan
      MPI.COMM_WORLD.Reduce([localval, MPI.DOUBLE], [redsum, MPI.DOUBLE], op=MPI.SUM, root=0)
      return redsum
  def greduce_noMPI(gobalval):
      return reduce(lambda x,y:x+y, local_map_noMPI, 0)
```

Our "map" routine is even simpler, it just calculates sum of all elements of its input, `data`, with `data.sum()` and returns the value.

``` {.python}
  @directview.parallel(block=True)
  def lmap(data):
      sum = numpy.array(data).sum() 
      return sum
```

But we also need to somehow give some data to the parallel reducer. Many examples generate such data on one rank or on the ipyparallel interactive console, but that does not scale at all and produces two nasty bottlenecks

-   the memory on the machine running the console must be big enough for the whole data (or some clever iterator constructs must be used) and
-   all the data gets sent through a single node, the IPController whose bandwidth now limits performance. Best if each rank can figure out its input data independently, just like Hadoop/Mapreduce usually (always?) does.
-   `@directview.remote(block=boolean)` decorator
    -   provided by `ipyparallel`
    -   arranges the decorated function to be called on the remote workers instead of the frontend
    -   once per worker and
    -   all with same parameters (although our parameter list is actually empty)
    -   if `block=True` the function returns after it is finished (like a normal function)
    -   if `block=False` the function immediately return an `ASyncResult` instance as its return value and we need to figure out the actual result later using its methods and attributes
    -   there is another common decorator, `directview.parallel` which also arranges the function to be executed by the available (i.e. not already busy doing something) parallel workers, but now with arguments, which must be a list, scattered to the workers in a maximally symmetric way

``` {.python}
  @directview.remote(block=True)
  def get_data():
      len = 1e7
      loclen = numpy.ceil(len*1.0/MPI.COMM_WORLD.Get_size())
      myrank=MPI.COMM_WORLD.Get_rank()
      return numpy.arange(loclen*myrank, min(len,loclen*(1+myrank)))
  @directview.parallel(block=True)
  def get_data_noMPI(myinput):
      len = 1e7
      loclen = numpy.ceil(len*1.0/myinput[0][0])
      myrank=myinput[0][1]
      return numpy.arange(loclen*myrank, min(len,loclen*(1+myrank)))
```

Now we can actually run this beast, one step at a time.

``` {.python}
  input_data=get_data()
  input_data_noMPI=get_data_noMPI([ [len(directview.targets),i] for i in range(0,len(directview.targets))])
  local_map=lmap(input_data)
  local_map_noMPI=lmap(input_data_noMPI)
  global_reduce=greduce(local_map)
  global_reduce_noMPI=greduce_noMPI(local_map_noMPI)
  print(global_reduce, global_reduce_noMPI)
```

Note how just one worker gives the sensible result: that is because `MPI_Reduce` sends the answer to one worker only; `MPI_Allreduce` would broadcast it to everyone.

Running the equivalent code non-interactively does not cause such funny output since there is no `ipcontroller` to gather results (which is not scalable anyway). You can find a directly-runnable version of this code in `codes/python/mapreduce.py`:

``` {.bash}
  %%bash
  cat ../codes/python/mapreduce.py
  mpirun -np 8 python -- ../codes/python/mapreduce.py
```

Distributed Computing
---------------------

-   runs (typically) one code for essentially single, but distributed, data
-   as the ranks are collectively operating on a single task, they need to communicate during computation

### The maximum of the gradient

-   as an example, we'll compute the gradient of a function over a distributed lattice and find its maximum value
-   immediate problem: discrete gradient depends on neighbouring lattice points, but on a data distributed code sometimes the neighbouring point will belong to a different rank!
-   in MPI we of course pass a message: the message copies the necessary lattice points from the "owner" rank to the "borrower"
    -   the borrower should not alter the values at the points it thus receives
    -   the borrowed points are called *ghost* or *halo* points or cells
    -   the ghost cells are used to make computations near the boundaries
    -   pink is external boundary, grey are the ghost cells; note that vertical axis is periodic
    -   coordinates shown are "global"

![](images/ghosts.png)

-   build this piecemeal, but first, we initialise the parallel environment

``` {.python}
  import ipyparallel
  c = ipyparallel.Client(profile="mpi", cluster_id="training_cluster_0")
  directview=c[:]
  directview.block=True
  with directview.sync_imports():
      import numpy
      import mpi4py
      from mpi4py import MPI
```

### define a couple of book-keeping classes

TODO!!! Would it be better to use docstrings?

-   `rankinfo` just holds a few "global" values of our problem, like stencil width and problem size
-   `Get_rank` and `Get_size` find out this rank's id and total number of ranks, respectively
-   `localsizes` has 2 extra points in each dimension: these will hold the ghost points
-   `serialised_print` will print out its arguments one rank at a time to avoid mess like above
-   in general, you do not want every rank to print: it will kill performance
    -   rather gather all messages to a few ranks (or just one) and print from there if every rank's output is needed

``` {.python}
  class rankinfo(object):
      ndim=3
      periods=[False, True, True]
      stencil_width = 1
      def __init__(self, sizes):
          self.rank=MPI.COMM_WORLD.Get_rank()
          self.size=MPI.COMM_WORLD.Get_size()
          self.localsizes=[x+rankinfo.stencil_width*2 for x in sizes]
  directview["rankinfo"]=rankinfo

  def serialised_print(msg, topo):
      # serialised printing: be VERY careful with structures like this lest you get a deadlock:
      # every rank MUST eventually call the Barrier!
      myrank = topo.Get_rank()
      for rankid in range(0,topo.Get_size()):
          if (myrank == rankid):
              print(msg)
          topo.Barrier()
      return
  directview["serialised_print"]=serialised_print
```

### set up the lattice

-   `topology` holds our (Cartesian) grid related information
    -   the preceding call `Compute_dims` just finds `self.me.ndim` factors of `self.me.size`: that will become rank layout in the Cartesian grid;
        -   the algorithm is implementation specific, but usually tries to find factors close to each other in size
        -   N.B. apart from a few exceptions, the MPI standard specifies an **interface**, not **implementations** so **never** depend on what a particular implementation does behind the scenes: that may change ay any time
    -   the important function here is `MPI.COMM_WORLD.Create_cart`, which actually creates the topology
    -   `reorder=True` means rank numbers in the new communicator may be different than in the old one
    -   the `Shift()` calls tell us who on our left, right, ahead, behind, below, above --- we need those later so we save them to a dict of dicts
    -   we also define an informative `print_info` function, it has no functional role

``` {.python}
  class topology(object):
      def __init__(self, rankinfo):
          self.me=rankinfo
          self.dims=MPI.Compute_dims(self.me.size, self.me.ndim)
          self.topology=MPI.COMM_WORLD.Create_cart(self.dims, periods=self.me.periods, reorder=True)
          left,right = self.topology.Shift(0,1)
          front,back = self.topology.Shift(1,1)
          up,down = self.topology.Shift(2,1)
          self.shifts={"X": {"up": up, "down": down},
                       "Y": {"up": back, "down": front},
                       "Z": {"up": right, "down": left}}
      def print_info(self):
          coords = self.topology.Get_coords(self.me.rank)
          msg="I am rank {rank} and I live at {coords}.".format(
              rank=self.me.rank, coords=coords)
          msg = msg + "Inverse lookup of {coords} gives rank {rank}.".format(
              coords=coords,rank=self.topology.Get_cart_rank(coords))
          serialised_print(msg, self.topology)
  directview["topology"]=topology
```

### set up the datatypes

-   MPI always sends a given number of elements of a particular datatype from consequtive memory locations: you should think of this as always sending a 1D array of a particular datatype and of given length
-   however, we want to send 2D subsets of our 3D data, which is contiguous only on two of the six faces of our cuboid, so we next set up custom datatypes for easy messaging between ranks
    -   with our datatype, sends and receives can be done directly from the actual array because MPI now understands about a datatype whose elements are 2D subsets of a 3D array
    -   with this datatype, we only send *one* element, which is trivially contiguous with itself, but note that *internally* the datatype does not need to be contiguous and in fact only 4 of our 12 datatypes are internally contiguous
-   you will often see examples and codes where data is copied to a temporary buffer for sends and receives instead of using datatypes
    -   this is usually not necessary: once the datatype is set up, it will do the copying for you and your code becomes cleaner and easier to maintain
        -   avoids having an identical loop in several places in the code
        -   change to the comms needs to be implemented in just one place
    -   MPI can sometimes also buffer things internally, causing two copies of data to be used
    -   downside of our approach is **the send buffer must not be altered** before the transfer is complete
-   we need a total of 12 datatypes: one per direction per axis
-   `MPI.DOUBLE.Create_subarray` creates the datatype using `MPI.DOUBLE` as the underlying unit datatype element
    -   `sizes` is the (local) size of the full 3D array of elements of type `MPI.DOUBLE`
    -   the second argument is the size and shape of the subarray: this needs to be of the same dimension as the full array, but one dimension can be just 1 grid point deep as we do here, effectively making it one dimension lower
    -   the third argument specifies the grid point where the subarray starts, in coordinates of the full local array
-   an example 2D subarray of a 2D array
    -   this would be created using `MPI.INT.Create_subarray([5,5], [2,3], [1,2])`
    -   shaded area is the subarray
    -   works similarly in any number of dimensions --- just a bit hard to draw 3D diagrams

![](images/MPI_subarray.png)

``` {.python}
  class ghost_data(object):
      def __init__(self, topology, sizes):
          self.mx,self.my,self.mz = sizes
          self.types = {}
          self.axes = {}
          for axis in ["X", "Y", "Z"]:
              self.types[axis]={}
              self.axes[axis]={}
              for op in ["send", "recv"]:
                  self.types[axis][op]={}
                  for movements in [("up","down"), ("down","up")]:
                      movement, negmovement = movements
                      self.types[axis][op][movement] = MPI.DOUBLE.Create_subarray(sizes,
                                                                                  self.get_plaq(axis),
                                                                                  self.get_corner(axis,op,movement))
                      self.types[axis][op][movement].Commit()
                      self.axes[axis][movement]={"dest": topology.shifts[axis][movement],
                                                 "source": topology.shifts[axis][negmovement]}
      def axis2basisvec(self, axis):
          return numpy.array([axis == "X", axis == "Y", axis == "Z"], dtype=numpy.float64)
      def get_plaq(self, axis):
          vec = self.axis2basisvec(axis)
          pl = [self.mx, self.my, self.mz]*(1-vec)+vec
          return list(pl)
      def get_corner(self, axis, sendrecv, movement):
          vec = self.axis2basisvec(axis)
          axis_size = [x[0] for x in ((self.mx, "X"), (self.my, "Y"), (self.mz, "Z")) if x[1]==axis][0]
          loc = vec*( (movement=="down") +
                      ((sendrecv=="send")*(movement=="up") or (sendrecv=="recv")*(movement=="down"))*(axis_size-2)
                  )
          return list(loc)
  directview["ghost_data"]=ghost_data
```

You can use `MPI_Type_create_darray()` to create a "distributed array" suitable for e.g. reading to/writing from a binary file in parallel. It will not have ghosts, though, which is what we want here.

### set up routines for exchanging the ghost data

-   we split this in two parts to allow for computation to take place while data is in transit
    -   do that by putting computations between calls to `ghost_exchange_start` and `ghost_exchange_finish`
    -   in practice very few MPI implementations actually transfer any data before the `Wait` call, but one should always allow for the few which do and perhaps others will improve in time, giving your code a free boost
    -   it does complicate code, though, so this code does not take advantage it
-   this simply uses the dictionaries in the class we defined above to loop over the receives and sends
-   **always** post the `Recv` before the `Send` lest deadlocks occur
-   there is also a (blocking!) `Sendrecv` call which is guaranteed never to deadlock

``` {.python}
  def ghost_exchange_start(topo, localarray, ghostdefs):
      commslist=[]
      for axis in ["X", "Y", "Z"]:
          for direction in ["up", "down"]:
              commslist.append(
                  topo.topology.Irecv(
                      buf=[localarray, 1, ghostdefs.types[axis]["recv"][direction]],
                      source=ghostdefs.axes[axis][direction]["source"], tag=0))
      for axis in ["X", "Y", "Z"]:
          for direction in ["up", "down"]:
              commslist.append(
                  topo.topology.Isend(
                      buf=[localarray, 1, ghostdefs.types[axis]["send"][direction]],
                      dest=ghostdefs.axes[axis][direction]["dest"], tag=0))
      return commslist
  directview["ghost_exchange_start"]=ghost_exchange_start

  def ghost_exchange_finish(commslist):
      MPI.Request.Waitall(commslist)
      return
  directview["ghost_exchange_finish"]=ghost_exchange_finish
```

### initialise the lattice

-   we have not yet looked at I/O so set up initial data to be just squares of consecutive integers starting from our MPI rank number squared
    -   TODO!!! description is wrong
    -   This should actually be samples of a differentiable function, but finding the global coordinates is a bit tricky (need to call to `Get_rank` and `Cart_coords` plus arithmetic) so we want to keep it simple here
-   a small complication comes from the fact that we only want to initialise the non-ghosted regions

``` {.python}
  def initialise_values(me, topo):
      size = topo.topology.Get_size()
      local_array = numpy.zeros(me.localsizes)
      procsalong, periods, mycoord = topo.topology.Get_topo()
      mycorner = mycoord*numpy.array(me.localsizes)
      for z in xrange(me.localsizes[0]):
          for y in xrange(me.localsizes[1]):
              start = mycorner[2] + 5*(y+mycorner[1])*procsalong[2] + 3*5*(z+mycorner[0])*procsalong[1]*procsalong[2]
              stop = start + me.localsizes[2]
              local_array[z,y,:] = numpy.arange(start, stop, step=1)**2
      return local_array
  directview["initialise_values"]=initialise_values
```

### compute the gradients over the global lattice

-   first we exchange the ghosts so we can compute the gradients on boundary points, too
-   external boundaries are periodic except in the "Z" direction, where the boundaries are at their initial values
    -   in this case they are all zero as that's how they were initialised above
    -   the initial values act as the boundary conditions
-   `numpy.gradient` computes 2nd order finite difference derivatives in all directions, i.e. the gradient

``` {.python}
  def compute_grad(topology, local_array, ghostdefs):
      commslist=ghost_exchange_start(topology, local_array, ghostdefs)
      # could do work here but NOT use ghost points!
      ghost_exchange_finish(commslist)
      gradients=numpy.array(numpy.gradient(local_array))[:,1:-1,1:-1,1:-1]
      return gradients
  directview["compute_grad"]=compute_grad
```

### find maximum value in a global array

-   we find the local maximum
-   reserve space for the global answer and
-   use `Allreduce` to

    1.  apply `MPI.MAX` operation (`find greatest) to all local values
         - there are other operations, too, like =MPI.SUM` etc
    2.  send the result to all ranks
-   we finally return both local and global answers

``` {.python}
  def find_global_max(topology, local_array, ghostdefs):
      maxgrad_local = numpy.array(local_array).max()
      maxgrad_global = numpy.zeros_like(maxgrad_local)
      topology.topology.Allreduce([maxgrad_local, MPI.DOUBLE],
                                  [maxgrad_global, MPI.DOUBLE],
                                  op=MPI.MAX)
      return maxgrad_local, maxgrad_global
  directview["find_global_max"]=find_global_max
```

### the main code

-   before main code, we define a rudimentary correctness testing routine: it knows the expected correct answers up to 8 ranks and could easily be expanded to calculate the expected result from an analytic expression

``` {.python}
  def testme(maxgrad, topology):
      size=topology.topology.Get_size()
      rank=topology.topology.Get_rank()
      expected=[1650.0,7632.0,13032.0,32119.5]
      return maxgrad == expected[size-1]
  directview["testme"]=testme
```

-   the main routine, it just calls what we defined above

``` {.python}
  @directview.remote(block=False)
  def main():
      me=rankinfo(sizes=[3,4,5])
      cartesian_topology=topology(me)
      ghosts = ghost_data(cartesian_topology, me.localsizes)
      cartesian_topology.print_info()
      local_array = initialise_values(me, cartesian_topology)
      gradients = compute_grad(cartesian_topology, local_array, ghosts)
      result_l, result_g = find_global_max(cartesian_topology, gradients, ghosts)
      serialised_print("Rank {rank} had max gradient {maxgrad_l} while the global was {maxgrad_g}."
                       .format(
                           rank=me.rank,
                           maxgrad_l=result_l,
                           maxgrad_g=result_g),
                       cartesian_topology.topology)
      if (me.rank == 0):
          if (testme(result_g, cartesian_topology)):
              print("Result is correct.")
          else:
              print("Result is incorrect!")
      return result_g, local_array
```

-   now everything is defined and we can run the code

``` {.python}
  results=main()
  results.wait()
  results.display_outputs()
```

-   this code is available in `codes/python/distributed_computing_interactive.py`
-   another version is available in `codes/python/distributed_computing_universal.py`
    -   it runs in a notebook, from the command line with ipyparallel installed and with pure MPI
    -   includes some extra wrapper functions to make that possible
-   a modularised, better compartmentalised, non-interactive version is available at `codes/python/distributed_computing.py`
-   notice that these codes have no differences in the classes or functions themselves
    -   only differences are some wrappers and extra decorators
    -   **allows development of real parallel batch codes in ipyparallel/ipython/notebook environment**
    -   if there is any concern of the effect of the wrappers on performance, one can just remove the compatibility layer
    -   this version is available at `codes/python/distributed_computing_batch.py`

TODO!!! No, it is not, it is an old version now!

Prototyping Parallel Programs Using Python
==========================================

Linear Example: \(\nabla^2 \phi(x,y) = g(x,y)\)
-----------------------------------------------

### Direct Solve (\(O((Nx*Ny)^2)\))

Let's see what it looks like. First we need to import some modules; if you come from C/Fortran and are new to python, think of these as "use module" or "\#include \<module.h\>" lines combined with "-lmodule"

``` {.python}
  from __future__ import division
  import sys
  import time
  import numpy
  import mpi4py
  from mpi4py import MPI
  import petsc4py
  petsc4py.init(sys.argv)
  from petsc4py import PETSc
  import cProfile
```

Next we need to set up some infrastructure. `PETSc.DMDA` is the most basic distributed data manager and its `StencilType` and `BoundaryType` attributes just define what shape region around a grid point is needed to compute whatever we want to compute at that point (options are `BOX` and `STAR`); `ssize` will become the size of this stencil later.

``` {.python}
  stype = PETSc.DMDA.StencilType.BOX
  ssize = 1
```

Boundaries of the lattice can be `NONE`, `GHOSTED`, or `PERIODIC`; `GHOSTED` means the ghost points exist on the external boundary, too. Those can be used to store boundary conditions. With `NONE` you need to special case the exterior boundary.

``` {.python}
  bx    = PETSc.DMDA.BoundaryType.GHOSTED
  by    = PETSc.DMDA.BoundaryType.GHOSTED
  bz    = PETSc.DMDA.BoundaryType.GHOSTED
```

We will have a look at MPI later, but with PETSc you rarely need any explicit MPI. For these examples, this is the only thing you need: the "name" of the MPI world we want to work in. For PETSc the top-level code almost invariably uses `PETSc.COMM_WORLD`.

``` {.python}
  comm = PETSc.COMM_WORLD
```

PETSc handles those pesky things called command line parameters (and configuration files!) for us, too. Let's see if we have been passed `m`, `n`, or `p`.

``` {.python}
  OptDB = PETSc.Options() #get PETSc option DB
  m = OptDB.getInt('m', PETSc.DECIDE)
  n = OptDB.getInt('n', PETSc.DECIDE)
  p = OptDB.getInt('p', PETSc.DECIDE)
```

This creates the distributed manager. Note how our variables above get used. There's one we did not explain: `dof` is simply the number of degrees of freedom (number of unknowns) per lattice site. The negative `sizes` values tells PETSc to get the value from command line parameters `-da_grid_x M`, `-da_grid_y N`, and `-da_grid_z P`, or use the magnitudes of the supplied parameter `sizes` if the corresponding cmdline one cannot be found. The latter two method calls handle the command line bit.

``` {.python}
  dm = PETSc.DMDA().create(dim=3, sizes = (-11,-7,-5), proc_sizes=(m,n,p),
                           boundary_type=(bx,by,bz), stencil_type=stype,
                           stencil_width = ssize, dof = 1, comm = comm, setup = False)
  dm.setFromOptions()
  dm.setUp()
```

At this stage we need to define our physics. We use the Poisson equation here, but any linear boundary value PDE would work. Obviously, initial value problems must be dealt differently. Comments on the code

`__init__()`  
-   called when class is instantiated; it just saves given lattice spacings `dx`, `dy`, `dz`; and creates a data structure `self.g` for the RHS.

`rhs()`  
-   the call to `self.dm.getVecArray()` is PETSc's most useful call: the returned data structure is a numpy array, indexable in almost the normal fashion with distributed-global indices
    -   almost: index `array[-1]` is not last element, but "left of 0": the first ghost element to the "left of 0"
-   we specify the value of `self.g` here simply as all ones, could be anything (as long as linear);
-   the `rhs_array` will gets its values in the usual fashion from 7-point Laplacian stencil
-   `self.dm.getRanges()` returns the distributed-local ranges of the lattice coordinates currect rank has
-   `self.dm.getSizes()` gives the distributed-global sizes of the lattice: needed in the loop for detecting when to apply boundary conditions
-   finally, a very inefficient loop setting the values: for most lattice points it is a `rhs_array[i,j,k] ` rhs<sub>array</sub>[i,j,k]= but this is only ran once, so not too important
-   the non-trivial values are the boundary conditions (i.e. u=7), see plot

![How a 2D slice at k=1 of the 3D data maps boundary conditions onto a 1D RHS vector; note that lattice points (i,j,k)=(1,1,0) and (1,1,2) also map to rhs(0) from outside the diagram.](file:images/boundary_conditions.png)

`compute_operators()`  
-   dealing with distributed matrices almost always starts with `A.zeroEntries()` and ends with `A.assemble()`
-   `PETSc.Mat.Stencil()` returns a convenient helper object to deal with setting sparse matrix values simply by using the lattice coordinates instead of tranaforming them to matrix indices
    -   slight performance penalty but again we do this just once
-   `row.index` and `col.index` are used to calculate the matrix indices from lattice indices; `row.field` and `col.field` refer to which degree of freedom these values apply to in said conversion (the `dof` in the `PETSc.DMDA().create()`)
-   finally, `A.setValueStencil()` puts the values in

``` {.python}
  class poisson(object):
      def __init__(self, dm, dx_i):
          self.dm = dm
          self.dx = dx_i["dx"]
          self.dy = dx_i["dy"]
          self.dz = dx_i["dz"]
          self.g = self.dm.createGlobalVector()

      def rhs(self, ksp, rhs):
          dx,dy,dz=self.dx,self.dy,self.dz
          rhs_array = self.dm.getVecArray(rhs)
          g_ = self.dm.getVecArray(self.g)
          g_[:] = 1.0 
          rhs_array[:]=g_[:]*numpy.ones_like(rhs_array)*dx*dy*dz
          (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
          mx,my,mz = self.dm.getSizes()
          for k in range(zs, ze):
              for j in range(ys, ye):
                  for i in range(xs, xe):
                          rhs_array[i,j,k] = (rhs_array[i,j,k] +
                                              7.0*(((k==0) + (k==mz-1))*dx*dy/dz +
                                                   ((j==0) + (j==my-1))*dx*dz/dy +
                                                   ((i==0) + (i==mx-1))*dy*dz/dx))
          return

      def compute_operators(self, ksp, J, A):
          A.zeroEntries()
          row = PETSc.Mat.Stencil()
          col = PETSc.Mat.Stencil()
          (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
          dx,dy,dz=self.dx,self.dy,self.dz
          for k in range(zs, ze):
              for j in range(ys, ye):
                  for i in range(xs, xe):
                      row.index = (i,j,k)
                      row.field = 0
                      diag = -2.0*(dx*dy/dz+dx*dz/dy+dy*dz/dx)
                      for index, value in [
                              ((i,j,k-1), +1.0/dz*dx*dy),
                              ((i,j-1,k), +1.0/dy*dx*dz),
                              ((i-1,j,k), +1.0/dx*dy*dz),
                              ((i, j, k), diag),
                              ((i+1,j,k), +1.0/dx*dy*dz),
                              ((i,j+1,k), +1.0/dy*dx*dz),
                              ((i,j,k+1), +1.0/dz*dx*dy)]:
                          col.index = index
                          col.field = 0
                          A.setValueStencil(row, col, value)
          A.assemble()
          return None
  poisson_problem = poisson(dm, {"dx":0.1, "dy":0.1, "dz":0.1})
```

Now we are ready to set up the solver. First we create a KSP solver,

``` {.python}
  ksp = PETSc.KSP().create()
```

tell it that we are working with a distributed manager (`ksp.setDM()`),

``` {.python}
  ksp.setDM(dm)
```

then tell the solver how to generate the RHS and matrix

``` {.python}
  ksp.setComputeRHS(poisson_problem.rhs)
  ksp.setComputeOperators(poisson_problem.compute_operators)
```

and finally finish the setup by accommodating all configuration file and command-line options

``` {.python}
  ksp.setFromOptions()
```

Before we can solve the problem we need a workspace (`sol`) and an initial guess (`field`), which we just leave uninitialised now: for a KSP solver, that of course affects convergence speed but unlike Newton algorithms, it makes no difference otherwise: the inverse of the matrix is unique when it exists.

``` {.python}
  field = dm.createGlobalVector()
  sol = field.duplicate()
```

The solver would now normally be invoked with `ksp.solve(field,sol)` but we wrap this in python's built-in profiler to get some information of the efficiency of the code and where is spends its time: `time.clock()` just gives the CPU time used since either the beginning of the process and `cProfile.run()` sets up profiling and then gives its parameter to `exec` and outputs statistics after that finishes (i.e. in this case after divergence or convergence).

``` {.python}
  start = time.clock()
  cProfile.run("ksp.solve(field,sol)")
  end = time.clock()
```

Now we can have a look at the solution; we will later see how we could visualise this. The code in the git repo has a rudimentary visualiser built in.

``` {.python}
  ksp.getSolution()[:]
```

That program was actually ran in an MPI distributed parallel fashion, PETSc just hides almost all of it. The only hints of MPI are in the *LocalVector* and *COMM<sub>WORLD</sub>* names. In this case, it ran with just one processor core, for reasons of interactive python. We can run a proper 8-way-parallel (8 *ranks*) quite easily, though: all we need is a "magic" string `%%bash` in our code below. First `git` checks out the correct version of the training codebase and then mpirun executes the code with 8 ranks. Finally it reverts back to master branch.

``` {.bash}
  %%bash
  mpirun -np 8 python -- ../codes/python/poisson_ksp.py -da_grid_x 80 -da_grid_y 70 -da_grid_z 60
```

-   PETSc's "direct" Krylov SPace (KSP) solvers are iterative
    -   this avoids matrix inversion, which is and \(O(N^2.8)\) operation (Strassen; Coppersmith-Winograd is \(O(N^2.373)\) but not know to been ever implemented)
    -   iterative KSP solvers get away with iterating matrix-vector only, which is \(O(N^2)\)
    -   one thus hopes KSP solver does not take too many iterations compared to iterative inversion
-   Next we forget about linearity and use non-linear solvers to solve \(\nabla^2 \phi(x,y) - g(x,y) = 0\)

Non-linear Example: TODO!!! global vortex?
------------------------------------------

-   Use SNES, TS, TAU?

### Problems (which we'll fix later)

-   RHS is not very fast
-   Not very memory friendly (can you spot extra copies?)
-   Did we save it?
-   Did we look at it?
-   Jacobian!

Cookbook: TODO!!!
-----------------

Efficient and portable I/O
==========================

-   You will eventually want to read and write data, too...
-   avoid machine dependent I/O, like
    -   Fortran's \`OPEN(UNIT = 10, FORM = ’unformatted’, FILE = filename)\`
    -   C's \`fwrite(data, size, count, file)\`

    as these will be useless on some (in fortran's case **most**) other computers should you ever move your files around.
-   latency is more likely to ruin performance than anything else, so unless you know exactly where the I/O bottleneck is, do big writes into big files, even buffering internally in your code if necessary
-   use parallel I/O, like MPI I/O or MPI-enabled HDF5 library

Save the solution of our Poisson problem in HDF5
------------------------------------------------

-   Best to save parameters as well; PETScBag???

Checkpointing
-------------

-   Your code should be able to do this on its own to support solving the problem by running the code several times: often not possible to obtain access to a computer for long enough to solve in one go.
-   Basically, you save your iterate (current best estimate solution) and later load it from file instead of using random or hard coded initial conditions.

### cookbook

-   basic MPI I/O and HDF5 I/O examples (hyperslabbing?)
-   Parallel Visualisation: ParaView

Have a Look at Our Solution to Poisson
--------------------------------------

-   Using ParaView as that comes with all the bells and whistles you can think of; other possibilities are Visit and for small (workstation-size) problems mayavi.

ParaView Filters
----------------

-   Just introduce some, they can find out about the rest
-   Streamlines???

Parallel ParaView!!!
--------------------

Optimisation
============

-   You've got a well designed, parallel, scalable code, but it still takes way too long to run.
-   Time to turn the prototype into a real workhorse!

Some Hardware Considerations (this is optimisation)
---------------------------------------------------

-   I/O will kill performance, avoid as much as you can
    -   7200 rpm is not that much if you need to read/write a million times: if you need to wait for the expectation value of 1/14400 min every time you access the disc, the million writes take about an hour regardless of how much you actually read/write. If you do it in one go, you'll get away with one wait.
    -   OS filesystem and hard disc caches alleviate this, but cannot completely hide the effect and for reads they are **almost completely powerless** to help you!
    -   SSD is much better than HDD but the effect is still there
    -   interleave with other tasks if you can
-   Interconnect Latency
-   Interconnect Bandwidth
-   Memory subsystem performance
    -   NUMA causes issues even on single socket these days
    -   pages
    -   78.6 GB/s (Broadwell) vs 915.2 GF/s gives 95 F/B!!!
    -   latency!
    -   caches help overcome this
        -   but introduce a degree of unpredictability
    -   cache is multi-level, only last level can keep up with core; prefetching
-   other on-core issues have to do with parallelism
    -   false sharing
    -   page ownership
-   in-core
    -   how to load a cache line
    -   cache associativity! (write an example code???)
    -   branch misprediction
        -   [here](http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array) is an example
        -   function calls are effectively branch misses
    -   pipeline stall
    -   pipeline flush

Profiling Your Code
-------------------

C+Python = Cython: finally a fast RHS
-------------------------------------

-   Jacobian, too; remember the FD checks!

OpenMP
------

-   Should we do this earlier in Choosing Your Algo???

Vector Unit and GPU: SIMD/MIMD
------------------------------

Crash Course on Other Libraries?
================================

-   BLAS
-   LAPACK
-   ScaLAPACK
-   SLEPc
-   FEniCS/dolfin (FEM)
-   ClawPACK/PyCLAW (FVM)
-   FFT
-   Trilinos
-   More Tools and Good Practices

Offload to an accelerator or GPU
--------------------------------

-   Provides much higher performance/watt than normal CPU
-   We use Xeon Phi in the examples; GPU is similar but slightly trickier
-   Can be done explicitly, but almost never worth the effort: Intel's compiler has two ways to offload using compiler directives (pragmas) only, LEO and OpenMP.
-   GPU very popular in e.g. machine learning and neural networks, so transferable skill

### Example/Cookbook

-   some basic example
-   courses available

Debugging
---------

-   Your code does not work or produces an incorrect result: you want a debugger
-   cosmos has Allinea's DDT, but any debugger will
    -   show you your variable's values at any position in the code (unless they are optimised away)
    -   be able to step one source-code line at a time
    -   insert breakpoints
    -   find where the crash occurred (may need you to enable core file output: \`ulimit -c unlimited\`
-   Further resources!

### Example Debugging

-   buffer overflow / array access out of bounds / write() to a NULL or closed file or …
-   Big Computers: Parallel Processing

High Performance Computer Architecture
--------------------------------------

### Terminology

-   core
-   process
-   thread
-   distributed processing
-   interprocess communication

### Memory layout

-   access patterns: striding, re-reading, …
-   access cost: CPU much faster than RAM
-   NUMA: not all memory is equal (OpenMP and KNL issues)

MPI
---

-   By far the most common way to handle very big problems
-   Either to access more memory than a single machine (**node**) has or solve a problem faster by bringing more machines to bear
-   Wastes some resources to interprocess communications: scaling
    -   weak scaling: access more memory
    -   strong scaling: solve quicker
    -   strong scaling will eventually fail
-   Break your problem into as independent chunks as possible
    -   completely independent: embarrassingly parallel (most parallel I/O)
    -   solving a PDE: each node processes a simple subset of the domain, but needs to communicate on the edges
    -   moving particles cause issues with load-balancing: genuinely hard to solve
        -   redistributing particles between nodes is very slow
        -   not redistributing is not acceptable either
        -   can do different things on different nodes but only suits certain situations
-   Explicit inter-node communication model: message passing
    -   as noted earlier, this communication comes with a cost in latency
    -   has relatively limited bandwidth
    -   must be minimised
    -   can lead to deadlocks, be careful! (example?)
-   Think parallel and distributed from the beginning: saves you from a lot of trouble later
-   Think scaling, too: very hard to change an algorithm which does not scale to one which does after the whole program is written around it
    -   any global algorithm suffers from poor scaling
    -   unfortunately this includes Fourier, so think hard whether you need it or not: for just solving an equation you probably don't (Fast Multipole Method, hybrid…)
-   Should rarely need directly: libraries like PETSc, SLEPc, Chombo, Trilinos
-   Pointers to courses (UIS?)

### Basic example/cookbook:

-   read in/initialise data
-   process data
-   output data
-   and same with PETSc
-   in python

OpenMP
------

-   compiler-based approach to parallel programming (and some other things, too)
-   can also be used to offload to accelerators/GPUs
-   needs a single, shared memory node to operate: use MPI to distribute across nodes, OpenMP to parallelise inside a node
-   cosmos has an unusual case of shared memory across nodes (properly called NUMA-nodes in this case), so both work
-   OpenMP and NUMA issues
-   OpenMP is shared memory model with implicit parallelism, so must be careful with what is shared and what is not
    -   false sharing
    -   data corruption can occur
    -   correct which is correct on one thread can suddenly be incorrect with OpenMP parallelism
    -   must use critical/atomic sections to guard shared written data
        -   effectively non-parallel region in an otherwise parallelised chunk
        -   example
-   OpenMP can also deadlock
-   we have course material, can even run a course if needed

### Basic example/cookbook

-   solve the same as with MPI

Hybrid MPI+OpenMP
-----------------

### Just an Example

Profiling, Visualisation, ...?
==============================

Profiling
---------

-   What is this and why should I?
-   VTune, MAP, HPCToolkit(, tau, PAPI)

### Example session?

Visualisation
-------------

-   matplotlib for 2D
-   paraview (stereo!!!) and visit for 3D
-   python scripting
-   xdmf files
-   OSPRay?

### Examples/Cookbook

-   at least read a hdf5 file using xdmf
-   isosurfaces
-   streamlines
-   volume rendering
-   Example Codes in a Cookbook / Exercises

Root Finding (\(F(x)=0\))
-------------------------

-   let N be the number of elements of x typically \(N>>10^6\), even billions
-   Newton scales as \(O(N^2)\): for dense problems now we DO need to think about memory
    -   consider a quasi-Newton method, preferably a LMVM like BFGS
    -   consider it even if memory does not constrain you as the Hessian inversion (even when done iteratively) is quite costly compared to a quasi-Newton method's approximation
-   quite often conjugate gradient is efficient enough
-   use a proper library again so swapping between algorithms is simply a matter of changing a command line parameter!
-   Elliptic PDE's fall into this category (both linear and non-linear should be treated iteratively)
-   how to find a global minimum? GA and MC?
-   secant may be better in 1D but in 1D you are not really doing HPC
-   non-differentiable problems (Carola)

### Example/cookbook

-   Solve ? with PETSc using several algorithms (but no Hessian?)

Integration
-----------

-   not sure what to say here

Inter- and extrapolation
------------------------

-   not sure of this either
-   spline is evil

Representing a PDE in numerical, discrete form
----------------------------------------------

-   Of course, these become \(F(x)=0\) once discretised
-   Finite Differences
    -   Pros: conceptually simple, easy to write
    -   Cons: hard to improve accuracy once written, values between points
-   Finite Elements
    -   Pros: can handle complicated geometries easily, mathematically very well understood
    -   Cons: needs a weak form of the PDE, gruelling hard to implement from scratch
-   Finite Volumes
-   Again, use libraries: FEniCS/dolfin for FEM, FVM?

### Example/cookbook

-   Poisson in all three
-   And in funny geometry using FEM

Time Evolution
--------------

-   Explicit Timestepping
    -   RK4
    -   Dormand-Prince
    -   low memory RK (check details)
    -   CFL
-   Implicit Timestepping
    -   backward Euler
    -   Crank-Nicholson
    -   Adams–Bashforth, Adams–Moulton
    -   the step-internal equation solving usually too costly but for stiff problems and problems with very restrictive CFL the price may be acceptable (see IMEX)
-   Stability (A-stability)
    -   Dahlquist Barrier
-   Implicit-Explicit etc

### Examples/Cookbook

-   PETSc provides a nice interface with command-line swappable algorithms
    -   you need to provide Jacobian for Implicit ones unless you want even slower code

Large Matrices
--------------

-   Avoid dense matrices if you can, but if you cannot, ScaLAPACK and EigenExa are your friends (PETSc can do dense, too, but probably not as efficiently)
-   For sparse matrices: PETSc, SLEPc
-   Even better than sparse: **shell matrix**
    -   need to know how to get element \(a_{ij}\) from \(i,j\)
    -   no need to store the matrix at all!
    -   PETSc has extensive support
    -   sometimes called "matrix free" methods, algorithms etc but that's confusing as some methods genuinely have no matrices so they don't have shell matrices either
-   Decompositions and eigenvalues
    -   GMRES (PETSc)
    -   Krylov-Schur (SLEPc)
    -   preconditioning

### Examples/Cookbook

-   Find (some) eigenvalues of dense, sparse, and shell

Spectral Methods
----------------

-   FFT from FFTW, MKL
-   very elegant, especially on pen and paper, but not on computer: avoid due to scalability issues

Random Numbers
--------------

-   PETSc has a parallel random number generator
-   if not using PETSc, SPRNG is a decent parallel one
-   of course the numbers are only as random as the seed or operating system entropy collector

### Examples/Cookbook

-   just a worked out example for both libraries
-   Science Topic 1
-   Science Topic 2
-   Science Topic 3
-   Science Topic 4

from practices
==============

Cookbook: TODO!!! what goes in here???
--------------------------------------

TODO Best Practices, part 1: basic libraries
--------------------------------------------

-   use them, no point in writing your own unless you're a researcher in algorithm implementation: others are paid to develop them for you
-   of course, it's useful to LEARN how algorithms work by writing your own, but…
-   BLAS for linear algebra manipulations
-   LAPACK for small linear equations
-   there are several options for large linear equations which are discussed later
    -   hopefully your matrix is mostly zeros so can use **sparse matrix** representations
-   Remember: never invert a matrix numerically
    -   slow
    -   non-restartable
    -   inaccurate
    -   typically unstable
    -   iterative solution of the equation wins on all counts
        -   even when you need all eigenvalues (=the inverse)
        -   due to controllable and better accuracy
    -   ok, you may invert a diagonal matrix if you really want
-   non-linear equations: always iteratively solve linear ones
-   bunch of other libraries for Fourier, F(x)=0, Runge-Kutta etc; more on them later

### Examples/cookbook

-   matrix "solve" using LAPACK (And no, Ben, no preconditioning yet)
-   oops, ran out of memory! What now?

TODO (Will move to good practices section!) Open Data Policies
--------------------------------------------------------------

[More here](http://www.data.cam.ac.uk/) but it is something you should probably be prepared for.

Cambridge FAQ on Open Data says:

> 1.  Do I need to share my source code?
>
> If your source code is necessary to validate your research findings, then you are expected to share it.

It is not clear to me how **your** source would **ever** be necessary to validate the results but best prepare for publishing nevertheless.

Which also relates to

### Copyright and Licencing and Publishing a Program

Crash Course on Other Libraries?
================================

-   BLAS
-   LAPACK
-   ScaLAPACK
-   SLEPc
-   FEniCS/dolfin (FEM)
-   ClawPACK/PyCLAW (FVM)
-   FFT
-   Trilinos
-   More Tools and Good Practices

Offload to an accelerator or GPU
--------------------------------

-   Provides much higher performance/watt than normal CPU
-   We use Xeon Phi in the examples; GPU is similar but slightly trickier
-   Can be done explicitly, but almost never worth the effort: Intel's compiler has two ways to offload using compiler directives (pragmas) only, LEO and OpenMP.
-   GPU very popular in e.g. machine learning and neural networks, so transferable skill

### Example/Cookbook

-   some basic example
-   courses available

Debugging
---------

-   Your code does not work or produces an incorrect result: you want a debugger
-   cosmos has Allinea's DDT, but any debugger will
    -   show you your variable's values at any position in the code (unless they are optimised away)
    -   be able to step one source-code line at a time
    -   insert breakpoints
    -   find where the crash occurred (may need you to enable core file output: \`ulimit -c unlimited\`
-   Further resources!

### Example Debugging

-   buffer overflow / array access out of bounds / write() to a NULL or closed file or …
-   Big Computers: Parallel Processing

High Performance Computer Architecture
--------------------------------------

### Terminology

-   core
-   process
-   thread
-   distributed processing
-   interprocess communication

### Memory layout

-   access patterns: striding, re-reading, …
-   access cost: CPU much faster than RAM
-   NUMA: not all memory is equal (OpenMP and KNL issues)

MPI
---

-   By far the most common way to handle very big problems
-   Either to access more memory than a single machine (**node**) has or solve a problem faster by bringing more machines to bear
-   Wastes some resources to interprocess communications: scaling
    -   weak scaling: access more memory
    -   strong scaling: solve quicker
    -   strong scaling will eventually fail
-   Break your problem into as independent chunks as possible
    -   completely independent: embarrassingly parallel (most parallel I/O)
    -   solving a PDE: each node processes a simple subset of the domain, but needs to communicate on the edges
    -   moving particles cause issues with load-balancing: genuinely hard to solve
        -   redistributing particles between nodes is very slow
        -   not redistributing is not acceptable either
        -   can do different things on different nodes but only suits certain situations
-   Explicit inter-node communication model: message passing
    -   as noted earlier, this communication comes with a cost in latency
    -   has relatively limited bandwidth
    -   must be minimised
    -   can lead to deadlocks, be careful! (example?)
-   Think parallel and distributed from the beginning: saves you from a lot of trouble later
-   Think scaling, too: very hard to change an algorithm which does not scale to one which does after the whole program is written around it
    -   any global algorithm suffers from poor scaling
    -   unfortunately this includes Fourier, so think hard whether you need it or not: for just solving an equation you probably don't (Fast Multipole Method, hybrid…)
-   Should rarely need directly: libraries like PETSc, SLEPc, Chombo, Trilinos
-   Pointers to courses (UIS?)

### Basic example/cookbook:

-   read in/initialise data
-   process data
-   output data
-   and same with PETSc
-   in python

OpenMP
------

-   compiler-based approach to parallel programming (and some other things, too)
-   can also be used to offload to accelerators/GPUs
-   needs a single, shared memory node to operate: use MPI to distribute across nodes, OpenMP to parallelise inside a node
-   cosmos has an unusual case of shared memory across nodes (properly called NUMA-nodes in this case), so both work
-   OpenMP and NUMA issues
-   OpenMP is shared memory model with implicit parallelism, so must be careful with what is shared and what is not
    -   false sharing
    -   data corruption can occur
    -   correct which is correct on one thread can suddenly be incorrect with OpenMP parallelism
    -   must use critical/atomic sections to guard shared written data
        -   effectively non-parallel region in an otherwise parallelised chunk
        -   example
-   OpenMP can also deadlock
-   we have course material, can even run a course if needed

### Basic example/cookbook

-   solve the same as with MPI

Hybrid MPI+OpenMP
-----------------

### Just an Example

Profiling, Visualisation, ...?
==============================

Profiling
---------

-   What is this and why should I?
-   VTune, MAP, HPCToolkit(, tau, PAPI)

### Example session?

Visualisation
-------------

-   matplotlib for 2D
-   paraview (stereo!!!) and visit for 3D
-   python scripting
-   xdmf files
-   OSPRay?

### Examples/Cookbook

-   at least read a hdf5 file using xdmf
-   isosurfaces
-   streamlines
-   volume rendering
-   Example Codes in a Cookbook / Exercises

Root Finding (\(F(x)=0\))
-------------------------

-   let N be the number of elements of x typically \(N>>10^6\), even billions
-   Newton scales as \(O(N^2)\): for dense problems now we DO need to think about memory
    -   consider a quasi-Newton method, preferably a LMVM like BFGS
    -   consider it even if memory does not constrain you as the Hessian inversion (even when done iteratively) is quite costly compared to a quasi-Newton method's approximation
-   quite often conjugate gradient is efficient enough
-   use a proper library again so swapping between algorithms is simply a matter of changing a command line parameter!
-   Elliptic PDE's fall into this category (both linear and non-linear should be treated iteratively)
-   how to find a global minimum? GA and MC?
-   secant may be better in 1D but in 1D you are not really doing HPC
-   non-differentiable problems (Carola)

### Example/cookbook

-   Solve ? with PETSc using several algorithms (but no Hessian?)

Integration
-----------

-   not sure what to say here

Inter- and extrapolation
------------------------

-   not sure of this either
-   spline is evil

Representing a PDE in numerical, discrete form
----------------------------------------------

-   Of course, these become \(F(x)=0\) once discretised
-   Finite Differences
    -   Pros: conceptually simple, easy to write
    -   Cons: hard to improve accuracy once written, values between points
-   Finite Elements
    -   Pros: can handle complicated geometries easily, mathematically very well understood
    -   Cons: needs a weak form of the PDE, gruelling hard to implement from scratch
-   Finite Volumes
-   Again, use libraries: FEniCS/dolfin for FEM, FVM?

### Example/cookbook

-   Poisson in all three
-   And in funny geometry using FEM

Time Evolution
--------------

-   Explicit Timestepping
    -   RK4
    -   Dormand-Prince
    -   low memory RK (check details)
    -   CFL
-   Implicit Timestepping
    -   backward Euler
    -   Crank-Nicholson
    -   Adams–Bashforth, Adams–Moulton
    -   the step-internal equation solving usually too costly but for stiff problems and problems with very restrictive CFL the price may be acceptable (see IMEX)
-   Stability (A-stability)
    -   Dahlquist Barrier
-   Implicit-Explicit etc

### Examples/Cookbook

-   PETSc provides a nice interface with command-line swappable algorithms
    -   you need to provide Jacobian for Implicit ones unless you want even slower code

Large Matrices
--------------

-   Avoid dense matrices if you can, but if you cannot, ScaLAPACK and EigenExa are your friends (PETSc can do dense, too, but probably not as efficiently)
-   For sparse matrices: PETSc, SLEPc
-   Even better than sparse: **shell matrix**
    -   need to know how to get element \(a_{ij}\) from \(i,j\)
    -   no need to store the matrix at all!
    -   PETSc has extensive support
    -   sometimes called "matrix free" methods, algorithms etc but that's confusing as some methods genuinely have no matrices so they don't have shell matrices either
-   Decompositions and eigenvalues
    -   GMRES (PETSc)
    -   Krylov-Schur (SLEPc)
    -   preconditioning

### Examples/Cookbook

-   Find (some) eigenvalues of dense, sparse, and shell

Spectral Methods
----------------

-   FFT from FFTW, MKL
-   very elegant, especially on pen and paper, but not on computer: avoid due to scalability issues

Random Numbers
--------------

-   PETSc has a parallel random number generator
-   if not using PETSc, SPRNG is a decent parallel one
-   of course the numbers are only as random as the seed or operating system entropy collector

### Examples/Cookbook

-   just a worked out example for both libraries
-   Science Topic 1
-   Science Topic 2
-   Science Topic 3
-   Science Topic 4
-   foobar
-   The petsc4py TS example achieves 3.5% of peak performance for the whole routine on an Ivy Bridge class cpu.
    -   the "computational kernel" is significantly better
        -   but since we are mostly interested in OpenMP's SIMD and offload capabilities, we'll cover them very quickly

ESP Cookbook/Project

TODOs
=====

-   don't do shell in notebook, it needs to be interactive in a real shell
-   docker for everyone?
-   ipyparallel install instr.
-   s/egrep/grep -E/
-   send people to www.ucs.cam.ac.uk.docs/course-notes/unix-courses/Building
-   where's the strong scaling plot?!?
-   explain what MPI actually does in the message pass (wtf???)
-   DO just the laplacian MPI example FIRST in petsc, THEN do poisson
-   at the end, have a non-debug-version of mpi code
-   init function could be global (x\*\*2+y\*\*2+z\*\*2) --- petsc so much easier
-   diagrammise stuff on board
-   RELEASE-TODO:
    -   "file:" generated by pandoc must be removed
    -   TODOs must be removed
-   build peetsc code bit by bit and even add viz at the end
-   cython things
-   tbb?
-   spyder!
-   check what catam has now? python? what modules? quota? qt version?
-   survey their python skills
-   Carola wants a short description

[1] \*By default ipcluster will try to use all resources on all the machines it connects to!\* The `-n 2` specifies we want 2 parallel workers. You can use any positive integer (although 1 would not give you any parallelism), but please consider that other people may be using the machine as well, so unless you do this on your personal desk- or laptop, please do not use all the resources.

[2] But often there is a "login node" which is of different capability than the nodes (computers) intended to execute parallel codes. COSMOS is a hybrid here: there are such login nodes but the execution nodes can also be directly logged onto, fudging the difference.

