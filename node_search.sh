#!/bin/bash

# This bash script is simply loading the necesarry env var's to allow a user to run python 3
# without having to 'module load python/3.4.0' Then, it is running the node_search.py script.
# Please read that script or view the man page for more information on what that script does.

# NOTE: These requirements will change when there is a new version of Python3 installed. To update
# simply look at what is loaded in your env when you have the latest python3 module loaded for the
# following variables:


export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/crc/p/python/3.6.0/gcc/6.2.0/lib:/opt/crc/i/isl/0.15/gcc/4.8.5/lib:/opt/crc/t/texinfo/6.3/gcc/6.2.0/lib:/opt/crc/g/gdb/7.12/gcc/6.2.0/lib:/opt/crc/g/gcc/6.2.0/lib64:/opt/crc/g/gcc/6.2.0/lib:/opt/crc/usr/local/lib
export LOADEDMODULES=$LOADEDMODULES:opt_local/1.0:gcc/6.2.0:python/3.6.0
export _LMFILES_=$_LMFILES_:/afs/crc.nd.edu/x86_64_linux/Modules/modules/system_modules/opt_local/1.0:/afs/crc.nd.edu/x86_64_linux/Modules/modules/development_tools_and_libraries/gcc/6.2.0:/afs/crc.nd.edu/x86_64_linux/Modules/modules/development_tools_and_libraries/python/3.6.0
export PATH=$PATH:/opt/crc/p/python/3.6.0/gcc/6.2.0/bin:

/afs/crc.nd.edu/user/c/ckankel/Public/node_search/node_search.py $@

