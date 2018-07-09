#!/bin/bash

# This scipt simply loads the python3 module for a user and then runs node_search. This
# must be done as python3 is not loaded by default. 
# ckankel --> This is who to bug about this

# NOTE: These requirements will change when the loaded version of Python 3 is deprecated. To mend,
# line 11 must be changed to load a correct version of python. As of July 5, 2018 python/3.6.4
# is the latest version of python.


path_to_python3=$(which python3 2>/dev/null)
if [ ! -x "$path_to_python3" ] ; then
    source /opt/crc/Modules/current/init/bash
    module load python/3.6.4
fi


# Calling the node_search.py script. All arugments will be passed into node_search
# The following needs to be the absolute path to node_search.py
/afs/crc.nd.edu/user/c/ckankel/Public/node_search/node_search.py $@ 

