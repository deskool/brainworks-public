# BRAINWORKS

## Cluster computing for NLP pipeline

<hr>

### About

This document provides instructions for setting up and deploying a SLURM parallel computing cluster to host the NLP Engine of BRAINWORKS. A computational cluster is **not required** to run the NLP pipeline, but is strongly encouraged if you want to perform information extraction from a large volume of papers.



### Directory Contents

* `privatemodules/java/jdk-17.0.1` : 
  A SLURM module file that enables Java on the SLURM cluster.
* `cluster-config.yaml` : 
  An AWS configuration file that specifies the infrastructure used within the cluster (e.g. number of worker machines).
* `extractInformation-parallel.py`: 
  A Python script that extracts one month intervals of of publication data from the BRAINWORKS database, and passes this data to the information extraction pipeline. This is the script that is run in parallel on the cluster.
* `deploy.sh` :
   A SLURM script that passes the month/year of interest to the `extractInformation-parallel.py` to the SLURM cluster.
* `setup.sh` : 
  A shell script that configures the SLURM cluster with all computational requirements needed to run the information extraction pipelines.



### Instructions for use

#### 1. Create the cluster

Install AWS pcluster command line tools and run the following from your local machine:

```bash
# Bind to an AWS Profile with IAM credentials that will allow you to create the cluster
export AWS_PROFILE=nih-ghassemi-iam

# Create a cluster configuration file
pcluster configure --config cluster-config.yaml

# Create the cluster
pcluster create-cluster --cluster-name slurm-cluster --cluster-configuration cluster-config.yaml

# Checking status
pcluster describe-cluster --cluster-name slurm-cluster --region us-east-1
```

**NOTE:** We assume here that you have an AWS IAM with admin privileges. Your profile should replace `nih-ghassemi-iam` in the above code. 



#### 2. SSH into the cluster 

Run from the local machine

```bash
# SSH into cluster
pcluster ssh -i ~/.ssh/nih-ghassemi-key.pem --cluster-name slurm-cluster
```



#### 3. Clone, setup, and deploy

From the computational cluster

```bash
# Clone this repository
git clone https://github.com/deskool/brainworks.git

# Move into the cluster directory
cd brainworks/cluster/

# Setup the cluster
./setup.sh

# Deploy the job
./deploy.sh
```



#### 4. Delete the cluster

From the local machine

```bash
# Delete Cluster
pcluster delete-cluster --cluster-name slurm-cluster --region us-east-1
```



### References

- [AWS Cluster Creation Instructions](https://docs.aws.amazon.com/parallelcluster/latest/ug/install-v3-configuring.html)





