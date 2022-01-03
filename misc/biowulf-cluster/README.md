# BRAINWORKS

## Processing Logs

<hr>

### About

This directory contains files for running a Jupiter Lab and MySQL instance on the NIH Biowulf SLURM cluster. 



### Directory Contents

* `reserve.sh`: This script creates a `jupyeter-lab` instance for your project on the NIH cluster (biowulf.nih.gov) and binds the instance to a tunneled port on your local machine. This allows you to work on the cluster directly from your local machine.

* `run_sinteractive.sh`:  This script is called by `reserve.sh` as part of the reservation process.

  

### Instruction for use

#### 1. Obtain Biowulf credentials

To obtain access to the Biowulf high performance computing cluster:

1. __Create an Account__: by visiting the NIH IT Service Portal. Search for _Helix/Biowulf (HPC) Account Request_. Fill out the form and wait to hear back with a confirmation about the creation of your account.  
2. __SSH into `biowulf.nih.gov`__: You should receive your login credentials from NIH IT after your account is created.



#### 2. Configure reservation requirements

You may need to  the `/scripts/biowulf/reserve.sh` to provision a new instance that will host the Jupyeterlab instance. Note that the `reserve.sh` script contains some parameters: `SCRATCH`,`CPUS`,`MEM`,`PROJECTNAME` that control the power of the machine hosting the jupyterlab instance. Depending on your needs, you may want to change these paramters. 



#### 3. How to Launch BRAINWORKS via HPC

To obtain access to Jupyterlab hosted on the HPC through your NIH machine, you will:

1. __Reserve an instance__ (from Biowulf): 

```
./reserve.sh
```

2. __Note the Port__: as reserve.sh runs, it will output a line that indicates a `PORT` you should bind to when setting up an SSH tunnel between your local machine and the cluster to use the Jupyterlab IDE. That message will look something like the output shown below; make sure to note down the `PORT`:

```bash
Please Create a SSH tunnel from your workstation to these ports on biowulf.
On Linux/MacOS, open a terminal and run:

ssh -L <PORT>:localhost:<PORT> user@biowulf.nih.gov
```

3. __Install Jupyterlab__ (from Biowulf): 

```bash
pip install jupyterlab
```

4. __Create a Tunnel into Biowulf__ (from your local machine):

```
ssh -L <PORT>:localhost:<PORT> user@biowulf.nih.gov
```
5. __Launch Jupyterlab__ (from Biowulf):

```
jupyter-lab --ip localhost --port <PORT> --no-brows
```

6. __Access Jupyterlab via Browser__ (from your local machine): 

Step 5 (above) will provide a url that you can put into your browser to access Jupyterlab.

