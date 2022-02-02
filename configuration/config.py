#################################################################
# BRAINWORKS - Platform Configuration File 
#################################################################

config = {'database': { 'name'   : 'brainworks',                                                         # The name of the database
                        'local'  : { 'is_used'            : False,                                       # A flag indicating if the database is local or remote
                                     'base_dir'           : '',                                          # The base directory of the database
                                     'configuration_file' : ''                                           # The configuration file of the database "my.cnf"
                                  },
                        'remote' : { 'is_used'  : True,
                                     'host'     : '',                                                    # The Remote database Hostname
                                     'user'     : '',                                                    # The Database User
                                     'port'     : 0 ,                                                    # The Database Port
                                     'password' : ''                                                     # The Database Password
                                   }                    
                      },
          'data_directory'    : '../data/',                                                              # The location where local data is stored
          'NCBI_API'          : {'NCBI_API_KEY' : '',                                                    # An NCBI API Key
                                'rate_limit'    : 0                                                      # The rate limit of the API (this is decided by NCBI)
                                },
          'UMLS' : {'username' : '',                                                                     # The username associated with the API Key
                    'APIKey'   : ''                                                                      # The UMLS API Keyfire database
                   },        
          'AWS': {'IAM':{'access_key_id'     : '',                                                       # The AWS Access Key ID Credendentials of your IAM account
                         'secret_access_key' : ''                                                        # The AWS Secret Access Key of your IAM account
                        },
                  'S3' :{'bucket_name':''}                                                               # The name of the S3 Bucket to store collected data
                 },
          'NLP': {'coreferenceResolution' : {'model': 'https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz'},   # Coreference Resolution Model
                  'getEntities'           : {'model': ["en_ner_bionlp13cg_md", "en_core_sci_scibert"]},                                                  # NER Models
                  'informationExtraction' : {'properties': {"annotators"                  : "tokenize,ssplit,pos,lemma,depparse,natlog,openie",          # OpenIE Configuration
                                                            "openie.max_entailments_per_clause" : "1000",   
                                                            "openie.triple.strict"   : "true",
                                                            "openie.threads"         : 12
                                                            },
                                            'memory'    : '16G',
                                            'endpoint'  : 'http://localhost:9000'
                                            }
                  
                 }
         }
