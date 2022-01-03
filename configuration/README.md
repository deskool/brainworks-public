# BRAINWORKS

## Platform configuration file

Author: [Dr. Mohammad Ghassemi](https://ghassemi.xyz), National Scholar of Data and Technology Advancement, National Institutes of Health

<hr>

### About

In this directory, you will find a configuration file for the BRAINWORKS tool: `config.py`. The configuration file has several fields that **must be** updated before use of the tool is possible; this includes the address of the database, and API keys for several tools used by the technology. Below we provide specific instructions to help you set the configuration file. 



### Directory Contents

* `config.py`: 
  contains a python dictionary with configuration information used by the tool.



### Instructions for use

#### 1.  API Keys and credentials

To use BRAINWORKS, you will be required to generate and/or provide three major credentials:

* `config['NCBI_API']` : 
  Is used for collection of data from PubMed; to generate credentials:

  * [Register](https://www.ncbi.nlm.nih.gov/account/) for an NCBI account (or login).
  * Navigate to the **settings** page by clicking your *username* in the top-right corner. 
  * Under the **API Key Management** section click *Create an API Key*

* `config['UMLS']` :
  Is used to access the UMLS API; to generate credentials:

  * [Register](https://uts.nlm.nih.gov/uts/login) for a NLM account (or login).
  * Under `UTS Profile` panel on the right, click `Generate an API Key`.
  * Complete the form and copy the `API Key` listed.

* `config['AWS']` : 
Is used to access Amazon Services; to generate credentials:
  
* [Register](https://aws.amazon.com/) for an AWS account (or login).
  
* Visit [IAM](https://console.aws.amazon.com/iamv2/home) and generate access key credentials with Admin privileges.
  
  * be sure to add your access key and secret access key to your `~/.aws/credentials` file.  
  
    

#### 2. Database 

The MYSQL database for BRAINWORKS can be hosted locally or remotely. If you choose to host the database remotely, you will need to provide all connection information under `config['database']['remote']`.  If you wish to host the database locally, set `config['database']['local']['is_used'] = True`, and specify the location of the `my.cnf` file.

