from configuration.config import config
from utils.database.database  import database
from utils.generalPurpose.generalPurpose import *
import json
import requests
import xmltodict
import os
from os import path
import datetime
import time
import glob
import re
import wget
from zipfile import ZipFile
from csv import reader
import collections
import re
import subprocess
import itertools
import shutil
from pprint import pprint
import re
import pycountry
import xml.etree.ElementTree as ET
from dateutil.parser import parse
from utils.affiliationParser import parse_affil, match_affil
from utils.text2Graph.text2Graph import text2graph


t2g = text2graph()
db = database()


us_states = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

state_abbr = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}


class pubmed:
    
    def __init__(self):
        self.base_url       = ''       
        self.write_location = '' 
        self.document_list  = [] 
 
    ######################################################################
    # Gets a list of all stored JSON documents in the PubMed data directory.
    ######################################################################  
    def getStoredDocumentList(self, data_path= config['data_directory'] + 'PubMed'):
        papers = getDirectoryContents(data_path, extension='json')
        
        # Remove anything that is search related.
        papers = [p for p in papers if '/search/' not in p]
        
        print('.... Identified', len(papers), 'papers.')
        self.document_list = papers
        
        
    ######################################################################
    # Computes the incidence of field availability across files downloaded pubmed files.  
    ######################################################################    
    def getStoredDocumentFieldStats(self, data_path=config['data_directory'] + 'PubMed', savename=config['data_directory'] + 'PubMed/stats/field-statistics.stats', replace_existing = False):

        print('------------------------------------------------')
        print('Generating field statistics from data in ', data_path)
        print('------------------------------------------------')

        # Create the save directory
        if not os.path.isdir(config['data_directory'] + 'PubMed/stats'):
            os.mkdir(config['data_directory'] + 'PubMed/stats')   
        
        # Check if this file already exists.
        if (os.path.exists(savename)) and (replace_existing == False):
            print('A field statistics file with that name already exists; if you would like to replace the file, set `replace_existing=True`')
            return None

        print('.... Getting list of stored .json documents in', data_path)
        self.getStoredDocumentList(data_path = data_path)
            
        # Intialize the field stats Counter.
        print('.... Ingesting papers (this may take some time)')
        field_stats = collections.Counter([])
        for i,paper in enumerate(self.document_list):
            with open(paper) as read_file:
                paper_json = json.load(read_file)

            # Flatten the paper
            x = flatten(paper_json, last_keys='',key_list=[], value_list=[])

            # Get the unique keys (so we do not double count author lists, for insntance.)
            keys = list(set([re.sub(r'_\d+_','',a) for a in list(x.keys())]))

            # Add the field counts
            field_stats += collections.Counter(keys)
        field_stats = dict(field_stats)
        
        print('.... Normalizing field counts')
        normalization =  len(self.document_list)
        for key, val in field_stats.items():
            field_stats[key] = round(100 * (val / normalization)) 
        
        print('.... saving field statistics to', savename)
        f = open(savename, "w")
        json.dump(field_stats, f); f.close();
        return None

    ######################################################################
    # Returns list of matches that satisfy the regular expression
    ######################################################################      
    def findMatches(self, regular_expression, text):
        import re
        results            = [ {"indicies":m.span(), "match":m.group() } for m in re.finditer(regular_expression,text)];
        matches            = []; [matches.append(m['match']) for m in results];
        return matches
        
    ######################################################################
    # Creates directory structure used to store the data,
    ######################################################################
    def makeDirectories(self, subdirectory = None, date = None):
            # Generate the root directory
            self.write_location = self.write_location[:-1] if self.write_location[-1] == '/' else self.write_location
            if not os.path.isdir(self.write_location):
                os.mkdir(self.write_location)

            if date is not None:
                # Make the date component of the directory
                if not os.path.isdir(self.write_location + '/' + date['year']):
                    os.mkdir(self.write_location + '/' + date['year'])
                if not os.path.isdir(self.write_location + '/' + date['year'] + '/' + date['month']):
                    os.mkdir(self.write_location + '/' + date['year'] + '/' + date['month'])
                if not os.path.isdir(self.write_location + '/' + date['year'] + '/' + date['month'] + '/' + date['day']):
                    os.mkdir( self.write_location + '/' + date['year'] + '/' + date['month'] + '/' + date['day'])

                # Update the write_location
                self.write_location = self.write_location + '/' + date['year'] + '/' + date['month'] + '/' + date['day']

            if subdirectory is not None:
                self.write_location = self.write_location + '/' + subdirectory
                # Make the folder for the sub-directory
                if not os.path.isdir(self.write_location):
                    os.mkdir(self.write_location)

                # Ensure the xml sub-directory exists
                if not os.path.isdir(self.write_location + '/xml'):
                    os.mkdir(self.write_location + '/xml')

                # Ensure the json sub-directory exists
                if not os.path.isdir(self.write_location + '/json'):
                    os.mkdir(self.write_location + '/json')

                    

    ######################################################################
    # Downloads pubmed abstracts and metadata via the entrez eutil
    ######################################################################
    def collect(self, query_params      = {'db':'pubmed','id':'212403'}, 
                      write_location    = 'data/',
                      replace_existing  = False,
                      show_query        = False,
                      action            = 'fetch'):
        
        #------------------------------------------------------------------
        # SETTING THE DEFAULTS FOR SOME PARAMETRS
        #------------------------------------------------------------------
        # The API Key
        query_params['api_key'] = config['NCBI_API']['NCBI_API_KEY']
        
        # Which database do we want to interact with, `pubmed` is the default.
        query_params['db'] = 'pubmed' if query_params.get('db') is None else query_params.get('db')    
        
        # How do we want to the data returned, `xml` is the default
        query_params['retmode'] = 'xml' if query_params.get('retmode') is None else query_params.get('retmode')   
            
        if action == 'search':
            query_params['retstart'] = '0'     if query_params.get('retstart') is None else query_params.get('retstart')
            query_params['retmax']   = '10000' if query_params.get('retmax')   is None else query_params.get('retmax')
        
        # Concatenate the IDs, if this is a list of ids.
        if query_params.get('id') is not None:
            query_params['id'] = ','.join(query_params.get('id')) if (isinstance(query_params['id'], list) and query_params['id'] is not None) else query_param.get('id')
        
        #------------------------------------------------------------------
        # CHOOSE THE UTILITY WE WILL BE USING
        #------------------------------------------------------------------
        self.write_location = write_location
        self.base_url       = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        
        base_url = self.base_url
        if action == 'fetch':
            tool = '/efetch.fcgi'
        if action == 'search':
            tool = '/esearch.fcgi'
        base_url += tool
    
        
        #------------------------------------------------------------------
        # CONSTRUCT THE REQUEST QUERY
        #------------------------------------------------------------------ 
        # Initialize the query with the API base
        query    = base_url + '?'
        savename = '' 

        # Construct the query using the provided information
        for key,value in query_params.items():

            # We want to include all but the API Key in the filename
            if key != 'api_key':
                svalue  = 'none'       if (value is None) else value
                svalue = '|||PMID|||' if (key == 'id' and ',' in svalue) else svalue 
                savename += "{key}-{value}_".format(key=key, value=svalue.replace('/','')) 

            # Update the query
            if action == 'fetch':
                query       += "{key}={value}&".format(key=key, value=value)
            
            elif action == 'search':
                if key in ['term']:
                    term_string = ''
                    if value is not None:
                        term_string  = value + "+AND+" 
                elif key in ['date']:
                    term_string += value + "[pdat]"
                    query       += "{key}={value}&".format(key='term', value=term_string)
                    date         = { 'year'  :value.split('/')[0], 
                                     'month' :value.split('/')[1], 
                                     'day'   :value.split('/')[2] }
                else:
                    query       += "{key}={value}&".format(key=key, value=value)
                

        #------------------------------------------------------------------
        # MAKE THE REQUEST, AND STORE THE DATA
        #------------------------------------------------------------------
        # GET THE DATA
        response = requests.get(query)
        
        if show_query == True:
            print('See Results Here:\n',query,'\n')

            
        #------------------------------------------------------------------
        # CONSTRUCT SAVE LOCATION FROM PUBLICATION DATE
        #------------------------------------------------------------------
        if action == 'fetch':
            articleset = ET.fromstring(response.content)
            
            # FOR EACH ARTICLE IN THE ARTICLESET
            filenames = []
            for article in articleset:
                
                # Get the article text
                article_text = ET.tostring(article)

                # Get the Pubmed_id
                try:
                    pmid = article.find("MedlineCitation/PMID").text
                except:
                    continue
                
                # CONSTRUCT THE DATE DICTIONARY FROM THE PUBLICATION DATE
                pubdate = {}
                if article.find("MedlineCitation/Article/Journal/JournalIssue/PubDate") is not None:    
                    for elem in article.find("MedlineCitation/Article/Journal/JournalIssue/PubDate"):
                        pubdate[elem.tag] = elem.text
                
                year    = pubdate.get('Year')
                month   = 'Jan' if pubdate.get('Month') is None else pubdate.get('Month')
                day     = '1'   if pubdate.get('Day') is None else pubdate.get('Day')
                dateval = parse(f"{year}-{month}-{day}",) if year is not None else None
                date    = None if dateval is None else {'year': str(dateval.year), 'month': str(dateval.month), 'day':str(dateval.day)}
                
                if date is not None:
                    date['month'] = '0' + date['month'] if len(date['month']) == 1 else date['month']
                    date['day']   = '0' + date['day'] if len(date['day'])     == 1 else date['day'] 
                else:
                    date = None

                #------------------------------------------------------------------
                # CREATE DIRECTORY STRUCTURES TO STORE DATA
                #------------------------------------------------------------------
            
                if date is not None:
                    self.write_location = write_location
                    self.makeDirectories(subdirectory=action, date=date)
                else:
                    self.write_location = write_location
                    self.makeDirectories(subdirectory = 'date_unknown')

                    
                _savename = savename[:-1].replace('|||PMID|||', pmid)
                filename  = self.write_location + '/xml/' + _savename + ".xml"    

                #------------------------------------------------------------------
                # SAVE THE DOCUMENTS
                #------------------------------------------------------------------
                data_dict = xmltodict.parse("<PubmedArticleSet>" + article_text.decode('utf-8') + "</PubmedArticleSet>")
                
                # Save as JSON
                filename = self.write_location + '/json/' + _savename + ".json"
                f = open(filename, "w")
                json.dump(data_dict, f); f.close();
                
                filenames.append(filename)
            return {'status':'download','location':filenames}
        
        elif action == 'search':
            #------------------------------------------------------------------
            # CREATE DIRECTORY STRUCTURES TO STORE DATA
            #------------------------------------------------------------------
            if date is not None:
                self.makeDirectories(subdirectory=action, date=date)
            else:
                self.makeDirectories(subdirectory = 'date_unknown')

            filename = self.write_location + '/xml/' + savename[:-1] + ".xml"   
            
            # Save the xml result
            f = open(filename,"w")
            f.write(response.text);f.close()

            # Convert the result to JSON
            with open(filename) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())
            xml_file.close()
            
            # Save as JSON
            filename = self.write_location + '/json/' + savename[:-1] + ".json"
            f = open(filename, "w")
            json.dump(data_dict, f); f.close();
            return {'status':'download','location':filename}

    
    #########################################################
    # Packages requests to the Entrez Eutil to improve collection speed
    #########################################################
    def bulkCollect(self, parameters, rate_limit = 5, batch_size = 100):

        
        def chunks(lst,n):
            return [lst[i:i + n] for i in range(0, len(lst), n)]


        
        # Set the rate limit according to the configuration file.
        if config.get('NCBI_API').get('rate_limit') is not None:
            rate_limit = config.get('NCBI_API').get('rate_limit')
        
        print('------------------------------------------------')
        print('Starting Bulk Paper Collection')
        print('------------------------------------------------')
        
        start_date   = parameters['start_date']
        end_date     = parameters['end_date']
        num_requests = 0
        
        while start_date != end_date:

            #-----------------------------------------
            # Perform the Search operation
            #-----------------------------------------
            query_params = {'db'       : parameters['database'],           
                            'term'     : parameters['search_term'],     
                            'date'     : start_date,                                      
                            'retstart' : '0',           
                            'retmax'   : '10000',       
                            'api_key'  : config['NCBI_API']['NCBI_API_KEY']
                            }

            self.collect(action       = 'search',
                     write_location   = parameters['save_directory'],
                     query_params     = query_params,
                     replace_existing = True,
                     show_query       = False)


            #-----------------------------------------
            # Get the IDS
            #-----------------------------------------
            data_path = parameters['save_directory'] + start_date + '/search/json/*'
            data_path = glob.glob(data_path)[0]
            with open(data_path) as read_file:
                search_result = json.load(read_file)

            ids = search_result.get('eSearchResult').get('IdList')
            
            if ids is not None:
                ids        = ids.get('Id')
                id_batches = chunks(ids,batch_size)
                
                for _id in id_batches:
                    
                    if num_requests % rate_limit == 0:
                        time.sleep(1)

                    query_params = {'db'      : parameters['database'],     
                                    'id'      : _id,    
                                    'retmode' : 'xml',        
                                    'api_key' : config['NCBI_API']['NCBI_API_KEY']
                                    }

                    self.collect(action       = 'fetch',
                             write_location   = parameters['save_directory'],
                             query_params     = query_params, 
                             replace_existing = parameters['replace_existing'],
                             show_query       = False)

                    num_requests += 1

            #-------------------------------------------
            # Increment the date
            #-------------------------------------------
            date_1     = datetime.datetime.strptime(start_date, "%Y/%m/%d")
            start_date = date_1 + datetime.timedelta(days = 1)
            start_date = start_date.strftime("%Y/%m/%d")

            
            

    #####################################################################################
    # Collects all papers that were cited by papers already in the `publications` table.
    ####################################################################################
    def downloadCitedPapersByPubmedId(self, write_location = 'data/PubMed', replace_existing = False, batch_size = 100):
        
        def chunks(lst,n):
            return [lst[i:i + n] for i in range(0, len(lst), n)]
        
        print('---------------------------------------------')
        print('Looking for pmids in the `citations` without a matching entry in `publications`...')
        print('---------------------------------------------')
        
        #-------------------------------------------------------------------
        # Take pmids from the `link_tables` that are not in publications table
        #--------------------------------------------------------------------
        pmids_in_database = db.query("""SELECT distinct citations.pmid  
                                          FROM citations
                                          LEFT JOIN publications on publications.pmid = citations.pmid
                                         WHERE publications.pmid is NULL
                                      """)
        
        # Remove those pmids that have already been downloaded
        pmids_in_database = [str(pmid['pmid']) for pmid in pmids_in_database] 
        pmids_downloaded  = [doc.split('id-')[1].split('_')[0] for doc in self.document_list] 
        pmids             = list(set(pmids_in_database) -  set(pmids_downloaded))
        
        print("... Found", len(pmids), "entries without matching publication.")
        print("... Collecting new papers...")
         
        num_requests = 0
        id_batches   = chunks(pmids,batch_size)
        for batch in id_batches:
            
            if (num_requests+1) % config['NCBI_API']['rate_limit'] == 0:
                time.sleep(1)

            query_params = {'db'      : 'pubmed',                            # Database: 'pubmed', 'pmc', 'nlmcatalog'  
                            'id'      : batch,                               # id of the paper
                            'retmode' : 'xml',                               # the format you want the results returned in
                            'api_key' : config['NCBI_API']['NCBI_API_KEY']   # Your API Key
                            }

            status = self.collect(action           = 'fetch',
                                  write_location   = write_location,
                                  query_params     = query_params)

            num_requests += 1
        print(num_requests, 'new files downloaded')        
    
    ######################################################################
    # Downloads all papers from the `link_tables`, i.e. those from EXPORTER
    ######################################################################  
    def downloadExporterPapersByPubmedId(self, write_location = 'data/PubMed', replace_existing = False, batch_size = 100):
        
        def chunks(lst,n):
            return [lst[i:i + n] for i in range(0, len(lst), n)]
        
        print('------------------------------------------------------------------------------------')
        print('Looking for pmids in the `link_tables` without a matching entry in `publications`...')
        print('------------------------------------------------------------------------------------')
        
        #-------------------------------------------------------------------
        # Take pmids from the `link_tables` that are not in publications table
        #--------------------------------------------------------------------
        pmids_in_database = db.query("""SELECT distinct link_tables.pmid  
                                         FROM link_tables
                                         LEFT JOIN publications on publications.pmid = link_tables.pmid
                                         WHERE publications.pmid is NULL
                                      """)
        print()
        
        # Remove those pmids that have already been downloaded
        pmids_in_database = [str(pmid['pmid']) for pmid in pmids_in_database] 
        pmids_downloaded  = [doc.split('id-')[1].split('_')[0] for doc in self.document_list] 
        pmids             = list(set(pmids_in_database) -  set(pmids_downloaded))
        
        print("... Found", len(pmids), "entries without matching publication.")
        print("... Collecting new papers...")
         
        num_requests = 0
        id_batches   = chunks(pmids,batch_size)
        for batch in id_batches:
            
            if (num_requests+1) % config['NCBI_API']['rate_limit'] == 0:
                time.sleep(1)

            query_params = {'db'      : 'pubmed',                            # Database: 'pubmed', 'pmc', 'nlmcatalog'  
                            'id'      : batch,                               # id of the paper
                            'retmode' : 'xml',                               # the format you want the results returned in
                            'api_key' : config['NCBI_API']['NCBI_API_KEY']   # Your API Key
                            }

            status = self.collect(action           = 'fetch',
                                  write_location   = write_location,
                                  query_params     = query_params)

            num_requests += 1
        print(num_requests, 'new files downloaded')

    ######################################################################
    # Downloads full papers using the pubmed Central identifier (which provides DOI)
    ######################################################################  
    def downloadExporterPapersByPubmedCentralId(self, replace_existing = False):
        publications = db.query("""SELECT pmc_id, pub_date FROM publications where pmc_id IS NOT NULL""")
        num_requests = 0
        for paper in publications:

            write_location = config['data_directory'] + 'PubMedCentral/'

            #----------------------------------------------------------
            # Respect the API rate limits
            #----------------------------------------------------------
            if (num_requests+1) % config['NCBI_API']['rate_limit'] == 0:
                time.sleep(1)

            #----------------------------------------------------------
            # Get the location
            #----------------------------------------------------------
            if  paper['pub_date'] is not None: 
                date = {'year': str(paper['pub_date'].year), 'month': str(paper['pub_date'].month), 'day': str(paper['pub_date'].day) }
                write_location = generateDateDirectory(write_location, date)
            else:
                write_location = config['data_directory'] + 'PubMedCentral/' + 'date_unknown/'


            query_params = {'db'      : 'pmc',                               # Database: 'pubmed', 'pmc', 'nlmcatalog'  
                            'id'      : str(paper['pmc_id']),                # id of the paper
                            'retmode' : 'xml',                               # the format you want the results returned in
                            'api_key' : config['NCBI_API']['NCBI_API_KEY']   # Your API Key
                            }
            try:
                status = self.collect(action         = 'fetch',
                                    write_location   = write_location,
                                    query_params     = query_params, 
                                    replace_existing = replace_existing,
                                    show_query       = False)
                status = status['status']
            except:
                status = 'skip'
            
            if status != 'skip':
                num_requests += 1
        print(num_requests, 'new files downloaded')

         
    ######################################################################
    # Generates the tables used to store the data
    ######################################################################          
    def generateTables(self):
        
        print('------------------------------------------------')
        print(' Creating PubMed Tables                         ')
        print('------------------------------------------------') 
         
        query = """CREATE TABLE IF NOT EXISTS `application_types` (
                      `application_type`  int(11)      NOT NULL     COMMENT 'A numeric code for the application type.',
                      `description`       varchar(500) DEFAULT NULL COMMENT 'The meaning of the application code.',
                      PRIMARY KEY (`application_type`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
        db.query(query)
        print('.... `application_types` table created')
        
        query = """CREATE TABLE IF NOT EXISTS `citations` (
                  `pmid`          int(11)             DEFAULT NULL COMMENT 'The PubMed identification number of the paper being cited',
                  `citedby`       int(11)             DEFAULT NULL COMMENT 'The PubMed identification number of the paper that did the citing',
                  `citation_date` date                DEFAULT NULL COMMENT 'The date that the `pmid` was cited.',
                  `citation_num`  bigint(20) unsigned NOT NULL AUTO_INCREMENT,
                  PRIMARY KEY (`citation_num`),
                  UNIQUE KEY `citation_num`           (`citation_num`),
                  KEY `citations_pmid_index`          (`pmid`),
                  KEY `citations_pmiddate_index`      (`citation_date`,`pmid`),      
                  KEY `citations_citedby_index`       (`citedby`),
                  KEY `citations_citation_date_index` (`citation_date`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
                """
        db.query(query)
        print('.... `citations` table created')
        
        
        query = """CREATE TABLE IF NOT EXISTS `documents` (
                  `element_id`    bigint(20) unsigned  NOT NULL AUTO_INCREMENT,
                  `pmid`          int(11)              DEFAULT NULL  COMMENT 'The PubMed identification number.',
                  `pub_date`      date                 DEFAULT NULL  COMMENT 'The full date on which the issue of the journal was published.',
                  `content_order` int(11)              NOT NULL      COMMENT 'The order of the element_id in a give pmid document. 1 preceeds 2 and so on.',
                  `content_type`  varchar(100)         DEFAULT NULL  COMMENT 'The content type of the element_id: figure, title, abstract, section, subsection, subsubsection, etc.',
                  `content` TEXT CHARACTER SET utf8mb4 DEFAULT NULL  COMMENT 'The text of the element_id container. If this were a `section` or instance, then this field would contain the name of the section.',
                  PRIMARY KEY (`element_id`),
                  FULLTEXT KEY `documents_content_index` (`content`),
                  KEY `documents_pmid_index`             (`pmid`),
                  KEY `documents_pub_date_index`         (`pub_date`),
                  KEY `documents_pmiddate_index`         (`pub_date`,`pmid`),
                  KEY `documents_type_index`             (`content_type`),
                  KEY `documents_order_index`            (`pmid`,`content_order`),
                  KEY `documents_element_id_index`       (`element_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
                """
        db.query(query)
        print('.... `documents` table created')
        
        query="""CREATE TABLE IF NOT EXISTS `grants` (
                  `grant_num`  bigint(20)  unsigned NOT NULL AUTO_INCREMENT,
                  `grant_id`   varchar(30) DEFAULT NULL      COMMENT 'The grant ID',
                  `pmid`       int(11)     DEFAULT NULL      COMMENT 'The PubMed ID',
                  `pub_date`   date        DEFAULT NULL      COMMENT 'The full date on which the issue of the journal was published.',
                  PRIMARY KEY (`grant_num`),
                  UNIQUE KEY `grant_num`       (`grant_num`),
                  KEY `grants_grant_id_index`  (`grant_id`),
                  KEY `grants_pmid_index`      (`pmid`),
                  KEY `grants_pub_date_index`  (`pub_date`),
                  KEY `grants_pmiddate_index`  (`pub_date`,`pmid`)
    
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
                """
        db.query(query)
        print('.... `grants` table created')
        
        query="""CREATE TABLE IF NOT EXISTS `id_map` (
                  `map_id`       bigint(20)   unsigned NOT NULL AUTO_INCREMENT,
                  `pmid`         int(11)      NOT NULL      COMMENT 'The PubMed ID',
                  `pub_date`     date         DEFAULT NULL  COMMENT 'The full date on which the issue of the journal was published.',
                  `pmc_id`       varchar(100) DEFAULT NULL  COMMENT 'The PubMed Central ID',
                  `nlm_id`       varchar(100) DEFAULT NULL  COMMENT 'Natonal Library of Medicine ID',
                  `doi`          varchar(100) DEFAULT NULL  COMMENT 'The Digital Object Identifier',
                  `issn_linking` varchar(100) DEFAULT NULL  COMMENT 'The ISSN Linking Number',
                  PRIMARY KEY (`map_id`),
                  UNIQUE KEY `map_id`       (`map_id`),
                  KEY `id_map_pmid_index`   (`pmid`),
                  KEY `id_pub_date_index`   (`pub_date`),
                  KEY `id_pmiddate_index`   (`pub_date`,`pmid`),
                  KEY `id_doi_index`        (`doi`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
                """
        db.query(query)
        print('.... `id_map` table created')
        
        query ="""CREATE TABLE IF NOT EXISTS `qualifiers` (
                  `qualifier_num` bigint(20) unsigned  NOT NULL AUTO_INCREMENT,
                  `pmid`          int(11)              NOT NULL     COMMENT 'The PubMed Indentification number.',
                  `pub_date`      date                 DEFAULT NULL COMMENT 'The full date on which the issue of the journal was published.',
                  `topic_id`      varchar(15)          NOT NULL     COMMENT 'A unique Medical Subject Heading Code that Identifies the topic this `qualifier_id` applies to.',
                  `qualifier_id`  varchar(15)          NOT NULL     COMMENT 'The Medical Subject Heading identification number for the qualifier that applies to the `topic_id`.',
                  `description`   varchar(100)         DEFAULT NULL COMMENT 'The text description of the `qualification_id`.',
                  `class`         varchar(15)          DEFAULT NULL COMMENT 'Indicates the importance of the qualification placed on the topic. Options:major, minor',
                  PRIMARY KEY (`qualifier_num`),
                  UNIQUE KEY `qualifier_num`            (`qualifier_num`),
                  KEY `qualifiers_pmid_topic_id_index`  (`pmid`,`topic_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
                """
        db.query(query)
        print('.... `qualifiers` table created')
        
        query = """CREATE TABLE IF NOT EXISTS `topics` (
                  `topic_num`    bigint(20) unsigned NOT NULL AUTO_INCREMENT,
                  `pmid`         int(11)             NOT NULL     COMMENT 'The PubMed identification number.',
                  `pub_date`     date                DEFAULT NULL COMMENT 'The full date on which the issue of the journal was published.',
                  `source`       varchar(15)         DEFAULT NULL COMMENT 'The type of topic. Options: `MeSH`, `chemical`, `publication`',
                  `description`  varchar(100)        DEFAULT NULL COMMENT 'The text description of the `topic_id`.',
                  `topic_id`     varchar(15)         NOT NULL     COMMENT 'The unique Medical Subject Heading (MeSH) identification number for this topic.',
                  `class`        varchar(15)         DEFAULT NULL COMMENT 'The importance of the `topic_id` for the paper assocated with the `pmid`. Options:major, minor.',
                  PRIMARY KEY (`topic_num`),
                  UNIQUE KEY `topic_num`            (`topic_num`),
                  KEY `topics_pmid_class_index`     (`pmid`),
                  KEY `topics_pub_date_index`       (`pub_date`),
                  KEY `topics_pmiddate_index`       (`pub_date`,`pmid`),
                  KEY `topics_description_index`    (`description`),
                  KEY `topics_topic_id_index`       (`topic_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
                """
        db.query(query)
        print('.... `topics` table created')

        # Affiliations Table
        query = """
        CREATE TABLE IF NOT EXISTS `affiliations` (
                  `affiliation_num`  bigint(20) unsigned NOT NULL AUTO_INCREMENT,
                  `pub_date`         date          DEFAULT NULL  COMMENT 'The full date on which the issue of the journal was published.',
                  `pmid`             int(11)       DEFAULT NULL  COMMENT 'The PubMed identification number.',
                  `first_name`       varchar(100)  DEFAULT NULL  COMMENT 'The first name of the author.',
                  `middle_name`      varchar(100)  DEFAULT NULL  COMMENT 'The midle name of the author.',
                  `last_name`        varchar(100)  DEFAULT NULL  COMMENT 'The last name of the author.',
                  `affiliation`      TEXT                        COMMENT 'The full affiliation string provided by PubMed.',
                  `department`       varchar(250)  DEFAULT NULL  COMMENT 'The inferred department of the author.',
                  `institution`      varchar(250)  DEFAULT NULL  COMMENT 'The inferred institution of the author.',
                  `location`         varchar(250)  DEFAULT NULL  COMMENT 'The inferred location of the author.',
                  `email`            varchar(250)  DEFAULT NULL  COMMENT 'The inferred email address of the author.',
                  `zipcode`          varchar(250)  DEFAULT NULL  COMMENT 'The inferred zipcode of the author.',
                  `country`          varchar(250)  DEFAULT NULL  COMMENT 'The inferred country of the author.',
                  `grid_id`          varchar(14)   DEFAULT NULL  COMMENT 'The inferred grid_id.',
                  `orcid_id`         varchar(50)   DEFAULT NULL  COMMENT 'The inferred ORCID id.',
                  PRIMARY KEY (`affiliation_num`),
                  UNIQUE KEY `affiliation_num`          (`affiliation_num`),
                  KEY `affiliations_pmid_index`         (`pmid`),
                  KEY `affiliations_pub_date_index`     (`pub_date`),
                  KEY `affiliations_pmiddate_index`     (`pub_date`,`pmid`),
                  KEY `affiliations_author_name_index`  (`last_name`,`first_name`),
                  FULLTEXT KEY `affiliation_index`      (`grid_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
            """
        # Publications
        db.query(query)
        print('.... `affiliations` table created')
        
        query = """CREATE TABLE IF NOT EXISTS `publications` (
                  `pmid`               int(11) NOT NULL COMMENT 'A PubMed unique identifier. This field is a 1- to 8-digit accession number with no leading zeros.',
                  `pub_date`           date DEFAULT NULL COMMENT 'The full date on which the issue of the journal was published.',
                  `pub_title`          text COMMENT 'The title of the journal article. The title is always in English; those titles originally published in a non-English language and translated for the title field are enclosed in square brackets.',
                  `country`            varchar(100) DEFAULT NULL COMMENT 'The journals country of publication. Valid values are those country names found in the Z category of the Medical Subject Headings (MeSH)',
                  `issn`               varchar(100) DEFAULT NULL COMMENT 'The International Standard Serial Number, an eight-character value that uniquely identifies the journal.',
                  `journal_issue`      varchar(100) DEFAULT NULL COMMENT 'The issue, part, or supplement of the journal in which the article was published.',
                  `journal_title`      varchar(300) DEFAULT NULL COMMENT 'The full journal title, taken from NLMs cataloging data following NLM rules for how to compile a serial name.',
                  `journal_title_abbr` varchar(200) DEFAULT NULL COMMENT 'The standard abbreviation for the title of the journal in which the article appeared.',
                  `journal_volume`     int(11) DEFAULT NULL COMMENT ' The volume number of the journal in which the article was published.',
                  `lang`               varchar(100) DEFAULT NULL COMMENT 'The language(s) in which an article was published. See https://www.nlm.nih.gov/bsd/language_table.html. for options',
                  `page_number`        varchar(200) DEFAULT NULL COMMENT 'The inclusive pages for the article.  The pagination can be entirely non-digit data.  Redundant digits are omitted.  Document numbers for electronic articles are also found here.',
                  PRIMARY KEY (`pmid`),
                  KEY `publications_pmid_index`          (`pmid`),
                  KEY `publications_pub_date_index`      (`pub_date`),
                  KEY `publications_pmiddate_index`      (`pub_date`,`pmid`),
                  KEY `publications_journal_title_index` (`journal_title`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        db.query(query)
        print('.... `publications` table created')

    ######################################################################
    # Checks if a dict satisfies a set of key, and value criteria
    ######################################################################  
    def extractFromPubmedData(self, flat_data, key_has = [], value_has = [], fetch_part = None ):
        
        try:
        
            data_elements = flat_data.keys()
            # See if this key matches the criteria 

            results = []

            for element in data_elements:

                # Key Critera
                key_critera = True
                for key in key_has:
                    if key not in element.lower():
                        key_critera = False 

                # See if the value matches this critera   
                value_criteria = True
                for value in value_has:
                    if value not in flat_data[element].lower():
                        value_critera = False

                if key_critera and value_criteria:
                    if fetch_part is not None:
                        results.append(flat_data['.'.join(element.split('.')[:-1] + [fetch_part])])
                    else:
                        results.append(flat_data[element])

            return list(set(results))
        except:
            return []


    ######################################################################
    # Inserts data into the database
    ######################################################################          
    def insertRow(self, table, columns, parameters, pmid = None, log_folder = 'ingest-pubmed', showtime = False,  db_insert=True):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
    
        if showtime == True:
            tic()
        
        # Make the log file directories (if they don't already exist)
        if log_folder is not None:
            if not os.path.isdir('logs/' + log_folder):
                os.mkdir('logs/' + log_folder)

            if not os.path.isdir('logs/' + log_folder + '/' + table):
                os.mkdir('logs/' + log_folder + '/' + table)

        # Construct the query we will execute to insert the row(s)
        keys       = ','.join(columns)
        values     = ','.join(['%s' for x in columns])
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """
                                 
        # Indicates if we should skip the insert - this is useful for testing things.
        if db_insert == False:
            #print(query)
            #print(parameters)
            #print('\n')
            return None, None
        
        insert_id = None
        try:
            insert_id = db.query(query,parameters)[0]['LAST_INSERT_ID()']            
            error = False

        except Exception as e:
            if log_folder is not None:
                location = 'logs/'+log_folder+'/' + table + '/error.log'
                append_write = 'a' if os.path.exists(location) else 'w' 
                f = open(location, append_write)
                f.write(str(pmid) + "|||" + str(e) + "," + "\n")
                f.close()

                error = True

        if showtime == True:
            #print(table)
            toc()
            
        return insert_id, error

    ######################################################################
    # Get the DOI from pubmed data
    ######################################################################  
    def getDoi(self, elocation):
        elocation =  [elocation] if isinstance(elocation, dict) else elocation
        _doi = [None]
        for location in elocation:
            if location.get('@EIdType') == 'doi' and location.get('@ValidYN') == 'Y':
                _doi = [location.get('#text')]
        return _doi[0]

    ######################################################################
    # Get the Publication Data from the pubmed data
    ######################################################################  
    def getPubDate(self, paper_json, paper_id):
        pubdate = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {}).get('Article',{}).get('Journal',{}).get('JournalIssue',{}).get('PubDate',{})
        year     = pubdate.get('Year')
        month    = 'Jan' if pubdate.get('Month') is None else pubdate.get('Month')
        day      = '1'   if pubdate.get('Day')   is None else pubdate.get('Day')
        dateval  = parse(f"{year}-{month}-{day}",) if year is not None else None
        return dateval

    ######################################################################   
    # Deletes the logs that records data processing
    ######################################################################   
    def purgeLogs(self, log_folder):
        try:
            print('....purging logs')
            shutil.rmtree('logs/' + log_folder) 
        except:
            print('....purge failed: this is probably because the log folder does not exist.')

    ######################################################################
    # Determines the set of pmids that have already been collected
    ######################################################################
    def _getCollectedDocuments(self, paper_list, starting_index):
        paper_ids, _collected  = [], []

        # Generate a set of paper pmids from the document_names.
        for i,paper in enumerate(paper_list[starting_index:]):
            paper_ids.append(paper.split('/')[-1].split('id-')[1].split('_')[0])

        # Find the pmids that 
        if paper_ids != []:
            _collected = db.query("""SELECT DISTINCT pmid FROM publications WHERE pmid IN({paper_list})""".format(paper_list = ','.join(paper_ids))) 

        #Create a dict that lists the collected documents
        collected = {}
        for a in _collected:
            collected[str(a['pmid'])] = True

        return collected    

    ############################################################################################
    # Returns the index of the paper we should start processing, given what we see in the logs
    ###########################################################################################
    def _getStartingIndex(self, log_location, paper_list):
        starting_index = 0
        p = subprocess.Popen(f"""tail -n 1 {log_location} """ , shell=True, stdout = subprocess.PIPE)
        last_processed = p.stdout.read().decode("utf-8")[:-1] 
        for i,x in enumerate(paper_list):
            if ('-' + last_processed + "_") in x:
                starting_index = i + 1
                print('We have completed', i+1, 'out of', len(paper_list), 'records so far...')
                break
        return starting_index

    ######################################################################
    # Extracts and parses author affiliations
    ######################################################################
    def _extractAffiliations(self, paper_json, paper_id): 
        columns, parameters = ['pub_date','pmid','last_name','first_name','middle_name','affiliation',
                               'department','institution','location','email',
                               'country','grid_id','orcid_id'], []
        
        _pubdate            = self.getPubDate(paper_json, paper_id)

        medline_citation  = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})
        author_list       = medline_citation.get('Article',{}).get('AuthorList', {}).get('Author',{})
        author_list       = [author_list] if not isinstance(author_list, list) else author_list
        _author_list      = [] 
        _affiliation_list = []
        
        for author in author_list:
            a = author.get('AffiliationInfo', {})
            
            affiliations =  [a] if not isinstance(a, list) else a 
            for i, affiliation in enumerate(affiliations):

                # Skip this if there is no author information.
                if author.get('LastName') is None and author.get('ForeName') is None:
                    continue

                _pmid        = paper_id
                _last_name   = str(author.get('LastName')) 
                forename     = str(author.get('ForeName')).split(' ')
                _first_name  = forename[0]
                _middle_name = ' '.join(forename[1:]) if len(forename) > 1 else None
                _affiliation = affiliation.get('Affiliation')
                
                
                if _affiliation is not None:
                    _email       = ';'.join(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', _affiliation))
                    
                    match        = re.search(r'\d{4}\-\d{4}\-\d{4}\-\d{3}(?:\d|X)', _affiliation)
                    _orcid_id    = match.group(0) if match is not None else None
                    
                    
                    _parsed_affil   = parse_affil(_affiliation)
                    #_grid_id       = match_affil(_affiliation)[0]['grid_id']
                    _grid_id        = None
                    
                    if _parsed_affil['institution'] is not None and _parsed_affil['department'] is not None:
                        _parsed_affil['institution'] = _parsed_affil['institution'].replace(_parsed_affil['department'],'')
                    
                    _country       = _parsed_affil['country']     if _parsed_affil['country']     != '' else None 
                    _department    = _parsed_affil['department']  if _parsed_affil['department']  != '' else None
                    _institution   = _parsed_affil['institution'] if _parsed_affil['institution'] != '' else None
                    _location      = _parsed_affil['location']    if _parsed_affil['location']    != '' else None
                else:
                    _email         = None 
                    _orcid_id      = None
                    _country       = None 
                    _department    = None
                    _institution   = None
                    _location      = None
                    _grid_id       = None
                    
                
                parameters.append([_pubdate, _pmid, _last_name, _first_name, _middle_name, _affiliation, 
                                   _department, _institution, _location, _email,
                                   _country, _grid_id, _orcid_id])

        # convert to list of lists
        if not any(isinstance(x, list) for x in parameters):
            parameters = [parameters]

        parameters = [x for x in parameters if x != []]
        return columns, parameters
    
    ######################################################################
    # Extracts the Abstract and Title from the pubmed document
    ######################################################################
    def _extractDocument(self, paper_json, paper_id):
        columns    = ['pmid','pub_date','content_order','content_type','content']
        _pubdate   =  self.getPubDate( paper_json, paper_id)
        
        # Format the data
        x  = flatten(paper_json, last_keys='',key_list=[], value_list=[])
        medline_citation = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})


        # Abstract
        abstract_candidates = [x[a] for a in x.keys() if ('abstracttext' in a.lower()) and (len(x[a].split()) > 1) and ('@Label' not in a.lower()) and ('@NlmCategory' not in a.lower())]
        _abstract           = ' '.join(abstract_candidates)
        if _abstract.isspace() or _abstract == '':
            _abstract = None

        # Title
        _title = self.extractFromPubmedData(flat_data = x, key_has=['PubmedArticleSet.PubmedArticle.MedlineCitation.Article.ArticleTitle'.lower()], value_has=[])
        if (len(_title) > 0) and (isinstance(_title, list)):
            candidates = [x for x in _title if not x.isnumeric() and len(x) > 10] 
            _title = candidates[0] if len(candidates) > 0 else None 

        
        parameters = [[ int(paper_id), _pubdate , 1 , 'title'    , _title], 
                      [ int(paper_id), _pubdate , 2 , 'abstract' , _abstract]
                     ]
        return columns, parameters

    ######################################################################
    # Extracts the various IDs from the pubmed data: PMC, NLP, ISSN, ETC.
    ######################################################################
    def _extractIdMap(self, paper_json, paper_id):
        columns    = ['pmid','pub_date','pmc_id','nlm_id','doi','issn_linking']
        _pubdate   =  self.getPubDate( paper_json, paper_id)
        
        
        medline_citation     = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})
        pubmed_data          = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('PubmedData',{})
        
        # Format the data
        x                = flatten(paper_json, last_keys='',key_list=[], value_list=[])
        parameters       = []

        # eLocation
        elocation = medline_citation.get('Article',{}).get('ELocationID',{})
        _location = self.getDoi(elocation)

        # Get the Pubmed Central ID
        pmc_candidates  = self.extractFromPubmedData( flat_data = x, key_has=['@IdType'.lower()], value_has=['pmc'],fetch_part='#text')
        _pmc            = [x for x in pmc_candidates if x[0:3] == "PMC"]
        _pmc = _pmc[0] if _pmc != [] else None

        # NLM and ISSN Linking IDS
        _nlmid       = self.extractFromPubmedData( flat_data = x, key_has=['nlmuniqueid'], value_has=[])
        _nlmid = _nlmid[0] if _nlmid != [] else None

        _issnLinking = self.extractFromPubmedData( flat_data = x, key_has=['issnlinking'], value_has=[])
        _issnLinking = _issnLinking[0] if _issnLinking != [] else None

        # Insert results into the database
        
        parameters = [ paper_id, _pubdate, _pmc, _nlmid, _location, _issnLinking]

        # convert to list of lists
        if not any(isinstance(x, list) for x in parameters):
            parameters = [parameters]

        parameters = [x for x in parameters if x != []]
        return columns, parameters
    
    ######################################################################
    # Extracts the grants information from the pubmed data
    ######################################################################
    def _extractGrants(self, paper_json, paper_id):
        columns     = ['grant_id','pmid','pub_date'] 
        _pubdate    =  self.getPubDate(paper_json, paper_id)
        
        # Format the data
        x = flatten(paper_json, last_keys='',key_list=[], value_list=[])
        parameters       = []

        _grantIDs   = self.extractFromPubmedData( flat_data = x, key_has=['grantid'], value_has=[])
        
        parameters  = []
        for grant in _grantIDs:
            parameters.append([grant, paper_id, _pubdate])

        # convert to list of lists
        if not any(isinstance(x, list) for x in parameters):
            parameters = [parameters]

        parameters = [x for x in parameters if x != []]
        return columns, parameters

    
    #######################################################################
    # Extraction information triples (subject, verb, object) from the data 
    #######################################################################    
    def _extractInformationFromDB(self, paper, paper_id, filter_results = True):
        
        import hashlib
        icols = ['pmid','pub_date','subject','relation','object','subject_hash','relation_hash','object_hash','confidence','sentence_number'] 
        ecols = ['pmid','pub_date','triple_hash','concept_type','concept_id','concept_name','sentence_number']
        
        # Get the Publication date
        _pubdate   =  paper['pub_date']
        _abstract  =  paper['content']        
    
        #Extract the triplets.
        triples  = t2g.processDocuments(text_set  = [_abstract],
                                           pmids  = [paper_id],
                                  filter_results  = filter_results)
        
        #Construct the parameters from the triplets
        iparams, eparams = [],[]
        for triple in triples:
            
            # Extract the confidence measure for the triple. 
            _confidence     = int(100*triple['confidence'])
            
            # Generate hash to uniquly identify paper entities 
            _subject_hash   = hashlib.md5(f"""{paper_id}{triple['subject']}""".encode('utf-8')).hexdigest()
            _object_hash    = hashlib.md5(f"""{paper_id}{triple['object']}""".encode('utf-8')).hexdigest()
            _relation_hash  = hashlib.md5(f"""{paper_id}{triple['relation']}""".encode('utf-8')).hexdigest()
            
            
            # Store the triple
            iparams.append([paper_id, _pubdate, triple['subject'], triple['relation'], triple['object'],_subject_hash,_relation_hash,_object_hash,_confidence, triple['sentence_number']])

            # Extract the entities, and store them
            for umls_concept_id, umls_canonical_name in triple['object_entity'].items():
                eparams.append([paper_id, _pubdate, _object_hash, 'object',umls_concept_id,umls_canonical_name,triple['sentence_number']])

            for umls_concept_id, umls_canonical_name in triple['subject_entity'].items():
                eparams.append([paper_id, _pubdate, _subject_hash, 'subject',umls_concept_id,umls_canonical_name,triple['sentence_number']])
                
            for umls_concept_id, umls_canonical_name in triple['relation_entity'].items():
                eparams.append([paper_id, _pubdate, _relation_hash, 'relation',umls_concept_id,umls_canonical_name,triple['sentence_number']])
                
        return icols, iparams, ecols, eparams


    
    #######################################################################  
    #
    #######################################################################    
    def _extractInformation(self, paper_json, paper_id, filter_results = True):
        
        import hashlib
        
        icols = ['pmid','pub_date','subject','relation','object','subject_hash','relation_hash','object_hash','confidence','sentence_number'] 
        ecols = ['pmid','pub_date','triple_hash','concept_type','concept_id','concept_name','sentence_number']
        
        # Get the Publication date
        _pubdate   =  self.getPubDate( paper_json, paper_id)
        
        # Format the data
        x  = flatten(paper_json, last_keys='',key_list=[], value_list=[])
        medline_citation = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})

        # Get the Abstract text
        abstract_candidates = [x[a] for a in x.keys() if ('abstracttext' in a.lower()) and (len(x[a].split()) > 1) and ('@Label' not in a.lower()) and ('@NlmCategory' not in a.lower())]
        _abstract           = ' '.join(abstract_candidates)
        if _abstract.isspace() or _abstract == '':
            _abstract = None        
    
        #Extract the triplets.
        triples  = t2g.processDocuments(text_set  = [_abstract],
                                           pmids  = [paper_id],
                                  filter_results  = filter_results)
        
        #Construct the parameters from the triplets
        iparams, eparams = [],[]
        for triple in triples:
            
            _subject_hash   = hashlib.md5(f"""{paper_id}{triple['subject']}""".encode('utf-8')).hexdigest()
            _object_hash    = hashlib.md5(f"""{paper_id}{triple['object']}""".encode('utf-8')).hexdigest()
            _relation_hash  = hashlib.md5(f"""{paper_id}{triple['relation']}""".encode('utf-8')).hexdigest()
            _confidence     = int(100*triple['confidence'])
            iparams.append([paper_id, _pubdate, triple['subject'], triple['relation'], triple['object'],_subject_hash,_relation_hash,_object_hash,_confidence, triple['sentence_number']])

            for umls_concept_id, umls_canonical_name in triple['object_entity'].items():
                eparams.append([paper_id, _pubdate, _object_hash, 'object',umls_concept_id,umls_canonical_name,triple['sentence_number']])

            for umls_concept_id, umls_canonical_name in triple['subject_entity'].items():
                eparams.append([paper_id, _pubdate, _subject_hash, 'subject',umls_concept_id,umls_canonical_name,triple['sentence_number']])
                
            for umls_concept_id, umls_canonical_name in triple['relation_entity'].items():
                eparams.append([paper_id, _pubdate, _relation_hash, 'relation',umls_concept_id,umls_canonical_name,triple['sentence_number']])
                
        return icols, iparams, ecols, eparams
        
    ######################################################################
    def _extractTopicsQualifiers(self, paper_json, paper_id):

        qcols  = ['pmid','pub_date','topic_id', 'qualifier_id', 'description', 'class']
        dcols  = ['pmid','pub_date','source', 'description', 'topic_id', 'class']
        _pubdate  =  self.getPubDate(paper_json, paper_id)
        
        # Medical Subject Headings -----------------------------------------------------------------
        medline_citation     = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})
        MeshHeadingList      = medline_citation.get('MeshHeadingList',{}).get('MeshHeading',{})
        MeshHeadingList      =  [MeshHeadingList] if isinstance(MeshHeadingList, dict) else MeshHeadingList
        _mesh = []
        dparams, qparams = [],[]

        for mesh in MeshHeadingList:
            # Get the descriptor information
            descriptor         = mesh.get('DescriptorName',{})
            _topic_id          = descriptor.get('@UI')
            _topic_class       = 'major' if descriptor.get('@MajorTopicYN',{}) == 'Y' else 'minor'     
            _topic_description = descriptor.get('#text') 

            if _topic_id is None:
                continue

            # Store the descriptor information
            dparams.append([paper_id, _pubdate, 'MeSH', _topic_description, _topic_id, _topic_class])

            # Get the qualifier information
            qualifiers = mesh.get('QualifierName') 
            if qualifiers is None:
                continue

            qualifiers =  [qualifiers] if not isinstance(qualifiers, list) else qualifiers
            for qualifier in qualifiers:
                # For each qualifier
                _qualifier_id          = qualifier.get('@UI')
                _qualifier_class        = 'major' if qualifier.get('@MajorTopicYN') == 'Y' else 'minor' 
                _qualifier_description = qualifier.get('#text') 

                #Store the qualifier information
                qparams.append([paper_id, _pubdate, _topic_id, _qualifier_id, _qualifier_description , _qualifier_class])


        # Chemicals------------------------------------------------------------------------         
        ChemicalList = medline_citation.get('ChemicalList',{}).get('Chemical',{})    
        ChemicalList = [ChemicalList] if isinstance(ChemicalList, dict) else ChemicalList
        parameters = []
        for chem in ChemicalList:
            if chem == {}:
                continue
            _topic_id          = chem.get('NameOfSubstance',{}).get('@UI')
            _topic_class       = None
            _topic_description = chem.get('NameOfSubstance',{}).get('#text') 
            dparams.append([paper_id, _pubdate, 'MeSH', _topic_description, _topic_id, _topic_class])

        # Publication Info------------------------------------------------------------------------
        try:
            publicationtypelist  = medline_citation.get('Article',{}).get('PublicationTypeList',{}).get('PublicationType',{})
        except:
            publicationtypelist  = {}

        publicationtypelist =  [publicationtypelist] if isinstance(publicationtypelist, dict) else publicationtypelist
        parameters = []
        for pub in publicationtypelist:
            if pub == {}:
                continue
            _topic_id          = pub.get('@UI')
            _topic_class       = None
            _topic_description = pub.get('#text')   
            dparams.append([paper_id, _pubdate, 'MeSH', _topic_description, _topic_id, _topic_class])

        # convert to list of lists
        if not any(isinstance(x, list) for x in dparams):
            dparams = [dparams]
        dparams = [x for x in dparams if x != []]

        # convert to list of lists
        if not any(isinstance(x, list) for x in qparams):
            qparams = [qparams]
        qparams = [x for x in qparams if x != []]

        return dcols, dparams, qcols, qparams

    ######################################################################
    def _extractCitations(self, paper_json, paper_id):
        columns   = ['pmid','citedby', 'citation_date']
        
        medline_citation     = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})
        pubmed_data          = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('PubmedData',{})

        
        try:
            Reference = pubmed_data.get('ReferenceList',{}).get('Reference') 
        except:
            Reference = []
            
        Reference = [] if Reference is None else Reference
            
        _pubdate  =  self.getPubDate(paper_json, paper_id)

        parameters = []
        for ref in Reference:

            # If this is a string - pass.
            if isinstance(ref, str):
                continue

            articlelist = ref.get('ArticleIdList',{}).get('ArticleId')
            if not isinstance(articlelist, list):
                articlelist = [articlelist]

            for ar in articlelist: 
                if ar is None:
                    continue
                IdType = ar.get('@IdType')
                if IdType == 'pubmed':
                    cited_by = ar.get('#text')
                    parameters.append([int(cited_by), int(paper_id), _pubdate])
        

        # convert to list of lists
        if not any(isinstance(x, list) for x in parameters):
            parameters = [parameters]
        parameters = [x for x in parameters if x != []]
        return columns, parameters

    ######################################################################
    def _extractPublication(self, paper_json, paper_id):
        columns = [ 'country', 'issn', 'journal_issue', 'journal_title', 'journal_title_abbr', 'journal_volume', 'lang', 'page_number', 'pmid', 'pub_date', 'pub_title']
    
        medline_citation    = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})
        pubmed_data         = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('PubmedData',{})
        journal             = medline_citation.get('Article',{}).get('Journal',{})
        x                   = flatten(paper_json, last_keys='',key_list=[], value_list=[])            
        
        _title              = self.extractFromPubmedData(flat_data = x, key_has=['PubmedArticleSet.PubmedArticle.MedlineCitation.Article.ArticleTitle'.lower()], value_has=[])
        _title              = _title[0] if (len(_title) > 0) else None
        _pubdate            =  self.getPubDate( paper_json, paper_id)
        _country            = medline_citation.get('MedlineJournalInfo',{}).get('Country')
        _issn               = journal.get('ISSN',{}).get('#text')
        _journal_volume     = journal.get('JournalIssue',{}).get('Volume')
        _journal_issue      = journal.get('JournalIssue',{}).get('Issue')
        _journal_title      = journal.get('Title')
        _journal_title_abbr = journal.get('ISOAbbreviation') 
        _page_number        = medline_citation.get('Article',{}).get('Pagination',{}).get('MedlinePgn')
        
        _language           = medline_citation.get('Article',{}).get('Language')
        if isinstance(_language, list):
            if len(_language) > 0:
                _language = _language[0]


        parameters = [ _country, _issn, _journal_issue, _journal_title, _journal_title_abbr,_journal_volume, _language, _page_number, paper_id, _pubdate, _title]

        # convert to list of lists
        if not any(isinstance(x, list) for x in parameters):
            parameters = [parameters]
        parameters = [x for x in parameters if x != []]

        return columns, parameters    

    
    ######################################################################
    #
    ######################################################################  
    def processPapers(self, paper_list=['/location/of/paper1.json'], log_folder='ingest-pubmed', showtime=False, db_insert=True, purge_logs = False, prevent_duplication = True, batch_size = 50000, limit_to_tables = ['affiliations','documents','id_map','grants','topics','qualifiers','citations','publications']):

            
        #----------------------------------------------------------------------------
        # Create the Log Folders
        #----------------------------------------------------------------------------
        # Purge if required
        self.purgeLogs(log_folder)     if purge_logs == True                      else None
        
        # Create log folders
        os.mkdir('logs')               if not os.path.isdir('logs')               else None
        os.mkdir('logs/' + log_folder) if not os.path.isdir('logs/' + log_folder) else None
        
        # Specify the log locations
        log_location, error_location, nodata_location = ['logs/' + log_folder +  x for x in ['/processed.log',  '/error.log', '/nodata.log']]

        #----------------------------------------------------------------------------
        # Determine which files have already been processed.
        #----------------------------------------------------------------------------
        # Figure out where we were when processing this file list using the logs.
        starting_index = self._getStartingIndex(log_location, paper_list)
        
        # Get the list of Documents that were already collected from the database `publications` table.
        collected      = self._getCollectedDocuments(paper_list, starting_index) if (prevent_duplication == True) else {}

        #----------------------------------------------------------------------------
        # For each paper in the archive that we have not already processed.
        #----------------------------------------------------------------------------
        data = {'affiliations' : {'columns'    : [], 'parameters' : [] },
                'documents'    : {'columns'    : [], 'parameters' : [] },  
                'id_map'       : {'columns'    : [], 'parameters' : [] },
                'grants'       : {'columns'    : [], 'parameters' : [] },
                'topics'       : {'columns'    : [], 'parameters' : [] },
                'qualifiers'   : {'columns'    : [], 'parameters' : [] },
                'citations'    : {'columns'    : [], 'parameters' : [] },
                'publications' : {'columns'    : [], 'parameters' : [] },
                'triples'      : {'columns'    : [], 'parameters' : [] },
                'concepts'     : {'columns'    : [], 'parameters' : [] }
                }
        
        for i,paper in enumerate(paper_list[starting_index:]):
            
            error = False
            tic() if (showtime == True) else None
                     
            # Get the Pubmed ID from the filename
            paper_id  = paper.split('/')[-1].split('id-')[1].split('_')[0]
            
            # If this pmid has been processed before, then skip it.       
            if (prevent_duplication == True) and (collected.get(paper_id) is not None):
                continue

            #----------------------------------------------------------------
            # Extract fields from the paper
            #----------------------------------------------------------------
            
            # Get the paper, and a flattened version of it.
            with open(paper) as read_file:
                paper_json = json.load(read_file)
            
            try:
                medline_citation     = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('MedlineCitation', {})
                pubmed_data          = paper_json.get('PubmedArticleSet', {}).get('PubmedArticle', {}).get('PubmedData',{})
            except:
                append_write = 'a' if os.path.exists(nodata_location) else 'w'
                f = open(nodata_location, append_write)
                f.write(str(paper_id) + "\n")
                f.close()
                continue

            #----------------------------------------------------------------
            # POPULATE TABLE: Affiliations
            #----------------------------------------------------------------
            if 'affiliations' in limit_to_tables:
                columns, parameters = self._extractAffiliations(paper_json, paper_id)
                data['affiliations']['columns']     = columns
                data['affiliations']['parameters'] += parameters 
    
            #----------------------------------------------------------------
            # POPULATE TABLE: documents
            #----------------------------------------------------------------    
            if 'documents' in limit_to_tables:
                columns, parameters = self._extractDocument(paper_json, paper_id)
                data['documents']['columns']     = columns
                data['documents']['parameters'] += parameters 
            
            #----------------------------------------------------------------
            # POPULATE TABLE: id_map
            #----------------------------------------------------------------        
            if 'id_map' in limit_to_tables:
                columns, parameters = self._extractIdMap(paper_json, paper_id)
                data['id_map']['columns']     = columns
                data['id_map']['parameters'] += parameters 

            #----------------------------------------------------------------
            # POPULATE TABLE: grants
            #----------------------------------------------------------------                
            if 'grants' in limit_to_tables:
                columns, parameters = self._extractGrants(paper_json, paper_id)
                data['grants']['columns']     = columns
                data['grants']['parameters'] += parameters 
            
            #----------------------------------------------------------------
            # POPULATE TABLE: topics and qualifiers
            #----------------------------------------------------------------
            if 'topics' in limit_to_tables:
                dcols, dparams, qcols, qparams    = self._extractTopicsQualifiers(paper_json, paper_id)
                data['topics']['columns']         = dcols
                data['topics']['parameters']     += dparams 
                data['qualifiers']['columns']     = qcols
                data['qualifiers']['parameters'] += qparams 
            
            #----------------------------------------------------------------
            # POPUALTE TABLE: citations
            #----------------------------------------------------------------
            if 'citations' in limit_to_tables:
                columns, parameters = self._extractCitations(paper_json, paper_id)
                data['citations']['columns']     = columns
                data['citations']['parameters'] += parameters if parameters is not [[]] else None
            
            #----------------------------------------------------------------
            # POPULATE TABLE: Publications
            #----------------------------------------------------------------
            if 'publications' in limit_to_tables:
                columns, parameters = self._extractPublication(paper_json, paper_id)
                data['publications']['columns']     = columns
                data['publications']['parameters'] += parameters if parameters is not [[]] else None

                
            #----------------------------------------------------------------
            # POPULATE TABLE: Information and entities
            #----------------------------------------------------------------
            if 'triples' in limit_to_tables:
                icols, iparams, ecols, eparams     = self._extractInformation(paper_json, paper_id)
                data['triples']['columns']         = icols
                data['triples']['parameters']     += iparams if iparams is not [[]] else None
                data['concepts']['columns']        = ecols
                data['concepts']['parameters']    += eparams if eparams is not [[]] else None
                
                
            #----------------------------------------------------------------
            # INSERT THE RESULTS
            #----------------------------------------------------------------
            if (i % batch_size) == 0:
                print('batch complete', i)
                for table, val in data.items():
                    self.insertRow(table = table,  columns    = val['columns'], 
                                                   parameters = val['parameters'], 
                                                   log_folder = log_folder, 
                                                   db_insert  = db_insert)
                    data[table]['columns'], data[table]['parameters']  = [], []     

            #----------------------------------------------------------------
            # Log that a paper was successfully processed.
            #----------------------------------------------------------------
            append_write = 'a' if os.path.exists(log_location) else 'w'
            f = open(log_location, append_write)
            f.write(str(paper_id) + "\n")
            f.close()
            
            # INSERT THE LAST BATCH    
            if showtime == True:
                toc()

        # Complete the Last Batch
        print('Completing Final Batch')        
        for table, val in data.items():
            
            self.insertRow(table = table,  columns    = val['columns'], 
                                           parameters = val['parameters'], 
                                           log_folder = log_folder, 
                                           db_insert  = db_insert)
            data[table]['columns'], data[table]['parameters']    = [], []



    ######################################################################
    # paper_list should be formatted like [{text:, pmid:,pub_date:},{text:, pmid:, pub_date:} ...]
    ######################################################################  
    def extractInformation(self, paper_list=[], db_insert=True, batch_size = 50000, filter_results = True, limit_to_tables = ['triples','concepts']):
  
        # Get the list of Documents that were already collected from the database `publications` table.
        collected = {}

        #----------------------------------------------------------------------------
        # For each paper in the archive that we have not already processed.
        #----------------------------------------------------------------------------
        data = {
                'triples'      : {'columns'    : [], 'parameters' : [] },
                'concepts'     : {'columns'    : [], 'parameters' : [] }
                }
        
        for i,paper in enumerate(paper_list):
            error = False
                     
            #----------------------------------------------------------------
            # POPULATE TABLE: Information and entities
            #----------------------------------------------------------------
            if 'triples' in limit_to_tables:
                icols, iparams, ecols, eparams     = self._extractInformationFromDB(paper, paper['pmid'], filter_results)
                data['triples']['columns']         = icols
                data['triples']['parameters']     += iparams if iparams is not [[]] else None
                data['concepts']['columns']        = ecols
                data['concepts']['parameters']    += eparams if eparams is not [[]] else None
                
                
            #----------------------------------------------------------------
            # INSERT THE RESULTS
            #----------------------------------------------------------------
            if (i % batch_size) == 0:
                print('batch complete', i)
                for table, val in data.items():
                    self.insertRow(table = table,  columns    = val['columns'], 
                                                   parameters = val['parameters'],
                                                   log_folder = None,
                                                   db_insert  = db_insert ) 
                    
                    data[table]['columns'], data[table]['parameters']  = [], []     

        # Complete the Last Batch
        print('Completing Final Batch')        
        for table, val in data.items():
            self.insertRow(table = table,  columns    = val['columns'], 
                                           parameters = val['parameters'],
                                           log_folder = None,
                                           db_insert  = db_insert)
            data[table]['columns'], data[table]['parameters']    = [], []


