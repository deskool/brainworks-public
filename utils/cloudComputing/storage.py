from configuration.config import config
import boto3
import re
import glob

################################################################################################
# To use this library, we assume that:
################################################################################################
# 0. You have an IAM account
# 1. You created an S3 bucket and S3 Access point
# 2. You have properly configured permissions on the bucket and the access points; The bucket access point has your IAM as a permitted user.
# 2. You have attached a permissions policy to the IAM that enables access to S3 and/or the bucket 

class storage:
    def __init__(self, bucket_name=config['AWS']['S3']['bucket_name']):
        
        # Connect to the resource
        self.bucket_name = bucket_name        
        self.s3 = boto3.resource(
                  's3',
                  aws_access_key_id=config['AWS']['IAM']['access_key_id'],
                  aws_secret_access_key=config['AWS']['IAM']['secret_access_key'])
        self.bucket = self.s3.Bucket(bucket_name)

        
    ################################################################################################
    # This Function returns a list of all ExPORTER files that have already been downloaded.
    #-----------------------------------------------------------------------------------------------
    # INPUTS 
    # data_path         <String> - The base directory where the ExPORTER data is stored.
    #-----------------------------------------------------------------------------------------------
    # OUTPUTS
    # data_group        <List>   - A list of all files in the the ExPORTER directory
    ################################################################################################        
     
    # Lists the contents of the S3 Bucket
    def contents(self):
        
        files = {}
        for obj in self.bucket.objects.all():
            location = obj.key
            files[location] = {}
            files[location]['last_modified']  = obj.last_modified
            if location[-1] == '/':
                files[location]['is_directory']   = True
            else:
                files[location]['is_directory']   = False
        return files
    
    # uploads file to the S3 Bucket
    def upload(self,local_file, remote_file):
        # Upload file to cloud storage
        self.s3.meta.client.upload_file(local_file, self.bucket_name, remote_file)

    # Downloads file from S3 bucket to local disk
    def download(self, remote_file, local_file):
        self.s3.meta.client.download_file(self.bucket_name, remote_file, local_file)
        
    # Delete file from S3 Bucket
    def delete(self, remote_file):
        # Delete from cloud storage
        self.s3.Object(config['AWS']['S3']['bucket_name'], remote_file).delete()
    
    #Backs up entire directory
    def backup(self, files = [], replace_existing = False):
        file_upload_errors = []
        file_subset = files
        if replace_existing == False:
            file_subset = list(set(files) - set(self.contents()))
        print('Uploading', len(file_subset), 'files')    
            
        for file in file_subset:
            try:
                self.upload(file, file)
            except:
                try:
                    self.__init__()
                    self.upload(file, file)
                except:
                    file_upload_errors += file
        return file_upload_errors
    
###############################################################################
# Example Usage:
###############################################################################
if __name__ == '__main__':
    from utils.cloudComputing.storage import storage
    cstore = storage()

    # Pull the contents and print it
    x = cstore.contents()
    pprint(x)

    # Set the local and remote files
    local_file = 'README.md'
    remote_file = 'README.md'

    # Upload the file
    cstore.upload(local_file, remote_file)
    x = cstore.contents()
    pprint(x)
    
    #download the file
    cstore.download(remote_file, '_' + local_file)
    
    #delete the file
    cstore.delete(remote_file)
    x = cstore.contents()
    pprint(x)

    
    