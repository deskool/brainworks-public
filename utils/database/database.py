import mysql.connector
from configuration.config import config
from   pprint import pprint
import os


#################################################################################
# EXAMPLE USAGE - Exploring what's in the database.   
#################################################################################

class database:
    
    def __init__(self, use_local = False):
          
        # Grab information from the configuration file
        self.use_local      = use_local
        self.local_db       = config.get('database',{}).get('local',{}).get('is_used')
        self.database       = config.get('database',{}).get('name')  
        self.base_directory = config.get('database',{}).get('local',{}).get('base_dir')
        self.option_files   = config.get('database',{}).get('local',{}).get('configuration_file')
        self.host           = config.get('database',{}).get('remote',{}).get('host')
        self.user           = config.get('database',{}).get('remote',{}).get('user')
        self.port           = config.get('database',{}).get('remote',{}).get('port')
        self.password       = config.get('database',{}).get('remote',{}).get('password')       
        self.table_info     = self.getTableInfo()
        self.id_map         = self.getIdMap()
    
    def getIdMap(self):
        
        idmap =  { 'application_types' : {'projects' : ['projects.application_type'  , 'application_types.application_type' ]
                                                       },
                                      'documents'    : {'publications' : ['publications.pmid'          , 'documents.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'documents.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'documents.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'documents.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'documents.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'documents.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'documents.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'documents.pmid' ]
                                                       },
                                      'publications' : {'documents'    : ['documents.pmid'             , 'publications.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'publications.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'publications.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'publications.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'publications.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'publications.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'publications.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'publications.pmid' ]
                                                       },
                                      'grants'       : {'documents'    : ['documents.pmid'             , 'grants.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'grants.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'grants.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'grants.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'grants.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'grants.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'grants.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'grants.pmid' ]
                                                       },
                                      'id_map'       : {'documents'    : ['documents.pmid'             , 'id_map.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'id_map.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'id_map.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'id_map.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'id_map.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'id_map.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'id_map.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'id_map.pmid' ]
                                                       },          
                                      'topics'       : {'documents'    : ['documents.pmid'             , 'topics.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'topics.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'topics.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'topics.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'topics.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'topics.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'topics.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'topics.pmid' ]
                                                       }, 
                                      'qualifiers'   : {'documents'    : ['documents.pmid'             , 'qualifiers.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'qualifiers.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'qualifiers.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'qualifiers.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'qualifiers.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'qualifiers.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'qualifiers.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'qualifiers.pmid' ]
                                                       }, 
                                      'affiliations' : {'documents'    : ['documents.pmid'             , 'affiliations.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'affiliations.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'affiliations.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'affiliations.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'affiliations.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'affiliations.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'affiliations.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'affiliations.pmid' ]
                                                       }, 
                                      'citations'    : {'documents'    : ['documents.pmid'             , 'citations.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'citations.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'citations.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'citations.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'citations.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'citations.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'citations.pmid' ],
                                                        'link_tables'  : ['link_tables.pmid'           , 'citations.pmid' ]
                                                       }, 
                                      'link_tables'  : {'documents'    : ['documents.pmid'             , 'link_tables.pmid' ],
                                                        'publications' : ['publications.pmid'          , 'link_tables.pmid' ],
                                                        'grants'       : ['grants.pmid'                , 'link_tables.pmid' ],
                                                        'id_map'       : ['id_map.pmid'                , 'link_tables.pmid' ],
                                                        'topics'       : ['topics.pmid'                , 'link_tables.pmid' ],
                                                        'qualifiers'   : ['qualifiers.pmid'            , 'link_tables.pmid' ],
                                                        'affiliations' : ['affiliations.pmid'          , 'link_tables.pmid' ],
                                                        'citations'    : ['citations.pmid'             , 'link_tables.pmid' ],
                                                        'patents'      : ['patents.project_id'         , 'link_tables.project_number'],
                                                        'projects'     : ['projects.core_project_num'  , 'link_tables.project_number']
                                                       },
                                      'patents'      : {'link_tables'      : ['link_tables.project_number'   , 'patents.project_id']

                                                       },
                                     'projects'      : {'abstracts'         : ['abstracts.application_id'   , 'projects.application_id'],
                                                        'link_tables'       : ['link_tables.project_number' , 'projects.core_project_num'],
                                                        'application_types' : ['application_types.application_type' , 'projects.application_type'],
                                                        'patents'           : ['patents.project_id' , 'projects.core_project_num']
                                                       },
                                     'abstracts'     : {'projects'          : ['projects.application_id', 'abstracts.application_id' ]
                                                       }}
        return idmap

    
    def query(self, query = "SELECT CURDATE()", parameters = None, use_local = False):
        
        # ----------------------------------------------------------
        # If this is a local instance of the database.
        # ----------------------------------------------------------
        if (self.local_db is True) or (self.use_local == True):
            if self.database == None:    
                cnx = mysql.connector.connect(option_files=self.option_files) # Connect to server
            else:
                cnx = mysql.connector.connect(option_files=self.option_files, database=self.database) # Connect to server
        # ----------------------------------------------------------
        # If this is a remote instance of the database.
        # ----------------------------------------------------------
        else:
            cnx = mysql.connector.connect(host     = self.host, 
                                          user     = self.user,
                                          password = self.password,
                                          port     = self.port,
                                          database = self.database
                                         )
  

        if parameters is not None:
            # Execute a query
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)                                 

        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()                                          
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")                     
            row = cur.fetchall()                                       
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    
    def purgeDocumentsfromDatabase(self, document_list):
        
        print("----------------------------------------------------------")
        print(" Purging Data from Database using `document_list`")
        print("----------------------------------------------------------")
        xx = [x.split('id-')[1].split('_')[0] for x in document_list]
        for table in ['citations', 'affiliations', 'publications','documents','grants','id_map','qualifiers','topics']:
            print('.... Purging rows from', table)
            query = f"DELETE FROM {table} WHERE pmid in ({','.join(xx)})"
            self.query(query)
        print('.... PURGE COMPLETED')            

    def help(self):
        print('---------------------------------------')
        print(' Returning Document JSON               ')
        print('---------------------------------------')
        doc = {'Explore the Database' :     """from utils.database.database import database   # import the utility
db = database()                                # instantiate the class
table_info = db.getTableInfo()                 # get the tables in the database
print(table_info.keys())                       # print a list of the tables
pprint(table_info['publications'])             # print table information from the `publications` table.
        """,
                'Query the database' :     """from utils.database.database import database   # import the utility
db = database()                                # instantiate the class
db.query("SELECT * FROM elements LIMIT 3")     # query the database
        """
               }
        return doc
    
    
    def getReccomendedInnoDbBufferPoolSize(self):
        print(self.query("""SELECT CEILING(Total_InnoDB_Bytes*1.6/POWER(1024,3)) RIBPS FROM
                    (SELECT SUM(data_length+index_length) Total_InnoDB_Bytes
                    FROM information_schema.tables WHERE engine='InnoDB') A"""))
            
    def getTableInfo(self, table_name = None):    
        table_info = {}
        if table_name is None:
            tables = [table['Tables_in_brainworks'] for table in self.query("SHOW TABLES")]   
        else:
            tables = [table_name]
        
        # Get the columns
        for t in tables:
            
            query = """SELECT COLUMN_NAME,
                              DATA_TYPE,
                              COLUMN_COMMENT,
                              CHARACTER_MAXIMUM_LENGTH,
                              COLUMN_KEY
                         FROM information_schema.columns 
                        WHERE table_schema = '{database_name}' 
                          AND table_name   = '{table_name}'
                    """.format(table_name = t, database_name = self.database)
            results = self.query(query)
            column_info = {}
            for row in results:
                column_info[row['COLUMN_NAME']] = {}
                column_info[row['COLUMN_NAME']]['data_type']     = row['DATA_TYPE']
                column_info[row['COLUMN_NAME']]['column_length'] = row['CHARACTER_MAXIMUM_LENGTH']
                column_info[row['COLUMN_NAME']]['comment']       = row['COLUMN_COMMENT']
                column_info[row['COLUMN_NAME']]['column_key']    = row['COLUMN_KEY']
            table_info[t] = column_info
        
        if table_name is None:
            self.table_info = table_info
            return table_info
        else:
            return column_info
            

    def listTables(self):
        return [ list(x.items())[0][1] for x in self.query("SHOW TABLES")]
    
    def listDataSourceFile(self, tables = ['abstracts','link_tables','patents','projects']):
        result = []
        for table in tables:
            try:
                query = """SELECT DISTINCT source FROM {table}""".format(table = table)
                result += [ list(x.items())[0][1] for x in self.query(query)]
            except:
                continue
        return result
    
    def addColumnsToTable(self,tablename = '', new_columns = {'name':{'type':'', 'size':''}}):
    # Example Usage:    
    # db.addColumnsToTable(tablename = 'publications', new_columns = {'nlmid' : {'type':'VARCHAR', 'size':'100'},
    #                                                                   'doi' : {'type':'VARCHAR', 'size':'100'},
    #                                                           'issnlinking' : {'type':'VARCHAR', 'size':'100'}})        

        add_columns      = list(set(new_columns.keys()) - set(self.get_table_info(tablename).keys()))
        
        if len(add_columns) == 0:
            print('No new columns to add')
        else:
            print('Adding', len(add_columns),'new columns')
        
        query = 'ALTER TABLE ' + tablename + ' '
        for column in add_columns:
            this_col = new_columns.get(column)
            if this_col['type'] == 'VARCHAR':
                query += """ ADD COLUMN {column} {type}({size}),""".format(column = column, type = this_col['type'], size = this_col['size'])
            else:
                query += """ ADD COLUMN {column} {type},""".format(column = column, type = this_col['type'])

        query = query[:-1]
        self.query(query)

        
