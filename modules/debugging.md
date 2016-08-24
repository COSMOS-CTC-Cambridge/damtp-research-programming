Debugging
=========

Debugging python, the standard way
----------------------------------

-   The usual wisdom uses python standard library's `pdb` module which comes with a handy way of allowing you to start debugging from a particular position in your code
    -   often not what you want as often we do not know where the problem is, just that we e.g. get the wrong result
    -   for that, the same module also comes as a standalone executable also called `pdb` so let's see that first

``` {.python}
  def bottom_func(x):
      y = x**2
      return str(x) + " squared equals " + str(y)

  def top_func(z):
      result = bottom_func(z)
      return result

  top_func("7")
```

-   you can now debug this in several ways, the easiest ones being to run `python -m pdb ../codes/python/debugging_pdb.py` or `pdb ../codes/python/debugging_pdb.py` and typing commands as you go
-   some useful commands are

|command|short|description|
|-------|-----|-----------|
|continue|c|continue (or start) executing the program "normally"|
|next|n|step onto the next line of code, running any function calls on the current line|
|step|s|step onto the next python statement whose implementation is written in python, i.e. into functions etc|
|backtrace|bt|shows the current call-tree or *stack trace*|
|breakpoint|break|set a breakpoint: both continue and next will stop when they encounter a breakpoint|
|print|p|print something; note that the full form "p" will invoke python's usual print|
|up|u|go up one stack frame|
|down|d|go down one stack frame|
|until|u|Continue execution until the line with a number greater than the current one is reached or until the current frame returns|

-   I rarely need more

Debugging python, the jupyter way
---------------------------------

-   now that we have just produced an error above, jupyter can examine what happened using *ipdb*, the ipython version of pdb
-   notice that this becomes interactive: feel free to experiment if you can find out what went wrong and why

``` {.python}
  %debug
```

-   ipython can also automatically call the post-mortem debugger if you pass it `--pdb` command line parameter
-   you can also start from the beginning and proceed line-by-lien, as `python -m pdb something.py` and `pdb something.py` would do

``` {.python}

```

-   in python, debugging rarely involves more than finding type errors and such where post-mortem is enough to reveal the cause or algorithmic errors where one usually needs to proceed step-by-step and make sure the algorithm does what one thinks it should
-   in Fortran, but especially in C/C++ things are worse: you can e.g. have memory corruption and no access to your variables (the debugger says "variable has been optimised away" or similar: at run-time that variable just sits on a register
-   unfortunately, python also provides an exceptionally annoying case: threads

Debugging python threads
------------------------

-   the following is a simple producer-consumer system:
    -   `produce()` puts timestamps into a queue in a separate thread
    -   `consume()` takes them and prints them in the main thread
    -   yes, `produce()` would never exit, but it will exit when main thread does

``` {.python}
  import threading, Queue, datetime, time
  q=Queue.Queue()

  def produce():
      myvar = 1
      while True:
          if (q.empty()):
              q.put(datetime.datetime.utcnow())
          else:
              time.sleep(1)
              mistake
      return

  def consume():
      now = datetime.datetime.utcnow()
      while (datetime.datetime.utcnow() > now + datetime.timedelta(seconds=100)):
          if not(q.empty()):
              print(q.get())
      return

  t=threading.Thread(target=produce)
  t.start()
  consume()
```

-   run in pdb, fails to help you!
-   run with ipdb, fails to help you!
-   even the magic %debug and %%debug fail
-   but pudb does not
    -   unfortunately cannot integrate that to jupyter, so will need to go console
    -   but it works exactly like pdb or %%debug except it can handle threads

Debugging C/Fortran
-------------------

-   always compile with `-g` to keep debugging symbols in your binary
-   we look at `gdb` as it is just about always available; on cosmos the Allinea Forge debugger is far superior (including price)
-   like with python, there are two ways: post mortem and line-by-line
    -   post-mortem requires a *core file*, so you need to make sure you have enough space for one and you ulimit is big eonugh

``` {.python}
  %%bash
  ulimit -c
  ulimit -c unlimited
```

-   changing =ulimit=s is a one-way door: they can be increased *once* per session
-   to get the post-mortem, do `gdb executablefilename corefilename`
-   to get line-by-line, one should either start the whole code inside a debugger, like `gdb
         ../codes/cpp/c_segfaults` or start the program normally and later attach debugger with `gdb executablefilename processid`
-   additional useful command: `start` which begins the program (python debuggers skip this step)
-   let's have a look at two buggy C codes

``` {.c}
  #include <stdio.h>

  int main(int argc, char * argv[]) {
    int input1, input2;
    FILE *fptr;
    fptr = fopen("../codes/cpp/subdir1/input.dat","r");
    fread(&input1, sizeof(int), 1, fptr);
    fclose(fptr);
    fptr = fopen("../codes/cpp/subdirO/input.dat","r");
    fread(&input2, sizeof(int), 1, fptr);
    fclose(fptr);
    printf("%i + %i = %i\n", input1, input2, input1+input2);
    return 0;
  }
```

-   why does this segfault? to fire up a `gdb` e.g. in the jupyter terminal
-   another problematic fellow

``` {.c}
  #include <stdlib.h>
  double * invert_data(int sz) {
    double dest[20] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19};
    double * data = (double *) calloc(20,sizeof(double));
    for (int ii=0; ii<=sz; ++ii) {
      dest[10+ii] = data[ii]+1;
    }
    return data;
  }

  int main(int argc, char * argv[]) {
    double *data = invert_data(10);
    free(data);
    return 0;
  }
```

