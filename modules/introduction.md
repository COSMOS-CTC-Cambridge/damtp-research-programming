Intro to Research Computing
===========================

Course website: <https://github.com/juhaj/damtp-research-programming>
---------------------------------------------------------------------

Getting the Course Material
---------------------------

-   the above web page is a git repository which you will learn about later
    -   until then, you can treat it as a web page and lecture notes
    -   this lecture is <https://github.com/juhaj/damtp-research-programming/blob/master/modules/introduction.md>
-   if you want to take the notes with you off-line right away, clone the repo with
    -   `git clone git@github.com:juhaj/damtp-research-programming.git` (if you have ssh-keys on github)
    -   `git clone https://github.com/juhaj/damtp-research-programming.git` (if you don't)
    -   or use old fashion download link on the website
-   change to the directory where you placed the clone
    -   if you used the defaults, do `cd damtp-research-programming`

### Some Instructions on Using the Course Repo

-   you'll learn these on the next two lectures but here's a summary
    -   after cloning, make your own branch: `git branch mybranch`
    -   check it out: `git checkout mybranch`
    -   whatever you do, you do on this branch to avoid complications later
    -   when you want the next lecture's material, do: `git checkout master` and `git pull`
    -   you now have two options: merge `master` to `mybranch` or lose your changes to `mybranch`
    -   merge: `git checkout mybranch` followed by `git merge master`, you need to sort your conflicts
    -   lose local changes: `git checkout -f master`, `git pull`, and `git checkout -B mybranch master`
    -   go back to doing whatever you do
-   note:
    -   you do not have write access to the github repo so you cannot push
    -   but you cannot screw up anything else than your local copy either so safe to play around if you wish

Goals
-----

### Good Programming Practices (a transferable skill)

-   we will cover
    -   version/revision control
    -   modularity
    -   correctness testing
    -   if time, we'll look at continuous integration, testing and deployment
-   many employers will set programming tests as part of their interview
    -   put in unit tests, show understanding of git, write modular and clean code, and you'll be head and shoulders above many others

### Python (a transferable skill)

-   a very widely used programming language
    -   a Data Science company University Careers Service event just described python as the number one skill to have in Data Science jobs
-   we'll cover the most important (from a scientist's point of view) parts of the python language
    -   it'll be easy to familiarise yourself with more industrially oriented bits, too

### Computing at Scale: HPC and HPDA

-   Get familiar with computing at scales past your desktop/laptop
    -   not as transferable as the above, but quite crucial in science
-   the assumption throughout is your problem is too big for a desktop/laptop
-   HPC traditionally has two very different categories:
    -   capacity/throughput: problems can possibly be solved without HPC but need to solve so MANY that HPC is necessary to give the capacity
    -   capability: cannot solve any other way either due to time constraints or resource limits
-   HPC involves a lot of software development
    -   very few fields can enjoy off-the-shelf programs
-   solving (and simulating, but that's just an equation to solve) very difficult and very large (sets of) equations (someone called a 6.5 TB dataset "tiny baby data" on DiRAC Day 2016)
-   HPDA is the processing and visualisation of these very large sets of data (larger than even most Big Data)
-   HPDA is also the processing and visualisation of streaming, observation etc data
-   rarely need to worry about memory consumption: distributed parallel processing allows access to more
    -   but watch out for the odd case where sizeof(memory) = sizeof(problem)<sup>N</sup> and N&gt;1
-   very rapidly changing requirements and continuous development
    -   this resembles AGILE software development in companies
-   need to worry about the computer hardware
    -   embedded software development shares this need and is also concerned by the speed and efficiency

### Know What Is Available and How To Do Things Right™

-   almost every mathematical problem is computationally unique, so no generalisations on this course, but
-   will give you an idea of how to proceed and where to start
-   and what not to do, ever
-   COSMOS IPCC at DAMTP works on code "modernisation" and optimisation
-   So what do we do? As examples of why doing things right matters:
    -   e.g. MODAL program now 100× faster than before
    -   another cosmology code more than 10× faster (actually the original was so slow it never finished, which gives just a lower limit of 10×)
    -   Fixing file-writing routine in yet another two codes to get 20x and 5x speedups.
    -   not only saves researchers' time but also allows more science to be done with the same resource (supercomputer)
    -   Can save a lot of time with very little effort: yet another code achieved 3-fold speedup in just an hour's worth of work

### This course will

-   have a look at algorithms, how to choose a good one, what things to consider in the process, how the computing hardware affects algorithms and imposes constraints on the algorithm etc
-   teach how to find out what your program spends most of its time doing ("profile" the code), apply the most important and crucial first steps in removing computational bottlenecks and optimise your code: often these initial steps can provide anything from 2- to 100-fold speedup depending on the case at hand so quite relevant even for small programs
-   cover the basic concepts of parallel programming, paralel processing, distributed processing both using a Map/Reduce approach and a more powerful message-passing based one (MPI); we also cover how to avoid the nitty gritty details of message passing
-   learning how to prototype your codes quickly taking advantage of existing libraries and how this prototyping can often turn into a heavy-lifting workhorse with practically no effort at all
-   towards the end, we will cover efficient data input/output, and parallel visualisation
-   together these provide a load of transferable skills: big data, software development, and programing skills are all sought after by industry as well as the obvious problem solving skills

The Unix Shell and SSH
======================

-   You'll ask why is this so difficult, there are two reasons
    -   First, when your laptop is not enough, there is a learning curve (which I try to smoothen)
