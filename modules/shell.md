Shell
=====

-   **PLEASE CHANGE THE KERNEL** to bash kernel (from the Kernel-menu)

The Unix Command Line
---------------------

-   This course uses the unix command line *shell* a lot and it's the de-facto interface to high performance computers
-   We'll use \`ssh\` to access a shell on a remote supercomputer
-   You can choose you favourite shell, all our examples use *bash*
-   The next magic cell sets up the environment and directories etc in a directory `training/tmp` in your home directory. It will be totally wiped in the process: if you run this outside the training accounts of this course, please be careful.

``` bash
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

``` bash
ls
```

-   list "hidden" files, too

``` bash
ls -a
```

-   give detailed information (we'll learn to interpret it later)

``` bash
ls -l
```

-   list only `examplefile1` and the contents of `exampledirectory1` directory

``` bash
ls -l examplefile1 exampledirectory1
```

-   a full usage help; works with almost all commands

``` bash
ls --help
```

-   When you need to operate on lots of files, use *glob patterns* like this

``` bash
echo example*
```

``` bash
echo examplefile[0-8]
```

-   Do yourself a favour and avoid "special" characters in filenames: `` ()[]{} &*$?\|#'"` ``
-   Yes, that is a space in there!
-   All of these work if you *escape* them correctly, but it is complicated:

``` bash
touch horriblen\ame1 horriblen\\ame2 horrible\\name3 horri\\blename4 horrible\ example5
```

-   and it gets even worse if you try to write a script and process this programmatically
-   besides `\` can give you nasty surprises:

``` bash
ls horr*
```

-   oops...

``` bash
rm horrible\name3 horrible example5
```

-   but only `/` is really forbidden in file names: you just cannot have it in a file name

### Making Directories

-   directory is just a special type file
    -   initially a directory is like an empty file
    -   creating one is equally simple

``` bash
mkdir exampledirectory10
```

-   there are other kinds of special files, too: *sockets*, *device nodes*, *symbolic links*, etc

### Changing to a different Directory

Go to directory called `exampledirectory1`

``` bash
cd exampledirectory1
```

-   and back to where you were

``` bash
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

``` bash
pwd
```

### Copying Files

-   copy `examplefile1` to `examplefile11`

``` bash
cp examplefile1 examplefile11
```

-   and `examplefile1` to `exampledirectory2/` with its original name

``` bash
cp examplefile1 exampledirectory2/
```

-   or with a new name

``` bash
cp examplefile1 exampledirectory2/newname
```

-   this is equivalent to move followed by copy or vice versa (but has different semantics)
-   a more sophisticated copying tool is called *rsync*

``` bash
rsync -a exampledirectory2/ exampledirectory12/
```

-   limitation: the above can only create one directory level, i.e. `rsync -a exampledirectory2/ exampledirectory12/exampledirectory13/` will fail

### Moving Files

-   just like copying

``` bash
mv examplefile11 exampledirectory3/
```

-   let's move it back to current directory but with a new name

``` bash
mv exampledirectory3/examplefile11 ./newname
```

-   remember, directories are files, so can `cp`, `rsync`, `mv` directories just as well as files
-   but be careful: `cp|mv|rsync directory dest` behaves differently depending on whether `dest` exists or not
-   be extra careful: all these commands overwrite destinations without warning

### Removing Files and directories

-   remove a file

``` bash
rm examplefile9
```

-   but directories cannot be removed unless they are empty

``` bash
rmdir exampledirectory1
```

-   so remove the contents first

``` bash
rm exampledirectory1/*
rmdir exampledirectory1
```

-   there is a way to do this with one command, but people have removed all their files with it by accident...

Shell, part 3: Working with Files from the Command Line
-------------------------------------------------------

### Displaying the contents of a file on the screen

-   for small files

``` bash
cat examplefile3
```

-   but this is not useful for big files as they'll scroll off the screen, better one is `less examplefile3` or `more examplefile3` if `less` is unavailable

### Searching the contents of a file

-   find "This" from a `examplefile3`

``` bash
grep -E "This" examplefile3
```

-   or use a *regular expression* or *regex* to match any string with capital "T" followed after any number (including zero) characters by "s"

``` bash
grep -E "T.*s" examplefile3
```

-   or "T" followed ... by "x"

``` bash
grep -E "T.*x" examplefile3
```

-   `man grep` for more details on what a `regex` is

### STDIO and friends

-   It is often useful to capture the output of a program or send input programmatically to a program: redirection!
-   all programs have three non-seekable files open: standard input where user types in, standard output where program writes normal output, and standard error where program is supposed to write error messages
-   normally called *stdin*, *stdout* and *stderr*
-   redirect stdout with "&gt;"

``` bash
ls > examplefile12
```

-   no output: it went to `examplefile2`:

``` bash
cat examplefile12
```

-   can also redirect stdin to a file using redirection: this provides input to `grep example` from a file

``` bash
grep example < examplefile12
grep directory < examplefile12
```

-   Can also combine these without going via files: *pipes*; note that the following only "pipes" stdout

``` bash
ls | grep example
```

-   A more complicated case with stderr ("2&gt;") redirected to `/dev/null` (a black hole):

``` bash
ls i_do_not_exist examplefile1 2> /dev/null | grep example
```

-   now errors go to where stdout goes ("&1" means "same as stdout")

``` bash
ls i_do_not_exist examplefile1 2>&1 | grep file
```

-   can also swap them around: now stderr is redirected to stdout (2&gt;&1) but stdout is then redirected to `/dev/null` ("1&gt;/dev/null"), so pipe ("|") only gets stderr now

``` bash
ls i_do_not_exist examplefile1 2>&1 1>/dev/null | grep file
```

-   order matters: this sends everything to `/dev/null`

``` bash
ls i_do_not_exist examplefile1 1>/dev/null 2>&1 | grep file
```

Shell, part 4: Permissions, Processes, and the Environment
----------------------------------------------------------

### Securing your files

-   Basic permissions are for *owner*, *group*, *other*.
-   `r` means read, `w` write, `x` execute (or "change into" for directories)

``` bash
ls -la
```

-   Careful! Permissions on directory control new file creation and deletion, so can "steal" files! (Just demonstrating the sequence, the original file is already owned by the training user.)

``` bash
mv examplefile3 3elifelpmaxe
cat 3elifelpmaxe > examplefile3
rm 3elifelpmaxe
```

-   For shared directories, use `getfacl` and `setfacl` but they have limitations: only files originally created in the directory inherit the ACL, files moved there from elsewhere will need further action.
-   ACLs are the only practical way of setting up shared directories
-   Give group `users` read access and current user read-write access to `exampledirectory3` and make sure subsequent files and directories created there have similar permissions:

``` bash
setfacl --default --modify u::rw exampledirectory3
setfacl --default --modify g::r exampledirectory3
setfacl --modify u:${USER}:rw exampledirectory3
setfacl --modify g:users:r exampledirectory3
```

### Managing processes

-   list your own processes controlled by current (pseudo) terminal

``` bash
ps
```

-   or list all processes and threads

``` bash
ps -elfyL
```

-   or processes in a parent-child tree

``` bash
ps -eflyH
```

-   another way to print the tree; fancy, but not very useful compared to above

``` bash
pstree
```

-   two interactive views of processes, including their CPU utilisation

``` bash
top -b -n1
```

-   there is also `htop` on most modern machines
-   You can execute processes "in the background"

``` bash
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

``` bash
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

``` bash
echo ${PATH}
```

-   check where (in `PATH`) command `ls` lives

``` bash
which ls
```

-   easiest way to give a long list of parameters to a program

``` bash
find exampledirectory12 -name 'example*1' -print0 |xargs -0 ls -l
```

Examples / Practicals / Exercises (these go to cookbook, too)
-------------------------------------------------------------

TODO!!! These need a pre-prepared directory!

1.  Remove file called `foo bar`.
2.  Remove file called `-rf`.
3.  Remove file called `nasty $SHELL`,
4.  Remove LaTeX compilation by-products (i.e. files ending in `.log` and `.aux`) in a directory hierarchy which is 10 levels deep (hint: `find`).
5.  List all executable files in the current directory, including "hidden" ones.
6.  List of directories in the current directory.
7.  Write a shell script which outputs "`filename` is older" if `filename` is older than your `~/.bashrc` and "`filename` is newer" it it is not older.
8.  Create yourself an ssh private-public-keypair and set up key based authentication with your training account on `slurmcluster01.westeurope.cloudapp.azure.com`.
9.  You should pick one and learn the tricks of at least one text-editor to make your life easier on the terminal. This course does not cover that but popular choices are `emacs` and `vim`; emacs has a good built-in tutorial which you can easily access the first time you start it.

Further resources
-----------------

