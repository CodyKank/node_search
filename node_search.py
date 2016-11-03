#!/usr/bin/env python3

import sys, subprocess

"""Script to get and report information on nodes withtin the Sun Grid Engine for the CRC at Notre Dame. It uses
the subprocess module to execute bash(tcsh) commands and gather their output. Basically this script is a fancy
swiss army knife parsing tool. Currently works with python 3.4.0. Created July 2016.
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
    """Class to hold representation of a node for the CRC at Notre Dame
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
        self.load = 0
        self.job_list = []
        
    def __repr__(self):
        name = self.name
        return name
    
    def __str__(self):
        return self.name
        
    def add_job(self, job):
        """Method to add an instance of class Job to the job_list of a node."""
        self.job_list.append(job)
    
    def set_load(self, load):
        """Method to set the sys-load for a node"""
        self.load= load
        
    def get_load(self):
        """Method to obtain the sys-load info of a node. Returns a str"""
        return str(self.load)
    
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
    """Class to hold representation of a user in a specific queue for the CRC at Notre Dame."""
    
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
        used in their job list. So this should nbe run once completed adding all of the user's jobs."""
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
    """Class to hold representation of a job in a specific node for the CRC at Notre Dame."""
    
    def __init__(self, name, user, cores=0):
        """Default instantiation for a Job. Only need the name, and user everything else defaults
        to empty or 0."""
        self.name = str(name)
        self.cores = cores
        self.user = str(user)
        self.priority = 0
        self.id = 0
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
    
    def set_id(self, job_id):
        self.id = job_id
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

#Globals
TERMWIDTH = 80
PRINT_INDENT = '    ' #4 spaces, used for formatting.
DEBUG_QUEUE_HOSTGROUP = '@dqcneh'
GENERAL_ACCESS_QUEUE_HOSTGROUP = '@general_access'

def main():
    """Main will parse through cmdline args, and give the result to the proper function. The debug
    queue is very simple to do on its own so it has its own function."""
    global TERMWIDTH, PRINT_INDENT, DEBUG_QUEUE_HOSTGROUP, GENERAL_ACCESS_QUEUE_HOSTGROUP
    
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Error: Too few or too many arguments.")
        show_usage(20)
    if (sys.argv[1] == '-d' or sys.argv[1] == '--debug'):
        desired_host = 'debug'
    elif (sys.argv[1] == '-l' or sys.argv[1] == '--long'):
        desired_host = 'general_access'
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
    elif sys.argv[1] == '-uf':
        if len(sys.argv) < 3 or len(sys.argv) > 4:
            print('Error: Incorrect Arg usage.')
            show_usage(20)
        elif len(sys.argv) == 4:
            if sys.argv[3] == '--details':
                find_host_groups(sys.argv[2], True)
        else:
            find_host_groups(sys.argv[2], False)
    elif sys.argv[1] == '-U':
        if len(sys.argv) != 2:
            print("Error: Too many args, you can't use --details with -U!")
            show_usage(20)
        else:   
            show_users()
    elif '-' not in sys.argv[1]:
        print("Error: Incorrect arg ussage")
        show_usage(23)
    elif (sys.argv[1] == '-H' or sys.argv[1] == '--hosts'):
        if len(sys.argv) > 2:
            print("Error: Too many args, you can't use --details with -H!")
            show_usage(20)
        show_hosts()
    else:
        desired_host = str(sys.argv[1][1:]) #getting rid of '-'
    
    valid_hosts = (subprocess.getoutput("qconf -shgrpl").split())
    if ('@' + str(desired_host)) not in valid_hosts: #need a '@' for host list
        print("Error: Incorrect/bad hostname")
        show_usage(22)
        
    process_host(desired_host)
    sys.exit()
#^----------------------------------------------------------------------------- main()   
 
def find_host_groups(user_name, detail_switch):
    """Method to find the host groups that a given user belongs to. Username is passed in,
    and method will send needed info to the respective printing functions depending if it is
    a detailed print or not. Program exits after executing this method."""
    
    all_user_lists = subprocess.getoutput("qconf -sul").split('\n')
    
    user_list = []
    #Going through each element of all_user_lists and finding detailed output for that element
    for ul in all_user_lists:
        u_list = subprocess.getoutput("qconf -su " + ul)
        if u_list.find(user_name) != (-1):
            user_list.append(ul)
            
    sq = subprocess.getoutput("qconf -sq long")
    
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
    # Manually adding these, as they do not have user_lists associated with them (open to everyone) !!!
    host_user_list.append(DEBUG_QUEUE_HOSTGROUP)
    host_user_list.append(GENERAL_ACCESS_QUEUE_HOSTGROUP)
    
    if detail_switch:
        print_duser_host(host_user_list, user_name, user_list)
    else:
        print_user_host(host_user_list, user_name, user_list)
    sys.exit()
#^----------------------------------------------------------------------------- find_host_groups(user_name)

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

def process_host(desired_host):
    """Processes the desired host whether thats long or any host group. Will gather info on
    all of that group's nodes and send them to the print_host_info() function."""
    
    node_list = []
    host_info_list = []    
    if desired_host == 'debug':
        host_info_list = (subprocess.getoutput("qstat -f | grep debug@")).split('\n')
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
        if len(host.split()) == 6 and host.split()[5] == 'd':
            temp_node.set_disabled_switch(True)
            disabled_cores += int(host_total_cores)
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
            print_detailed_host(total_cores, used_cores, total_nodes, empty_nodes, desired_host, disabled_cores, disabled_nodes, node_list)
        elif sys.argv[2] == '-v' or sys.argv[2] == '--visual':
            draw_queue(total_nodes, total_cores, used_cores, empty_nodes, desired_host, disabled_cores, disabled_nodes, node_list, free_cores)
        else:
            print('Error: Arg syntax error with: ' + sys.argv[2])
            show_usage(23)
    elif len(sys.argv) < 3:
        print_host_info(total_cores, used_cores, total_nodes, empty_nodes, desired_host, disabled_cores, disabled_nodes)
    else:
        print('Error: Too many args')
        show_usage(23)
    return
#^----------------------------------------------------------------------------- process_host(desired_host)    

def draw_queue(total_nodes, total_cores, used_cores, empty_nodes, desired_host, disabled_cores, disabled_nodes, node_list, free_cores):
    """Method to draw the queue on the screen. Will use '[]' to represent a core."""
    
    if total_cores > 400:
        screen_size = 120
        cores_per_row = 40
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
    print('Disabled Cores:'.ljust(int(screen_size/2)), end="")
    print('{0}'.format(str(disabled_cores)).ljust(int(screen_size/2)))
    print('Total Nodes:'.ljust(int(screen_size/2)),end ="")
    print('{0}'.format(str(total_nodes)).ljust(int(screen_size/2)))
    print('-'.center(screen_size, '-'))
    print(('[0] = Open Core' + PRINT_INDENT + '[~] = Used Core' + PRINT_INDENT + '[#] = Disabled Core').center(screen_size) + '\n')
    
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
    print('\n' + '-'.center(100,'-'))
    return
#^----------------------------------------------------------------------------- draw_queues(. . .)

def print_detailed_host(total_cores, used_cores, total_nodes, empty_nodes, desired_host, disabled_cores, disabled_nodes, node_list):
    """Prints detailed version of the designated host. Will print every node along with the totals."""
    
    print('\nDetailed info pertaining to: ' + desired_host)
    print('Total Nodes: {0}'.format(str(len(node_list))) + ' (some may be disabled!)')
    print('Total Cores : {0}'.format(total_cores) + PRINT_INDENT + 'Used Cores: {0}'.format(used_cores)
          + PRINT_INDENT + 'Free Cores: {0}'.format(str(total_cores - used_cores)) )
    print('\nThe following is a list of each node within {0}:\n'.format(desired_host))
    print('Node name'.ljust(int(TERMWIDTH/2)) + 'Used Cores/Total Cores')
    for node in node_list:
        cores = str(node.get_used()) + '/' + str(node.get_total())
        if node.get_disabled_switch():
            disabled = 'd'
        else:
            disabled = ''
        print((PRINT_INDENT + node.get_name()).ljust(int(TERMWIDTH/2)) + PRINT_INDENT + (str(cores).rjust(5,' ') \
        + PRINT_INDENT + disabled))
    return
#^----------------------------------------------------------------------------- print_detailed_host(. . .)
    
def print_host_info(total_cores, used_cores, total_nodes, empty_nodes, desired_host, disabled_cores, disabled_nodes):
    """Prints the information from the process_host function in a pretty* format"""
    
    print(str(desired_host).ljust(TERMWIDTH))
    print('-'.center(TERMWIDTH, '-'))
    print('Total Cores:'.ljust(int(TERMWIDTH/2)) + str(total_cores).ljust(int(TERMWIDTH/2)))
    print('Used Cores:'.ljust(int(TERMWIDTH/2)) + str(used_cores).ljust(int(TERMWIDTH/2)))
    print('Free Cores:'.ljust(int(TERMWIDTH/2)) + str(total_cores - used_cores).ljust(int(TERMWIDTH/2)))
    print('Disabled Cores:'.ljust(int(TERMWIDTH/2)) + str(disabled_cores).ljust(int(TERMWIDTH/2)))
    print("")
    print('Total Nodes:'.ljust(int(TERMWIDTH/2)) + str(total_nodes).ljust(int(TERMWIDTH/2)))
    print('Used Nodes:'.ljust(int(TERMWIDTH/2)) + str(total_nodes - empty_nodes).ljust(int(TERMWIDTH/2)))
    print('Disabled Nodes:'.ljust(int(TERMWIDTH/2)) + str(disabled_nodes).ljust(int(TERMWIDTH/2)))
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
    
    user_list = subprocess.getoutput("qconf -suserl")
    if str(user_name) not in user_list:
        print('Error: User, ' + user_name + ' is currently not logged on or does not exist.')
        sys.exit(25)
    
    qstat = subprocess.getoutput("qstat -f").split('-'.center(81, '-')) #81 -'s
    
    node_list = []
    pending_jobs = ''
    pending_search = '#'.center(79, '#') #denotes pending jobs in qstats 79 #'s
    #Weeding out nonessential nodes
    for node in qstat:
        if user_name in (node.split()):
            if pending_search in node.split(): #Taking pending jobs out
                pending_jobs += (node[node.find(pending_search):]) #reaping pending jobs
            else:
                node_list.append(node)
    
    final_list = []
    for node in node_list:
        lines = node.split('\n')
        temp_str = lines[1] #Keeping node
        for i in range(2, len(lines)):
            if lines[i].find(user_name) != (-1):
                temp_str += '\n'+ str(lines[i])      
        final_list.append(temp_str)
    
    pending_list = []
    if len(pending_jobs): #As long as the user has pending jobs T if len != 0
        p_lines = pending_jobs.split('\n')
        pending_list.append((p_lines[0] + '\n' + p_lines[1] + '\n' + p_lines[2] + '\n'))
        for i in range(3, len(p_lines)):
            if p_lines[i].find(user_name) != (-1):
                pending_list.append(p_lines[i])
         
    if len(sys.argv) == 4:
        if sys.argv[3] == '--details':
            print_detailed_user(node_list, pending_list, user_name)
        else:
            print('Error: Arg syntax error with: ' + args[4])
            show_usage(23)
    else:
        print_short_user(final_list, pending_list, user_name)
#^----------------------------------------------------------------------------- process_user(user_name)
 
def print_detailed_user(node_list, pending_list, user_name):
    """Prints detailed version, as in all of the nodes the specified user's jobs are on along with other
    user's jobs which are running on that node. Will also print all of user's pending jobs(if any)."""
    
    user_pend = []
    if len(pending_list):    
        for j in range(3, len(pending_list)):
            user_pend.append(pending_list[j])
    
    for node in node_list:
        print(node)
    if len(user_pend):
        print('\n' + '#'.center(TERMWIDTH, '#'))
        print("{0}'s pending jobs:".format(user_name).center(TERMWIDTH))
        print('#'.center(TERMWIDTH, '#'))
        for job in user_pend:
            print(job)
    sys.exit()
#^----------------------------------------------------------------------------- print_detailed_user(. . .)

def print_short_user(job_list, pending_list, user_name):
    """Prints a short version of the user details: the node the user is running on with their jobs, and the
    user's pending jobs (if any)."""
    
    # Processing info to be printed in short version. Creating dict with all needed info
    printing_list = []
    for node in job_list:
        temp_dict = {}
        split_node = node.split('\n')
        temp_dict['node'] = (split_node[0]).split()[0]
        temp_dict['cores'] = (split_node[0]).split()[2]
        temp_dict['user'] = user_name
        temp_list = []
        for i in range(1, len(split_node)):
            temp_list.append(split_node[i])
        temp_dict['jobs'] = temp_list
        printing_list.append(temp_dict)
    user_pend = []
    if len(pending_list):    
        for j in range(3, len(pending_list)):
            user_pend.append(pending_list[j])

    job_count = 0
    for item in printing_list:
        job_count += len(item['jobs'])
        
    print('Job information for {0}.{1}Total Jobs: {2}'.format(user_name, PRINT_INDENT, job_count))
    #using dicts just created for printing. Ugly code but decent results.  
    for node in printing_list:
        print()
        print('Node name'.ljust(int(TERMWIDTH/2)) + 'Used Cores'.rjust(int(TERMWIDTH/4)) +
              '  Total Cores'.ljust(int(TERMWIDTH/4)))
        print('-'.center(int(TERMWIDTH), '-')) #Creating line of separation
        print(node['node'].ljust(int(TERMWIDTH/2)) +
              ((node['cores'].replace('/', ' ')).split()[1]).rjust(int(TERMWIDTH/4))
              + '  ' + ((node['cores'].replace('/', ' ')).split()[2]).ljust(int(TERMWIDTH/4)))
        #print('_'.center(TERMWIDTH, '_'))
        print('Jobs on node: ' + str(len(node['jobs'])))
        
        print('{0}Job ID'.format(PRINT_INDENT).ljust(int(TERMWIDTH/4))
              + '{0}Job Name'.format(PRINT_INDENT).ljust(int(TERMWIDTH/4))
              + '{0}Num Cores'.format(PRINT_INDENT).ljust(int(TERMWIDTH/4)))
        for job in node['jobs']:
            print(PRINT_INDENT + job.split()[0].ljust(int(TERMWIDTH/4)) + PRINT_INDENT
                  + job.split()[2].ljust(int(TERMWIDTH/4)) + PRINT_INDENT +job.split()[7].ljust(int(TERMWIDTH/4)))
        
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
    
    print("usage: " + str(sys.argv[0]) + " [flag] [optional argument]")
    print("Display node information from the Grid Engine".center(80))
    print('Flags:')
    print("  -h, --help".ljust(int(TERMWIDTH/2)) + "show this message and exit.".ljust(int(TERMWIDTH/2)))
    print("  -d, --debug".ljust(int(TERMWIDTH/2)) + "show information from the debug queue.".ljust(int(TERMWIDTH/2)))
    print("  -l, --long".ljust(int(TERMWIDTH/2)) + "show information from the long queue.".ljust(int(TERMWIDTH/2)))
    print("  -H, --hosts".ljust(int(TERMWIDTH/2)) + "show all available hosts(you may not have access to all hosts)".ljust(int(TERMWIDTH/2)))
    print("  -[hostname]".ljust(int(TERMWIDTH/2)) + "show information on specific host, the '@' is not required.".ljust(int(TERMWIDTH/2)))
    print("  -u, --user [user_name] ".ljust(int(TERMWIDTH/2)) + "show which nodes the specified user's jobs are on and job info.".ljust(int(TERMWIDTH/2)))
    print("  -uf, [user_name]".ljust(int(TERMWIDTH/2)) + "show which host groups are available to specified user.".ljust(int(TERMWIDTH/2)))
    print("  -U".ljust(int(TERMWIDTH/2)) + "show a list of all users currently recognized by the Univa Grid Engine.".ljust(int(TERMWIDTH/2)))
    print("Optional arguments:".ljust(int(TERMWIDTH/2)))
    print("  --details".ljust(int(TERMWIDTH/2)) + "flag which can be passed after a user or a hostname to specify a detailed output.".ljust(int(TERMWIDTH/2)))
    print("  -v, --visual".ljust(int(TERMWIDTH/2)) + "flag which can be passed after a host name for a visual queue.".ljust(int(TERMWIDTH/2)) + '\n')
    print('Examples:')
    print('  {0} -d'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)) + '[--debug] could also be used'.rjust(int(TERMWIDTH/2)))
    print('  {0} -l'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)) + '[--long] could also be used'.rjust(int(TERMWIDTH/2)))
    print('  {0} --long --details'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)) + '[-l] could also be used'.rjust(int(TERMWIDTH/2)))
    print('  {0} -u johndoe33 --details'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)) + '[--details] is optional'.rjust(int(TERMWIDTH/2)))
    print('  {0} -uf johndoe33 --details'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)) + '[--details] is optional'.rjust(int(TERMWIDTH/2)))
    print('  {0} -corke'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)))
    print('  {0} -l --visual'.format(str(sys.argv[0])).ljust(int(TERMWIDTH/2)) + '[-v] could also be used.'.rjust(int(TERMWIDTH/2)) + '\n')
    print("Hint: Sometimes it's better to pipe through less.")
    print("{0} [-flags] | less".format(sys.argv[0]).center(int(TERMWIDTH)))

    sys.exit(exit_code) 
#^----------------------------------------------------------------------------- show_usage(exit_code)    
    
# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  main()
