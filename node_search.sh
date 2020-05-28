#!/bin/bash

# This scipt simply loads the python3 module for a user and then runs node_search. This
# must be done as python3 is not loaded by default. 

module load python &>/dev/null

# Calling the node_search.py script. All arugments will be passed into node_search
# The following needs to be the absolute path to node_search.py
/afs/crc.nd.edu/user/c/ckankel/Public/node_search/node_search.py $@ 

