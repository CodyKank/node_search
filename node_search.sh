#!/bin/bash

# This bash script is simply loading the necesarry env var's to allow a user to run python 3
# without having to 'module load python/3.4.0' Then, it is running the node_search.py script.
# Please read that script or view the man page for more information on what that script does.

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/afs/crc.nd.edu/x86_64_linux/python/3.4.0/gcc-4.8.0/lib/
export LOADEDMODULES=$LOADEDMODULES:opt_local/1.0:gcc/4.8.0:python/3.4.0
export _LMFILES_=$_LMFILES_:/afs/crc.nd.edu/x86_64_linux/Modules/modules/development_tools_and_libraries/python/3.4.0
export PATH=$PATH:/afs/crc.nd.edu/x86_64_linux/python/3.4.0/gcc-4.8.0/bin

/afs/crc.nd.edu/user/c/ckankel/Public/node_search/node_search.py $@

