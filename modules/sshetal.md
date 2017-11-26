SSH
===

-   strongly encrypted and authenticated connection between two computers
-   used to access a shell on a remote computer
    -   sometimes programs other than shell, too

Microsoft Azure
===============

-   MS's incarnation of a Cloud computing service
-   we'll use Azure for some of the practicals
-   if you `git clone` the course repo to Azure, you'll be able to edit, run, execute, try out things on the lecture notes as well
    -   Maths desktops and servers will also work, but you need to sort things out yourself
-   you can also run `jupyter` there to interact with the lecture notes \[see below\]
-   some of the later exercises benefit from running on the Azure HPC teaching cluster
    -   and I interact with the lecture notes there anyway
-   I have set up a cluster on Azure for you to work with, however **it** **is** **ephemeral**: you will lose files you leave there, so please regularly copy all your stuff to safety

Exercises
=========

1.  Find a terminal from your computer and run a shell in it
    1.  Find out the full path of the directory you find yourself in (your home directory)
    2.  What is the value of `$HOME` environment variable? (Print it to the terminal.)
    3.  Create a file called `PLEASE_DELETE_ME`
    4.  Delete above file

2.  Create an account on [github](https://www.github.com) if you don't have one yet.
3.  You were given a username and password for Azure.
    1.  Use them to log into `slurmcluster01.westeurope.cloudapp.azure.com`. The simplest syntax for ssh is `ssh
               <username>@<hostname>`
    2.  Repeat Exercise 1.
    3.  Create a file and use `rsync -a <source> <destination>` to copy it to safety: you should run the command on `source` if you have a machine you can `ssh` to from anywhere in the world (like `linux.ds.cam.ac.uk`, using your CRSID as the username) or you run the command on `destination` and use the Azure host as the source. Use `rsync --help` or `man rsync` to figure out how to specify a file or directory to copy.
    4.  If you know how to, clone the course repo to `/share/data/<yourusername>`

4.  There is a special program `my_jupyter` on the Azure host. This runs a pre-configured version of jupyter for your convenience and allows you to interact with the lecture notes.
    1.  Use `ssh` to log in to `slurmcluster01.westeurope.cloudapp.azure.com` using your account.
    2.  Run `my_jupyter` in that shell: this will reserve this shell, if you want to explore the machine using shell, open another `ssh` connection using another terminal.
        1.  Advanced tip: or use output redirection and backgrounding to keep using this shell, but read next task first.

    3.  Read the message printed by `jupyter`: it asks you to "login with a token". Copy that URL to your browser, but replace `localhost` with `slurmcluster01.westeurope.cloudapp.azure.com`.

