Intro to Research Computing
===========================

Getting the Course Material
---------------------------

-   all the course material is available in a git repository — naturally
-   the repo to clone is TODO!!! ON GITHUB!!! `git clone git://git.csx.cam.ac.uk/damtp-ipcc/HPC_course_student`
-   some instructions on using the course repo
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

Goal
----

-   Learn good programming practices (a transferable skill)
-   Learn python, a very widely used programming language (a transferable skill)
-   Get familiar with computing at scales past your desktop/laptop (not as transferable as the above, but quite crucial in science); the assumption throughout is your problem is too big for a desktop/laptop

Programming Practices
---------------------

-   version/revision control
-   modularity
-   correctness testing
-   if time, we'll look at continuous integration, testing and deployment

Python
------

-   the main language used in this course
-   we'll cover the most important (from a scientist's point of view) parts of the python language

Computing at Scale: HPC and HPDA
--------------------------------

-   HPC traditionally has two categories:
    -   capacity/throughput: problems can possibly be solved without HPC but need to solve so MANY that HPC is necessary to give the capacity
    -   capability: cannot solve any other way either due to time constraints or resource limits
-   HPC involves a lot of software development
    -   very few fields can enjoy off-the-shelf programs
-   solving (and simulating, but that's just an equation to solve) very difficult and very large (sets of) equations (someone called a 6.5 TB dataset "tiny baby data" on DiRAC Day 2016)
-   HPDA is the processing and visualisation of these very large sets of data (larger than even most Big Data)
-   HPDA is also the processing and visualisation of streaming, observation etc data
-   almost every mathematical problem is computationally unique, so no generalisations on this course, but
    -   will give you an idea of how to proceed and where to start
    -   and what not to do, ever
    -   COSMOS IPCC at DAMTP can help you further:
        -   e.g. MODAL program now 100× faster than before
        -   another cosmology code more than 10× faster (actually the original was so slow it never finished, which gives just a lower limit of 10×)
        -   Fixing file-writing routine in yet another two codes to get 20x and 5x speedups.
        -   not only saves researchers' time but also allows more science to be done with the same resource (supercomputer)
        -   Can save a lot of time with very little effort: yet another code achieved 3-fold speedup in just an hour's worth of work

This course will
----------------

-   expect you know the basics of using a UNIX shell, there's a decent tutorial you should look at at <http://www.ee.surrey.ac.uk/Teaching/Unix/>
-   have a look at algorithms, how to choose a good one, what things to consider in the process, how the computing hardware affects algorithms and imposes constraints on the algorithm etc
-   teach how to find out what your program spends most of its time doing ("profile" the code), apply the most important and crucial first steps in removing computational bottlenecks and optimise your code: often these initial steps can provide anything from 2- to 100-fold speedup depending on the case at hand so quite relevant even for small programs
-   cover the basic concepts of parallel programming, paralel processing, distributed processing both using a Map/Reduce approach and a more powerful message-passing based one (MPI); we also cover how to avoid the nitty gritty details of message passing
-   learning how to prototype your codes quickly taking advantage of existing libraries and how this prototyping can often turn into a heavy-lifting workhorse with practically no effort at all
-   towards the end, we will cover efficient data input/output, and parallel visualisation
-   together these provide a load of transferable skills: big data, software development, and programing skills are all sought after by industry as well as the obvious problem solving skills

Some unique things about HPC/HPDA:
----------------------------------

-   rarely need to worry about memory consumption: distributed parallel processing allows access to more
    -   but watch out for the odd case where sizeof(memory) = sizeof(problem)<sup>N</sup> and N&gt;1
-   very rapidly changing requirements and continuous development
    -   this resembles AGILE software development in companies
-   need to worry about the computer hardware
