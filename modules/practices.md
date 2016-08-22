Good Programming Practices and basic tools
==========================================

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
