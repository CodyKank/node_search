#!/usr/bin/env python3

from pwd import getpwnam
import sys, subprocess, urllib.request, os

#Globals
TERMWIDTH = 80
PRINT_INDENT = '    ' #4 spaces, used for formatting.
DEBUG_QUEUE_HOSTGROUP = 'debug_d12chas'
GENERAL_ACCESS_QUEUE_HOSTGROUP = 'general_access'
SCRIPT_NAME = 'node_search.sh'
LOWTHRESHOLD = 0.05

"""Script to get and report information on nodes withtin the Sun Grid Engine for the CRC. It uses
the subprocess module to execute bash(tcsh) commands and gather their output. Basically this script is a fancy
swiss army knife parsing tool. Currently works with python 3.4.0 and 3.6.0. Created July 2016.
Issues or bugs contact: ckankel@nd.edu
Purposely used exit codes:
    0 = clean run, proper execution
    20 = too few or many args
    21 = used -h option
    22 = incorrect hostname
    23 = incorrect arg
    24 = no user-name with -u option
    25 = User not on, or DNE
"""

class Node:
    """Class to hold representation of a node for the CRC 
    Note: Python doesn't have private data, but the direct variables of
    this class are treated as private, and as such there are methods created
    to obtain them."""
    
    def __init__(self, name, total_cores=0, used_cores=0, disabled=True):
        """Instantiation for Node class, must pass in the node name, everything else defaults to 0.
        Node defaults in the disabled state."""
        self.name = name
        self.total_cores = int(total_cores)
        self.used_cores = int(used_cores)
        self.free_cores = (int(self.total_cores) - int(self.used_cores))
        self.disabled = disabled
        self.num_jobs = 0
        self.load = None
        self.job_list = []
        
    def __repr__(self):
        name = self.name
        return name
    
    def __str__(self):
        return self.name
        
    def add_job(self, job):
        """Method to add an instance of class Job to the job_list of a node."""
        self.job_list.append(job)
        self.num_jobs += 1
    
    def set_load(self, load):
        """Method to set the sys-load for a node"""
        self.load= load
        
    def get_load(self):
        """Method to obtain the sys-load info of a node. Returns a str"""
        return str(self.load)
    
    def get_total_mem(self):
        """Returns the total amount of memory a node contains as a STRING"""
        return self.total_mem
    
    def get_used_mem(self):
        """Returns the amount of memory(RAM) a node currently is using as a STRING"""
        return self.used_mem
    
    def get_free_mem(self):
        """Returns the amount of free RAM a node currently is using as a STRING"""
        return self.free_mem
    
    def set_total_mem(self, mem):
        """Method which sets the total memory (RAM) that this certain node has, which is found using qstat -F
        and parsing the node. The amount of total_mem will be stored as an string."""
        self.total_mem = mem
        return
    
    def set_used_mem(self, u_mem):
        """Method to set the amount of used memory (RAM) in a certain node. This info is found by parsing qstat -F.
        The amount of used_mem will be stored as an string."""
        self.used_mem = u_mem
        return
    
    def set_free_mem(self, default=0):
        """Method which sets the amount of free memory. If no amount of memory is specified, the funciton will calculate
        the free memory from the self.total_mem - self.used_mem. Thus, it is important to set those first. If an amount of
        memory is speified, that will be stored instead. self.free_mem is set as an string."""
        if default == 0:
            self.free_mem = (int(self.total_mem) - int(self.used_mem))
        else:
            self.free_mem = default
        return
    
    def get_num_jobs(self):
        """Method to obtain the number of jobs a node currently has running on it. Returns a str"""
        return str(self.num_jobs)
        
    def set_num_jobs(self, num):
        """Method to set the number of jobs running on a node """
        self.num_jobs = num
    
    def set_name(self, name):
        """Method to set the name of a node"""
        self.name = name
    
    def get_name(self):
        """Method to retrieve a node's name"""
        return self.name
    
    def get_free(self):
        """Method to retrieve the node's # of free cores"""
        return int(self.free_cores)
    
    def get_job_list(self):
        """Method to obtain the job-list of a node"""
        return self.job_list
    
    def get_used(self):
        """method to retrive a node's # of used cores"""
        return int(self.used_cores)
    
    def get_total(self):
        """Method to retrieve a node's # of total cores"""
        return int(self.total_cores)
    
    def set_cores(self, total_cores, used_cores):
        """Method to set all of the core information on a node. Just needs the total
        and the used cores, it will determine the number of free cores."""
        self.total_cores = int(total_cores)
        self.used_cores = int(used_cores)
        self.free_cores = int(total_cores) - int(used_cores)
        
    def set_disabled_switch(self, disabled):
        """Method to set whether or not the node is disabled. The parameter 'disabled'
        is a bool, so True or false or the equivilent ( 0 or 1 )"""
        self.disabled = disabled
        
    def get_disabled_switch(self):
        """Method to obtain the disable bool from a node"""
        return self.disabled
#^--------------------------------------------------------- class Node

class User:
    """Class to hold representation of a user recognized by UGE."""
    
    def __init__(self, name, jobs=[],cores_used=0):
        """Default instantiation for a user. Only need the name, everything else defaults
        to empty or 0."""
        
        self.name = str(name)
        self.job_list = jobs
        self.cores_used = cores_used
        self.node_list = []
        
    def __repr__(self):
        return 'User-{0}'.format(self.name)
    
    def __str__(self):
        return self.name
    
    def get_name(self):
        """Method to obtain name of user."""
        return self.name
    
    def get_job_list(self):
        """Method to obtain the job list of a user."""
        return self.job_list
    
    def get_core_info(self):
        """Method to obtain core info on a user."""
        return self.cores_used
    
    def update_cores(self):
        """Method to update the total number of cores a user has allocated to them, by checking the cores
        used in their job list. So this should be run once completed adding all of the user's jobs."""
        num_cores = 0
        for job in self.job_list:
            num_cores += int(job.get_core_info())
        self.cores_used = num_cores
        return
    
    def get_node_list(self):
        """Method to obtain node_list of a user. The node_list is a list of the different nodes
        a user has jobs running on. May come in handy if a user page is created."""
        return self.node_list
        
    def add_job(self, job):
        """Method to add a job to the users job list, this job must be an instance of class Job!"""
        self.job_list.append(job)
        return
#^--------------------------------------------------------- class User

class Job:
    """Class to hold representation of a job in a specific node for the CRC."""
    
    def __init__(self, name, user, cores=0):
        """Default instantiation for a Job. Only need the name, and user everything else defaults
        to empty or 0."""
        self.name = str(name)
        self.cores = cores
        self.user = str(user)
        self.priority = 0
        self.id = 0
        self.max_mem = 'NA'
        return
        
    def __repr__(self):
        return 'Job-{0}'.format(self.name)
    
    def __str__(self):
        return self.name
    
    def get_name(self):
        """Method to obtain name of user."""
        return self.name
    
    def set_cores(self, cores):
        """Method to set the number of cores a job uses."""
        self.cores = cores
        return
    
    def get_core_info(self):
        """Method to obtain core info on a user."""
        return self.cores
    
    def get_priority(self):
        """Method to obtain the priority of a job. Returns a str"""
        return str(self.priority)
    
    def set_priority(self, pri):
        self.priority = pri
        return
    
    def get_user(self):
        """Method to obtain the user behind the job itself."""
        return self.user
    
    def get_id(self):
        """Method to get job id of a job"""
        return self.id
    
    def get_start_time(self):
        """Function to obtain the start time of a running job. Will leverage qstat's -j flag."""
        # Searching through qstat and grabbing only the start time. Lot of weeding out.
        qstat = subprocess.getoutput("qstat -j {0}".format(self.id))
        qstat = qstat[qstat.find("start_time"):]
        qstat = qstat[:qstat.find('\n')]
        return qstat[28:]
    
    def find_max_mem(self):
        """Function that will find this job's maximum used memory (RAM) by parsing
        through qstat -j <job_id>. The function will set this Job object's max_mem
        variable."""
        qstat = subprocess.getoutput("qstat -j {0}".format(self.id))
        qstat = qstat[qstat.find("maxvmem=") + 8 :]
        self.max_mem = qstat[:qstat.find('\n')]
    
    def get_max_mem(self):
        """Function to return a STRING of the maximum memory a job as used thus far detected
        by the grid engine."""
        return str(self.max_mem)
    
    def set_id(self, job_id):
        self.id = job_id
        self.find_max_mem()
        return
#^--------------------------------------------------------- class Job

class Pending(Job):
    """Class to represent a Pending job in the SGE pending job-list. Class is child of Job class."""
    
    def set_status(self, status):
        """Method which sets the waiting status of the job. In qstat -f, hqw is error waiting, which will
        become 'Error' here, and qw is simply waiting turn, which will be 'Waiting' here. """
        if status == 'qw':
            status = 'Waiting'
        elif status == 'hqw':
            status = 'Held'
        elif status == 'Eqw':
            status = 'Error'
        else:
            sys.exit(20)
        self.status = status
        return
        
    def get_status(self):
        """Method to obtain the waiting status of a pending job."""
        return self.status
    
    def set_date(self, date):
        """Method to set the date which the job entered the pending state."""
        self.date = date
        return
    
    def get_date(self):
        """Method I wish was made a long time ago."""
        return self.date
#^--------------------------------------------------------- class Pending(Job)


def main():
    """Main will parse through cmdline args, and give the result to the proper function. The debug
    queue is very simple to do on its own so it has its own function."""
    global TERMWIDTH, PRINT_INDENT, DEBUG_QUEUE_HOSTGROUP, GENERAL_ACCESS_QUEUE_HOSTGROUP
    
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Error: Too few or too many arguments.")
        show_usage(20)
    
    if (sys.argv[1] == '-d' or sys.argv[1] == '--debug'):
        desired_host = DEBUG_QUEUE_HOSTGROUP
    elif (sys.argv[1] == '-g' or sys.argv[1] == '--general_access'):
        desired_host = GENERAL_ACCESS_QUEUE_HOSTGROUP
    elif (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        show_usage(21)
    elif (sys.argv[1] == '-Mordor' or sys.argv[1] == '--Mordor'):
        print("One does not simply view Mordor. . .")
        show_usage(23)
    elif sys.argv[1] == '-u' or sys.argv[1] == '--user':
        if len(sys.argv) < 3:
            print("Error: Missing user-name.")
            show_usage(24)
        else:
            process_user(sys.argv[2])
    elif (sys.argv[1] == '-a' or sys.argv[1] == '--all'):
        if len(sys.argv) > 3:
            print('Argument Error. To see info on every host group just type "node_search.sh --all" or use "-a".')
            show_usage(23)
        desired_host = "all"
    elif sys.argv[1] == '-uf':
        if len(sys.argv) < 3 or len(sys.argv) > 4:
            print('Error: Incorrect Arg usage.')
            show_usage(20)
        elif len(sys.argv) == 4:
            if sys.argv[3] == '--details':
                find_host_groups(sys.argv[2], True, False)
        else:
            find_host_groups(sys.argv[2], False, False)
    elif sys.argv[1] == '-qlong':
        if (len(sys.argv)) != 2:
            print("Error: Too many arguments!") 
            show_usage(20)
        else:
            find_host_groups(os.environ['USER'], False, True)
            
    elif sys.argv[1] == '-j':
        if (len(sys.argv)) > 4 or (len(sys.argv)) < 3:
            print("Error: Incorrect argument number.")
            show_usage(20)
        else:
           process_id(sys.argv[2]) 
        
    elif sys.argv[1] == '-U':
        if len(sys.argv) != 2:
            print("Error: Too many args, you can't use --details with -U!")
            show_usage(20)
        else:   
            show_users()
    elif sys.argv[1] == '--low_efficiency' or sys.argv[1] == '-l_e':
        if len(sys.argv) > 2:
            print('Error: Too many args.')
            show_usage(20)
        else:
            show_efficiency()
    elif '-' not in sys.argv[1]:
        print("Error: Incorrect arg ussage")
        show_usage(23)
    elif sys.argv[1] == "-all":
        print("Did you mean, '--all'?")
        show_usage(20)
    elif (sys.argv[1] == '-H' or sys.argv[1] == '--hosts'):
        if len(sys.argv) > 2:
            print("Error: Too many args, you can't use --details with -H!")
            show_usage(20)
        show_hosts()
    else:
        desired_host = str(sys.argv[1][1:]) #getting rid of '-'
    
    valid_hosts = (subprocess.getoutput("qconf -shgrpl").split())

    if desired_host == DEBUG_QUEUE_HOSTGROUP or desired_host == GENERAL_ACCESS_QUEUE_HOSTGROUP or \
       desired_host == "all":
        process_host(desired_host)
    else:
        if ('@' + str(desired_host)) not in valid_hosts: #need a '@' for host list
            print("Error: Incorrect/bad hostname")
            show_usage(22)
        process_host(desired_host)
    sys.exit()
#^----------------------------------------------------------------------------- main()   
 
def find_host_groups(user_name, detail_switch, queue_switch):
    """Method to find the host groups that a given user belongs to. Username is passed in,
    and method will send needed info to the respective printing functions depending if it is
    a detailed print or not. Program exits after executing this method."""
    
    # Ensure user is a crc user (check /etc/passwd)
    try:
        user_pwd = getpwnam(user_name)
    except KeyError:
        print("Error: User {0} is not recognized.".format(user_name))
        sys.exit(25)

    all_user_lists = subprocess.getoutput("qconf -sul").split('\n')
    
    user_list = []
    #Going through each element of all_user_lists and finding detailed output for that element
    for ul in all_user_lists:
        u_list = subprocess.getoutput("qconf -su " + ul)
        if u_list.find(user_name) != (-1):
            user_list.append(ul)
            
    #sq = subprocess.getoutput("qconf -sq long")
    #
    ##splicing the sq output up to the user_list point, we don't need the rest of the garbarge before that
    #sq = sq[sq.find('user_lists') + 9 :sq.find('xuser')]
    #sq = (((sq.replace('\n', '')).replace(' ', '')).replace('\\', '')).replace('],', '')
    #host_user_list = []
    #sq = sq.split('[')
    #hostg_list = []
    #for line in sq:
    #    if line.find('@') != (-1):
    #        #host-groups in sq output have '@', so that's what we're looking for
    #        hostg_list.append(line)
    #for line in hostg_list:
    #    for ul in user_list:
    #        if ul in line:
    #            host_user_list.append(line.split('=')[0])

    queue_list= []
    if queue_switch:
        queue_list = ['long']
    else:
        queue_list = ['long', 'hpc', 'gpu', 'gpu-debug']
        
    host_user_list = []

    # Run through each queue
    for searchQ in queue_list:
        host_user_list = host_user_list + find_queue_usersets(searchQ, user_list)

    # Everyone has access to general access, adding in case of queue_switch
    host_user_list.append('@' + GENERAL_ACCESS_QUEUE_HOSTGROUP)

    if queue_switch:
        process_queue(host_user_list, user_name, user_list)

    # Everyone has access to debug
    host_user_list.append('@' + DEBUG_QUEUE_HOSTGROUP)
    
    if detail_switch:
        print_duser_host(host_user_list, user_name, user_list)
    else:
        print_user_host(host_user_list, user_name, user_list)
    sys.exit()
#^----------------------------------------------------------------------------- find_host_groups(user_name)

def process_id(job_id):
    """Accepts the job id to search for. Parses qstat to find the job associated with the job_id.
    Will parse both qstat's -j flag and searches for the job on xymon. Passes on necessary information
    to print_id function."""



def find_queue_usersets(queue, user_list):
    """Searches through a queue with 'qconf -sq' to find all usersets which are allowed on the hostgroups
    that operate within the specified queue. Takes in the queue to be searched as a string. Returns a list
    of hostgroups from the specified queue which the user belongs to."""

    sq = subprocess.getoutput("qconf -sq {0}".format(queue))
    
    #splicing the sq output up to the user_list point, we don't need the rest of the garbarge before that
    sq = sq[sq.find('user_lists') + 9 :sq.find('xuser')]
    sq = (((sq.replace('\n', '')).replace(' ', '')).replace('\\', '')).replace('],', '')
    host_user_list = []
    sq = sq.split('[')
    hostg_list = []
    for line in sq:
        if line.find('@') != (-1):
            #host-groups in sq output have '@', so that's what we're looking for
            hostg_list.append(line)
    for line in hostg_list:
        for ul in user_list:
            if ul in line:
                host_user_list.append(line.split('=')[0])
    return host_user_list
#^----------------------------------------------------------------------------- find_queue_usersets(user_name)

def print_user_host(host_list, user, ul):
    """Method to print a non-detailed version of the host groups and user-lists a specifed user
    belongs to and is able to use. ul represents a list of the user-list, host_list is a list of the host groups,
    and user would be the username of the specifed user as a string."""
    
    print('\nHost-group info pertaining to {0}:'.format(user))
    print('-'.center(80, '-'))
    if len(ul) == 0:
        print('User is not a member of any user-lists.')
    else:
        print('User belongs to the following user-lists:')
        for u in ul:
            print(u)
        print()
    print('User has access to the following host-groups:')
    for hg in host_list:
        print(hg)
    print('-'.center(80, '-') + '\n')
    return
#^----------------------------------------------------------------------------- print_user_host(host_list, user, ul)

def print_duser_host(host_list, user, ul):
    """Method to print a detailed version of the hosts available to the specified user. This function will
    print the 'qconf -shgrp_tree' of all of the hosts the user is able to use. That means the host along with what
    nodes belongs to it will be displayed. 'ul' is the user_list, technically it is a list of user_lists in qconf's
    terms."""
    
    header = ('Host group information pertaining to: {0}.\n' + '-'.center(TERMWIDTH, '-') + '\n' + \
    'There are {1} different host groups available to {0}.').format(user, str(len(host_list)))
    
    if len(ul) == 0:
        content = 'User {0} does not belong to any user-lists.'.format(user) + '\n'
    else:
        content = 'User-lists:'
        for u in ul:
            content += '\n{0}\n'.format(u)
    content += '-'.center(TERMWIDTH, '-') + '\n'
    
    for host in host_list:
        content += subprocess.getoutput('qconf -shgrp_tree ' + host ) + '\n'
        
    print(header)
    print(content)
    return
#^----------------------------------------------------------------------------- print_duser_host(host_list, user, ul)
   
def show_hosts():
    """Function that displays all available hosts and exists. Best to be piped through less etc."""
    valid_hosts = (subprocess.getoutput("qconf -shgrpl").split())
    for host in valid_hosts:
        print(host)
    sys.exit()
#^----------------------------------------------------------------------------- show_hosts()

def process_queue(host_user_list, user_name, user_list):
    """Process the long queue for the user who's environment this is running in. Accepts
    the results from find_host_groups. Will run through process_host for every hostgroup
    this user has access to through the long queue."""

    total_nodes = 0
    total_cores = 0
    disabled_cores = 0
    used_cores = 0
    free_cores = 0
    empty_nodes = 0
    disabled_nodes = 0
 
    node_strings= []

    for hostgroup in host_user_list:
        # Obtain totals for one hostgroup, and contine a summation
        tc, uc, tn, en, dc,dn, nl = process_host(hostgroup.replace('@',''))

        # Do not want to recount same nodes. This needs to be looked at for efficiency.
        nl_strings = [n.name for n in nl]

        if nl_strings[0] in node_strings:
            continue

        # Sum to get totals for whole queue which user has access to
        total_cores += tc 
        used_cores += uc 
        total_nodes += tn
        empty_nodes += en
        disabled_cores += dc
        disabled_nodes += dn
        node_strings= node_strings + nl

    # Send totals to be printed to screen
    print_host_info(total_cores, used_cores, total_nodes, empty_nodes, "Long Queue", disabled_cores, 
                    disabled_nodes)
    sys.exit(0)
#^----------------------------------------------------------------------------- process_queue(...)

def process_host(desired_host):
    """Processes the desired host whether thats long or any host group. Will gather info on
    all of that group's nodes and send them to the print_host_info() function."""
    
    node_list = []
    host_info_list = []    
    if desired_host == "all":
        desired_host_list = getAllMachines()
    else:
        desired_host_list = (subprocess.getoutput("qconf -shgrp_resolved " + '@' + str(desired_host))).split()
    qstat = subprocess.getoutput('qstat -f')
    for host in desired_host_list:
        if qstat.find(host) != (-1):
            #Searches the long string for the index of the occurance of the specified host, then
            #parses it the string for just that one line with the host that we want.
            host_info_list.append((qstat[qstat.find(host):].split('\n'))[0])
    #Start at with everything at 0, and will count up as encountered.
    total_nodes = 0
    total_cores = 0
    disabled_cores = 0
    used_cores = 0
    free_cores = 0
    empty_nodes = 0
    disabled_nodes = 0
    for host in host_info_list:
        #simply gathering info qstat spat out for us
        temp_node = Node((host.split()[0]))
        cores = host.split()[2].replace('/', ' ').split()
        host_used_cores = cores[1]
        host_total_cores = cores[2]
        if len(host.split()) == 6 and (host.split()[5] == 'd' or host.split()[5] == 'E' or \
               host.split()[5] == 'au' or host.split()[5] == 'Eau' or host.split()[5] == 'Eqw' \
               or host.split()[5] == 'adu'):
            temp_node.set_disabled_switch(True)
            disabled_cores += int(host_total_cores)
            total_cores += int(host_total_cores)
            disabled_nodes += 1
        else:    
            temp_node.set_disabled_switch(False)
            used_cores += int(host_used_cores)
            total_cores += int(host_total_cores)
            free_cores += int(host_total_cores) - int(host_used_cores)
            if int(host_used_cores) == 0:
                empty_nodes += 1
        temp_node.set_cores(host_total_cores, host_used_cores)
        total_nodes += 1
        node_list.append(temp_node)        
    
    if len(sys.argv) == 3:
        if sys.argv[2] == '--details':
            print_detailed_host(total_cores, used_cores, total_nodes, empty_nodes, desired_host, 
                                disabled_cores, disabled_nodes, node_list)
        elif sys.argv[2] == '-v' or sys.argv[2] == '--visual':
            draw_queue(total_nodes, total_cores, used_cores, empty_nodes, desired_host, disabled_cores, 
                       disabled_nodes, node_list, free_cores)
        else:
            print('Error: Arg syntax error with: ' + sys.argv[2])
            show_usage(23)
    elif sys.argv[1] == "-qlong":
        # Returning values from this host group to the qlong function
        return(total_cores, used_cores, total_nodes, empty_nodes, disabled_cores,disabled_nodes, node_list)
    elif len(sys.argv) < 3:
        print_host_info(total_cores, used_cores, total_nodes, empty_nodes, desired_host, disabled_cores, 
                        disabled_nodes)
    else:
        print('Error: Too many args')
        show_usage(23)
    return
#^----------------------------------------------------------------------------- process_host(desired_host)    

def show_efficiency():
    """Function to find and show machines with low efficiency. Low efficiency is described as
    a machine where all or most of the cores are being used by UGE (not ocndor) jobs, but the CPU usage is very
    low."""

    machineList = getAllMachines() # obtaining all nodes from UGE into a list.

    macString = machineList[0].replace('.crc.nd.edu','') # priming the machine list.
    for mac in machineList[1:]: # Going through all but the first machine in machineList
        mac = mac.replace('.crc.nd.edu','')
        macString += ("," + mac) # Making the string comma separated
    qh = subprocess.getoutput('qhost -h {0}'.format(macString))

    qstat = subprocess.getoutput('qstat -f').split('-'.center(81, '-')) #81 -'s, grabbing results of qstat to wade through
    pending_search = '#'.center(79, '#') #denotes pending jobs in qstat 79 #'s

    lowEffNodes = []
    for node in qh.split('\n')[3:]: # Skipping lines that aren't nodes
        ns = node.split()
        if len(ns) < 7:
            continue # Skipping if it's a mistake
        if ns[6] != '-' and float(ns[6]) < LOWTHRESHOLD : # Not including machines that are turned off
            #lowUsageNodes.append({'NAME': ns[0], "LOAD": ns[6]}) #appending the string name of the nodes with low CPU usage
            for nd in qstat:
                if ns[0] in nd: # ns[0] == name of node
                    if pending_search in nd: #Taking pending jobs out
                        if ".crc.nd.edu" in nd:
                            # Reap out the node text before the pending search and keep it as a node, ditch the rest of pending jobs
                            continue
                        else:
                            # ignore it
                            continue
                    cores = nd.split()[2][nd.split()[2].find('/')+1:]
                    usedCores = cores[:cores.find('/')]
                    totalCores = cores[cores.find('/')+1:]
                    if usedCores != totalCores:
                        continue
                    else:
                        splitNode = nd.lstrip().split('\n') # We want one more value than there really is for the for loop to work easily
                        tempNode = Node(splitNode[0].split()[0].replace('long@','').replace('gpu-debug@','')\
                                .replace('debug@','').replace('gpu@','').replace('.crc.nd.edu',''),
                                totalCores,usedCores, False) # Creating node for this low efficiency node
                        tempNode.set_load(ns[6])
                        num_jobs = len(splitNode) -1
                        for x in range(1, num_jobs):
                            jobSplit = splitNode[x].split() # splitting the job itself into a list to easily grab what we need
                            tempJob = Job(jobSplit[2], jobSplit[3], jobSplit[7]) # Creating a Job to be added.
                            tempJob.set_id(jobSplit[0])
                            tempNode.add_job(tempJob) # appending this job to the node's jobList

                        lowEffNodes.append(tempNode) # adding the tempNode to the final list of low_efficiency nodes


    # Printing the header
    print("=".center(80,'='))
    print('=' + '='.rjust(79,' '))
    print('=' + "Low Efficiency Nodes".center(78, " ") + '=')
    print('=' + '='.rjust(79,' '))
    print('='.center(80,'='))
    print("HOSTNAME".ljust(15,' ') + "CPU LOAD".center(15, " "))
    print("    " + "Job ID".ljust(15,' ') + "User".ljust(15,' ') + "Job Name\n")

    # Printing the nodes along with the jobs on those nodes
    for node in lowEffNodes:
        if node.num_jobs >= 1:
            print(node.name.ljust(15,' ') +  node.load.center(15, " "))
            for job in node.get_job_list():
                print("    " + job.id.ljust(15,' ') + job.user.ljust(15, ' ') + job.name)
        print('-'.center(40,'-'))

    #print(qh.split('\n')[2:])

    sys.exit(0)
#^---------------------------------------------------------------------------- show_efficiency(...)

def getAllMachines():
    """Function to get all of the machines UGE can find and return a list of them as strings.
    This takes into account duplicate machines. Will not count machines counted in previous HG's.
    Returns: List of strings."""

    validHosts = (subprocess.getoutput("qconf -shgrpl").split())
    machineList = []
    processedHGList = []
    readNodes = False
    for host in validHosts:
        hostMachineList = ((subprocess.getoutput("qconf -shgrp_tree " + str(host))).split())
        for element in hostMachineList:
            if '@' not in element: # If it is not a HG name
                if element not in machineList:
                    machineList.append(element) # Searching whole list for this node
    machineList.sort()
    return machineList
#^----------------------------------------------------------------------------- getAllMachines()

def draw_queue(total_nodes, total_cores, used_cores, empty_nodes, desired_host, 
                disabled_cores, disabled_nodes, node_list, free_cores):
    """Method to draw the queue on the screen. Will use '[]' to represent a core.
    Returns: Nothing, draws to stdout."""
    
    if total_cores > 400:
        screen_size = 119
        cores_per_row = 39
    else:
        screen_size = 100
        cores_per_row = 30
    
    o_core = '[O]'
    u_core = '[~]'
    dis_core = '[#]'
    print('{0} Queue'.format(str(desired_host)).center(screen_size))
    print('-'.center(screen_size,'-'))
    print('Total Cores:'.ljust(int(screen_size/2)), end="")
    print('{0}'.format(str(total_cores)).ljust(int(screen_size/2)))
    print('Used Cores:'.ljust(int(screen_size/2)), end="")
    print('{0}'.format(str(used_cores)).ljust(int(screen_size/2)))
    print('Free Cores:'.ljust(int(screen_size/2)), end="")
    print('{0}'.format(str(free_cores)).ljust(int(screen_size/2)))
    print('Disabled/Error Cores:'.ljust(int(screen_size/2)), end="")
    print('{0}'.format(str(disabled_cores)).ljust(int(screen_size/2)))
    print('Total Nodes:'.ljust(int(screen_size/2)),end ="")
    print('{0}'.format(str(total_nodes)).ljust(int(screen_size/2)))
    print('-'.center(screen_size, '-'))
    print(('[0] = Open Core' + PRINT_INDENT + '[~] = Used Core' + PRINT_INDENT + \
           '[#] = Disabled/Err Core').center(screen_size) + '\n')
    
    #Drawing representation of the Queue
    drawn_cores = 0
    for node in node_list:
        if node.get_disabled_switch():
            for i in range(1, node.total_cores +1):
                print(dis_core, end="")
                drawn_cores += 1
                if drawn_cores == cores_per_row:
                    drawn_cores = 0
                    print('')
            continue
        if node.get_free():
            for i in range(1, (node.free_cores) +1):
                print(o_core, end="")
                drawn_cores += 1
                if drawn_cores == cores_per_row:
                    drawn_cores = 0
                    print('')
        if node.get_used():
            for i in range(1, (node.used_cores) +1):
                print(u_core, end="")
                drawn_cores += 1
                if drawn_cores == cores_per_row:
                    drawn_cores = 0
                    print('')
    print('\n' + '-'.center(screen_size,'-'))
    return
#^----------------------------------------------------------------------------- draw_queues(. . .)

def print_detailed_host(total_cores, used_cores, total_nodes, empty_nodes, desired_host, 
                        disabled_cores, disabled_nodes, node_list):
    """Prints detailed version of the designated host. Will print every node along with the totals.
    Return: Nothing, writes to stdout."""
    
    print('\nDetailed info pertaining to: ' + desired_host)
    print('Total Nodes: {0}'.format(str(len(node_list)))) 
    print('Total Cores : {0}'.format(total_cores) + PRINT_INDENT + 'Used Cores: {0}'.format(used_cores)
          + PRINT_INDENT + 'Free Cores: {0}'.format(str(total_cores - used_cores - disabled_cores)) 
          + PRINT_INDENT + 'Disabled Cores: {0}'.format(disabled_cores))
    print('\nThe following is a list of each node within {0}:\n'.format(desired_host))
    print('Node name'.ljust(int(TERMWIDTH/2)) + 'Used Cores/Total Cores')
    for node in node_list:
        cores = str(node.get_used()) + '/' + str(node.get_total())
        if node.get_disabled_switch():
            disabled = 'Unavailable'
        else:
            disabled = ''
        print((PRINT_INDENT + node.get_name()).ljust(int(TERMWIDTH/2)) + PRINT_INDENT + (str(cores).rjust(5,' ') \
        + PRINT_INDENT + disabled))
    return
#^----------------------------------------------------------------------------- print_detailed_host(. . .)
    
def print_host_info(total_cores, used_cores, total_nodes, empty_nodes, desired_host, 
                    disabled_cores, disabled_nodes):
    """Prints the information from the process_host function in a pretty* format"""
    
    print(str(desired_host).ljust(TERMWIDTH))
    print('-'.center(60, '-'))
    print('Total Cores:'.ljust(int(TERMWIDTH/2)) + str(total_cores).ljust(int(TERMWIDTH/2)))
    print('Used Cores:'.ljust(int(TERMWIDTH/2)) + str(used_cores).ljust(int(TERMWIDTH/2)))
    print('Free Cores:'.ljust(int(TERMWIDTH/2)) + str(total_cores - used_cores - disabled_cores).ljust(int(TERMWIDTH/2)))
    print('Disabled/Error Cores:'.ljust(int(TERMWIDTH/2)) + str(disabled_cores).ljust(int(TERMWIDTH/2)))
    print("")
    print('Total Nodes:'.ljust(int(TERMWIDTH/2)) + str(total_nodes).ljust(int(TERMWIDTH/2)))
    print('Used Nodes:'.ljust(int(TERMWIDTH/2)) + str(total_nodes - empty_nodes - disabled_nodes).ljust(int(TERMWIDTH/2)))
    print('Disabled/Error Nodes:'.ljust(int(TERMWIDTH/2)) + str(disabled_nodes).ljust(int(TERMWIDTH/2)))
    print('Empty Nodes:'.ljust(int(TERMWIDTH/2)) + str(empty_nodes).ljust(int(TERMWIDTH/2)))
    return
#^----------------------------------------------------------------------------- print_host_info(. . .)

def show_users():
    """Will display users currently detected by the Univa Grid Engine (qconf)"""
    user_list = subprocess.getoutput("qconf -suserl").split('\n')
    for user in user_list:
        print(user)
    sys.exit()
#^----------------------------------------------------------------------------- show_users()

def process_user(user_name):
    """Function to process the username given after -u option. Will find information pertaining to the specified
    user and send them to the printing function."""
    
    try:
        user_pwd = getpwnam(user_name)
    except KeyError:
        print('Error: User {0} is not recognized.'.format(user_name))
        sys.exit(25)
    
    qstat = subprocess.getoutput("qstat -f").split('-'.center(81, '-')) #81 -'s
    
    node_list = []
    pending_jobs = ''
    pending_search = '#'.center(79, '#') #denotes pending jobs in qstat 79 #'s
    #Weeding out nonessential nodes
    for node in qstat:
        if user_name in (node.split()):
            if pending_search in node: #Taking pending jobs out
                if ".crc.nd.edu" in node:
                    # This means its the last node. We must only accept up tp the pending jobs ONLY. Below we are doing that and taking out an
                    # Additional newline by stripping it but adding one back in to keep formatting correct. (there were two instead of one).
                    tempNode = (node[:node.find(pending_search)].rstrip())+'\n'
                    if user_name in tempNode:
                        node_list.append(tempNode)
                pending_jobs += (node[node.find(pending_search):]) #reaping pending jobs
            else:
                node_list.append(node)
    
    final_list = []
        
    numU_jobs = 0 # Will hold the number of jobs attributed to the specified user
    numU_cores = 0 # The number of cores the user is currently using. Starts at 0 and counts up as jobs encountered.
    
    for host in node_list:
        # Grabbing the node's name in qstat and making a Node() instance of it
        temp_node = Node((host.split()[0]))
        host_used_cores = host.split()[2].split('/')[1]
        host_total_cores = host.split()[2].split('/')[2]
        # If within the first line of the node there is a 'd' at the end, disable it
        if len(host.split('\n')[0]) == 6 and host.split()[5] == 'd':
            temp_node.set_disabled_switch(True)
            disabled_cores += int(host_total_cores)
        else:    
            temp_node.set_disabled_switch(False)
            
        temp_node.set_cores(host_total_cores, host_used_cores)
        # In qstat -F, qf:min_cpu . . . . is the last item before the jobs are listed, 
        # 28 is how many char's that string is (don't want it)
        node_stat= host[host.find('qf:min_cpu_interval=00:05:00') + 28\
                             :host.find('\n---------------------------------------------------------------------------------\n')]
        """Possibly do a host.split('\n') and join the rest of 2 - end"""

        # There is always an extra '\n' in here, so subtract 1 to get rid of it
        num_jobs = len(node_stat.split('\n')) -1
        # If there are any jobs, parse them and gather info
        if num_jobs > 0:
            # Python is non-inclusive for the right operand, and we want to 
            # skip another extra '\n' so start at 1, and want to go num_jobs
            for i in range(1, num_jobs + 1):
                info = node_stat.split('\n')[i].split()
                temp_job = Job(info[2], info[3], info[7])
                temp_job.set_id(info[0])
                temp_job.set_priority(info[1])
                temp_node.add_job(temp_job)
                if info[3] == user_name:
                    numU_jobs += 1 #info[3] is the user-name of job, if == spec. user, increment user_jobs
                    numU_cores += int(info[7]) # info[7] is the number of cores occupied by the user's job
        
        final_list.append(temp_node)
    
    pending_list = []
    if len(pending_jobs): #As long as the user has pending jobs T if len != 0
        p_lines = pending_jobs.split('\n')
        pending_list.append((p_lines[0] + '\n' + p_lines[1] + '\n' + p_lines[2] + '\n'))
        for i in range(3, len(p_lines)):
            if p_lines[i].find(user_name) != (-1):
                pending_list.append(p_lines[i])
         
    if len(sys.argv) == 4:
        if sys.argv[3] == '--details':
            print_detailed_user(final_list, pending_list, user_name, numU_jobs, numU_cores)
        else:
            print('Error: Arg syntax error with: ' + sys.argv[3])
            show_usage(23)
    else:
        print_short_user(final_list, pending_list, user_name, numU_jobs, numU_cores)
#^----------------------------------------------------------------------------- process_user(user_name)
 
def print_detailed_user(node_list, pending_list, user_name, user_jobs, num_cores):
    """Prints detailed version, as in all of the nodes the specified user's jobs are in along with the 
    processes spawned that are owned by the specified user. Will also print all of user's pending jobs(if any).
    Upon completion, will exit."""
    
    user_pend = []
    if len(pending_list):    
        for j in range(1, len(pending_list)):
            user_pend.append(pending_list[j])
    
    print("=".center(TERMWIDTH,"="))
    print("=".ljust(TERMWIDTH - 1) + "=")
    print("=" + ("Detailed Process information for {0}."\
                .format(user_name)).center(TERMWIDTH - 2) + "=")
    print("=".ljust(TERMWIDTH - 1) + "=")
    print("=".center(TERMWIDTH, '=') + "\n")

    print("{0}'s total number of running jobs on UGE: {1}\n".format(user_name, user_jobs))
    # Getting every process of the user to print
    for node in node_list:
        user_proc_list = []
        cleanName = str(node).replace('long@','').replace('debug@','').replace('.crc.nd.edu','').replace('gpu@','').replace('gpu-debug@','')
        full_page = urllib.request.urlopen("https://mon.crc.nd.edu/xymon-cgi/svcstatus.sh?HOST={0}.crc.nd.edu&SERVICE=cpu".format(cleanName))
        mybytes = full_page.read() # getting all html into a byte-list
        pageStr = mybytes.decode("utf8") # Now the html is in a string
        full_page.close()
        del mybytes #releasing these
        del full_page
        # Each line below will be a line in Top for processes
        userNodeMem = [] # List to hold the different amounts of memory a user is using on this node!
        for line in pageStr.split('\n'):
            if user_name in line:
                lineSplit = line.split()
                memCheck = lineSplit[5] # used to check quality of memory string (check for m's, t's, or g's)
                tmp_user_list = {}
                lineSplit = line.split()
                tmp_user_list["PID"] = lineSplit[0]
                tmp_user_list["RESMEM"] = cleanMem(memCheck)
                tmp_user_list["CPU%"] = lineSplit[8]
                tmp_user_list["TIME"] = lineSplit[10]
                tmp_user_list["PNAME"] = lineSplit[11]
                user_proc_list.append(tmp_user_list)
                if ('t' in memCheck)  or ('g' in memCheck) or ('m' in memCheck): # this is what contains the amount of resident memory
                    userNodeMem.append(toKB(memCheck))
                else:
                    userNodeMem.append(memCheck) # we want it in KB to add up after finished running through node


        # Printing process information that pertains to the current user only.
        print(cleanName + ("Cores Used / Total Cores : " + str(node.used_cores) + "/" + str(node.total_cores)).rjust(int(TERMWIDTH/2)))
        print('-'.center(TERMWIDTH,"-"))
        print('PID'.center(10, ' ') + 'ProcName'.center(20, ' ') + 'Memory Used'.center(20) + 'CPU%'.center(10) + 'TIME'.center(16))
        for proc in user_proc_list:
            print(proc['PID'].center(10) + proc['PNAME'].center(20) + proc['RESMEM'].center(20) + proc['CPU%'].center(10) + proc['TIME'].center(16))
        userTotalMem = 0
        for mem in userNodeMem:
            userTotalMem += int(mem)  
        print("User's total memory usage on Node: {0}".format(cleanMem(str(userTotalMem))))
        print("Total number of processes owned by user on Node: {0}".format(str(len(user_proc_list))))
                
        print('') # Simple newline

    if len(user_pend):
        print('\n' + '#'.center(TERMWIDTH, '#'))
        print("{0}'s pending jobs:".format(user_name).center(TERMWIDTH))
        print('#'.center(TERMWIDTH, '#'))
        for job in user_pend:
            print(job)
    sys.exit()
#^----------------------------------------------------------------------------- print_detailed_user(. . .)

def toKB(badMem):
    """Function which accepts a string representing resident memory from top off of a node. badMem will contain
    a t for terabytes, m for megabytes, or a g for gigabytes. These will be translated into KB and returned so the total
    amount of memory can be calculated for a user on a node."""

    if 't' in badMem:
        badMem = badMem.replace('t','')
        badMem = float(badMem) * 1000000000
        return badMem
    elif 'g' in badMem:
        badMem = badMem.replace('g','')
        badMem = float(badMem) * 1000000
        return badMem
    elif 'm' in badMem:
        badMem = badMem.replace('m','')
        badMem=float(badMem) * 1000
        return badMem
    else:
        # Error???
        print("\nERROR: Cannot determine memory in function badMem with memory of: {0}\nExiting....\n".format(badMem))
        sys.exit()
#^----------------------------------------------------------------------------- toKB(badMem)

def cleanMem(badMem):
    """Function which accepts a string which is the memory of a process from top. These are in KB or in t for terabyte.
    These will be transformed into human readable memory units like MB and GB to easily understand them. Returns:
    a string which holds the human readable memory amount."""

    if len(badMem) > 3 and len(badMem) <= 6 and ('t' not in badMem) and ('g' not in badMem) and ('m' not in badMem):
        return (str( float(badMem) / 1000.0) + ' MB') # Moving decimal point over 3 times and adding MB
    elif 'm' in badMem:
        return badMem.replace('m', ' MB')
    elif len(badMem) > 6 and ('t' not in badMem ) and ('g' not in badMem):
        return (str( float(badMem) /1000000.0) + ' GB')
    elif 't' in badMem:
        badMem = badMem.replace('t','') # removing the t from terabyte
        return (str(float(badMem)*1000) + ' GB')
    elif 'g' in badMem:
        return badMem.replace('g', ' GB')
    else:
        # The true usage must be in KB, so add that
        return badMem + ' KB'
#^----------------------------------------------------------------------------- cleanMem(string:badmem)

def print_short_user(node_list, pending_list, user_name, user_jobs, num_cores):
    """Prints a short version of the user details: the node the user is running on with their jobs, and the
    user's pending jobs (if any)."""
    
    user_pend = []
    if len(pending_list):    
        for j in range(1, len(pending_list)): # Skipping first, as its a print header and not job.
            user_pend.append(pending_list[j])

    job_count = 0
    print("=".center(TERMWIDTH,"="))
    print("=".ljust(TERMWIDTH - 1) + "=")
    print("=" + ("Job information for {0}."\
                .format(user_name)).center(TERMWIDTH - 2) + "=")
    print("=".ljust(TERMWIDTH - 1) + "=")
    print("=".center(TERMWIDTH, '=') + "\n")
    for node in node_list:
        print()
        user_proc_list = []
        cleanName = str(node).replace('long@','').replace('debug@','').replace('.crc.nd.edu','').replace('gpu@','').replace('gpu-debug@','')
        full_page = urllib.request.urlopen("https://mon.crc.nd.edu/xymon-cgi/svcstatus.sh?HOST={0}.crc.nd.edu&SERVICE=cpu".format(cleanName))
        mybytes = full_page.read() # getting all html into a byte-list
        pageStr = mybytes.decode("utf8") # Now the html is in a string
        full_page.close()
        del mybytes #releasing these
        del full_page
        # Each line below will be a line in Top for processes
        userNodeMem = [] # List to hold the different amounts of memory a user is using on this node!
        for line in pageStr.split('\n'):
            if user_name in line:
                lineSplit = line.split()
                memCheck = lineSplit[5]
                if ('t' in memCheck)  or ('g' in memCheck) or ('m' in memCheck): # this is what contains the amount of resident memory
                    userNodeMem.append(toKB(memCheck))
                else:
                    userNodeMem.append(memCheck) # we want it in KB to add up after finished running through node

        print(node.get_name().ljust(int(TERMWIDTH/2)) + ('Core Usage: ' + (str(node.get_used())) + '/' + (str(node.get_total()))).rjust(int(TERMWIDTH/2)))
        print('-'.center(int(TERMWIDTH) -1, '-')) #Creating line of separation

        print('Job ID'.center(int(TERMWIDTH/4))
              + 'Job Name'.center(int(TERMWIDTH/4))
              + 'Num Cores'.center(int(9))
              + 'Start Time'.center(int(TERMWIDTH/2) - 9))
        for job in node.get_job_list():
            this_nodeJobs = 0
            if user_name in job.get_user():
                print(str(job.get_id()).center(int(TERMWIDTH/4))  \
                    + job.get_name().center(int(TERMWIDTH/4)) +str(job.get_core_info()).center(int(9))\
                    + job.get_start_time().center(int(TERMWIDTH/2) - 9))
                job_count += 1

        userTotalMem = 0
        for mem in userNodeMem:
            userTotalMem += int(mem)  
        print("User's total memory usage on Node: {0}\n".format(cleanMem(str(userTotalMem))))
    print("----\n{0}'s Total Running Jobs: {1}".format(user_name, str(job_count)))
    print("Total cores used: {0}\n".format(num_cores))
        
    if len(user_pend):
        print('\n' + '#'.center(TERMWIDTH, '#'))
        print("{0}'s pending jobs:".format(user_name).center(TERMWIDTH))
        print('#'.center(TERMWIDTH, '#'))
        for job in user_pend:
            print(job)
      
    sys.exit()
#^----------------------------------------------------------------------------- print_short_user(. . .)

def show_usage(exit_code):
    '''Prints usage info, will exit with the corresponding exit code given. See top of script (ln 8).
    Breaks formatting of easily viewing from 118 col terminal, sorry.'''
    
    print("usage: " + SCRIPT_NAME + " [flag] [optional argument]")
    print("Display node information from the Grid Engine".center(80))
    print('Flags:')
    print("  -h, --help".ljust(int(TERMWIDTH/2)) + "show this message and exit.".ljust(int(TERMWIDTH/2)))
    print("  -d, --debug".ljust(int(TERMWIDTH/2)) + "show information from the debug queue.".ljust(int(TERMWIDTH/2)))
    print("  -g, --general-access".ljust(int(TERMWIDTH/2)) + "show information from the general_access queue.".ljust(int(TERMWIDTH/2)))
    print("  -H, --hosts".ljust(int(TERMWIDTH/2)) + "show all available host-groups(you may not have access to all)".ljust(int(TERMWIDTH/2)))
    print("  -[hostgroup]".ljust(int(TERMWIDTH/2)) + "show information on specific host-group, the '@' is not required.".ljust(int(TERMWIDTH/2)))
    print("  -u, --user [user_name] ".ljust(int(TERMWIDTH/2)) + \
          "show which nodes the specified user's jobs are on and job info.".ljust(int(TERMWIDTH/2)))
    print("  -uf, [user_name]".ljust(int(TERMWIDTH/2)) + "show which host-groups are available to specified user.".ljust(int(TERMWIDTH/2)))
    print("  -U".ljust(int(TERMWIDTH/2)) + "show a list of all users currently recognized by the Univa Grid Engine.".ljust(int(TERMWIDTH/2)))
    print("  -qlong".ljust(int(TERMWIDTH/2)) + "display node and core usage of the long queue for the current user.".ljust(int(TERMWIDTH/2)))
    print("Optional arguments:".ljust(int(TERMWIDTH/2)))
    print("  --details".ljust(int(TERMWIDTH/2)) + "flag which can be passed to certain args for a detailed output.".ljust(int(TERMWIDTH/2)))
    print("  -v, --visual".ljust(int(TERMWIDTH/2)) + "flag which can be passed after a host name for a visual queue.".ljust(int(TERMWIDTH/2)) \
          + '\n')
    print('Examples:')
    print('  {0} -d'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)) + '[--debug] could also be used'.ljust(int(TERMWIDTH/2)))
    print('  {0} -g'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)) + '[--general_access] could also be used'.ljust(int(TERMWIDTH/2)))
    print('  {0} -g --details'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)) + ''.ljust(int(TERMWIDTH/2)))
    print('  {0} -u jdoe3 --details'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)) + '[--details] is optional'.ljust(int(TERMWIDTH/2)))
    print('  {0} -uf jdoe3 --details'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)) + '[--details] is optional'.ljust(int(TERMWIDTH/2)))
    print('  {0} -hostgroup'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)))
    print('  {0} -g --visual'.format(SCRIPT_NAME).ljust(int(TERMWIDTH/2)) + '[-v] could also be used.'.ljust(int(TERMWIDTH/2)) + '\n')
    print("Hint: Sometimes it's better to pipe through less.")
    print("{0} [-flags] | less".format(SCRIPT_NAME).center(int(TERMWIDTH)))

    sys.exit(exit_code) 
#^----------------------------------------------------------------------------- show_usage(exit_code)    

def show_everything():
    """Function which will display information on all host groups summed up into a format similiar to the format
    of viewing a single host-group/queue. This function will most likely take a very long time..."""
    
    #print("WARNING: This may take awhile. . .\n")
    # Need to find all hostgroups, and make sure there are no deuplicate machines in this calculation.
    print("This feature is still under construction. Check back soon!")
    sys.exit(0)
#^----------------------------------------------------------------------------- show_everything()    
    

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  main()
