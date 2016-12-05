#!/bin/bash

# This bash script is simply loading the necesarry env var's to allow a user to run python 3
# without having to 'module load python/3.4.0' Then, it is running the node_search.py script.
# Please read that script or view the man page for more information on what that script does.

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/afs/crc.nd.edu/x86_64_linux/python/3.4.0/gcc-4.8.0/lib/

/afs/crc.nd.edu/user/c/ckankel/Public/node_search/node_search.py $@

