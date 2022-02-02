#!/bin/bash
#-----------------------------------------------------------
# Purpose: This script creates a `jupyeter-lab` instance
#          for your project on the NIH cluster (biowulf.nih.gov) 
#          and binds the instance to a tunneled port on your
#          local machine. This allows you to work on the cluster
#          directly from your local machine.
#        
#
# Author:  Mohammad M. Ghassemi
#          DATA Scholar, NIH, 2021
#          ghassemimm@nih.giv or ghassem3@msu.edu
#----------------------------------------------------------
# PARAMETERS:
#----------------------------------------------------------
# - SCRATCH     : SSD Disk Reservation (GB)
# - CPUS        : Number of CPUs you want
# - MEM         : Memory for your instance
# - EXCLUSIVE   : '--exclusive': Indicates exclusive reservation of node, '': nonexclusive
# - PROJECTNAME : Location for the project
#---------------------------------------------------------
SCRATCH=5
CPUS=8
MEM=128g
EXCLUSIVE= 
PROJECTNAME=/data/$USER/brainworks
PROJECTDATABASE=/data/$USER/brainworks/database
#PROJECTNAME=/lscratch/$SLURM_JOB_ID

#------------------------------------------------
# CANCEL ANY RESERVATIONS
#-----------------------------------------------
scancel -u $USER
CREATIONSTATUS=$(squeue -u ghassemimm | tr -s ' ' | cut -d ' ' -f 9 | tail -1)
while [ "$CREATIONSTATUS" != "NODELIST(REASON)" ]
do
    echo "Canceling the interactive session"
    sleep 5
    CREATIONSTATUS=$(squeue -u ghassemimm | tr -s ' ' | cut -d ' ' -f 9 | tail -1)
done


#-------------------------------------------------
# RESERVE THE MACHINE
#-------------------------------------------------
bash run_sinteractive.sh $SCRATCH $CPUS $MEM $EXCLUSIVE & 

CREATIONSTATUS=$(squeue -u ghassemimm | tr -s ' ' | cut -d ' ' -f 9 | tail -1)
while [[ "$CREATIONSTATUS" == "(None)" || "$CREATIONSTATUS" == "NODELIST(REASON)" ]]
do
    echo "waiting for interactive session to be provisioned"
    sleep 5
    CREATIONSTATUS=$(squeue -u ghassemimm | tr -s ' ' | cut -d ' ' -f 9 | tail -1)
done

#-----------------------------------------------
# CREATE THE PROJECT AND DATABASE FOLDER
#-----------------------------------------------
# CHECK IF THE PROJECT EXISTS, IF NOT CRAETE IT.
if [ ! -d "$PROJECTNAME" ]; then
     echo "Project directory does not exist, creating it..."
     ssh $USER@$CREATIONSTATUS -t "mkdir $PROJECTNAME"
fi

# CHECK IF THE DATABASE FOLDER EXISTS, IF NOT CREATE IT.
if [ ! -d "$PROJECTDATABASE" ]; then
    echo "Database directory does not exist, creating it..."
    mkdir $PROJECTDATABASE
    mkdir $PROJECTDATABASE/data
    mkdir $PROJECTDATABASE/temp
    
    echo "Initilizing the database..."
    echo "See: https://seo-explorer.io/blog/twenty-ways-to-optimize-mysql-for-faster-insert-rate/"
    echo "And: https://gist.github.com/fevangelou/fb72f36bbe333e059b66"
    echo "And: https://seo-explorer.io/blog/five-ways-to-improve-mysql-select-speed-part-1/"
    mysqld --initialize-insecure --datadir="$PROJECTDATABASE/data"

    echo "Creating Database Configuration File"
    echo "[client]" > $PROJECTDATABASE/my.cnf
    echo "user=root"                            >> $PROJECTDATABASE/my.cnf
    echo "socket=$PROJECTDATABASE/mysql.sock"   >> $PROJECTDATABASE/my.cnf 
    echo ""                                     >> $PROJECTDATABASE/my.cnf 
    echo "[mysqld]"                             >> $PROJECTDATABASE/my.cnf 
    echo "datadir=$PROJECTDATABASE/data"        >> $PROJECTDATABASE/my.cnf 
    echo "socket=$PROJECTDATABASE/mysql.sock"   >> $PROJECTDATABASE/my.cnf 
    echo "tmpdir=$PROJECTDATABASE/temp"         >> $PROJECTDATABASE/my.cnf 
    echo "log-error=$PROJECTDATABASE/mysql.log" >> $PROJECTDATABASE/my.cnf 
    echo "pid-file=$PROJECTDATABASE/mysql.pid"  >> $PROJECTDATABASE/my.cnf
    echo "default_storage_engine = InnoDB"      >> $PROJECTDATABASE/my.cnf  
    echo "innodb_buffer_pool_instances = 2"     >> $PROJECTDATABASE/my.cnf 
    echo "innodb_buffer_pool_size = 8G"         >> $PROJECTDATABASE/my.cnf
    echo "innodb_flush_log_at_trx_commit  = 0"  >> $PROJECTDATABASE/my.cnf
    echo "innodb_flush_method = O_DIRECT"       >> $PROJECTDATABASE/my.cnf
    echo "innodb_thread_concurrency = 4"        >> $PROJECTDATABASE/my.cnf
    echo "max_connections = 100"                >> $PROJECTDATABASE/my.cnf
    echo "back_log= 512"                        >> $PROJECTDATABASE/my.cnf 
    echo "innodb_file_per_table = 1"            >> $PROJECTDATABASE/my.cnf
    echo "innodb_log_buffer_size = 32M"         >> $PROJECTDATABASE/my.cnf
    echo "innodb_read_io_threads = 64"          >> $PROJECTDATABASE/my.cnf
    echo "innodb_write_io_threads = 64"         >> $PROJECTDATABASE/my.cnf
    echo "skip-networking"                      >> $PROJECTDATABASE/my.cnf  
 
    # Setting the permissions on the file.
    chmod 600 $PROJECTDATABASE/my.cnf
    
fi

#-----------------------------------------------
# SET UP CONDA ENVIRONMENT
#-----------------------------------------------
if [ ! -d "$PROJECTNAME/conda" ]; then
    echo "Conda environment does not exist, creating it..."
    ssh $USER@$CREATIONSTATUS -t "cd $PROJECTNAME; wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh; bash Miniconda3-latest-Linux-x86_64.sh -p $PROJECTNAME/conda -b"
fi 

#-----------------------------------------------
# CREATE A CUSTOM .BASHRC THAT BINDS TO CONDA
#-----------------------------------------------
echo "cd $PROJECTNAME" > ~/.bashrc_custom
echo "PS1='\[\033[1;36m\]\u\[\033[1;31m\]@\[\033[1;32m\]\h:\[\033[1;35m\]\w\[\033[1;31m\]\$\[\033[0m\] '" >> ~/.bashrc_custom
#echo "PORT1=$PORT1" >> ~/.bashrc_custom
echo "source $PROJECTNAME/conda/etc/profile.d/conda.sh" >> ~/.bashrc_custom
echo "conda activate base" >> ~/.bashrc_custom
echo "mysqld_safe --defaults-file=$PROJECTDATABASE/my.cnf &" >> ~/.bashrc_custom

#-----------------------------------------------
# SSH INTO THE INSTANCE - YOU CAN NOW PIP INSTALL
#-----------------------------------------------
#ssh $USER@$CREATIONSTATUS -t "cd $PROJECTDATABASE; mysqld_safe --defaults-file=my.cnf &"
ssh $USER@$CREATIONSTATUS -t "cd $PROJECTNAME; /bin/bash --rcfile ~/.bashrc_custom -i " 

