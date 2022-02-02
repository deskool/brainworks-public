from utils.generalPurpose.generalPurpose import *
from utils.database.database import database
from configuration.config import config
from dateutil.parser import parse
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
import math
import numpy as np
import shutil
import os, ssl


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


exporter_primary_keys =  { 'abstracts'    : ['application_id', 'version'],
                           'publications' : ['pmid'],
                           'projects'     : ['application_id', 'version'],
                           'patents'      : ['patent_id', 'project_id'],
                           'afilliations' : ['pmid','author_name']}


class exporter:
    
    def __init__(self):
        self.base_url       = ''
        self.write_location = '' 
        self.document_list  = [] 
        
  
    ################################################################################################
    # This Function collects files pasted on the NIH ExPORTER website
    #-----------------------------------------------------------------------------------------------
    # INPUTS 
    # save_directory      <String> - Indicates the directory where we will save the downloaded data. 
    # replace_existing    <Bool>   - When True, all previously downloaded files are replaced.   
    #-----------------------------------------------------------------------------------------------
    # OUTPUTS
    # See the ExPORTER/ directory for information on the files 
    ################################################################################################                    
    def collect(self, replace_existing = False, limit_to_tables = []):
        
        save_directory = config['data_directory'] + 'ExPORTER/'
        requires_update = []
        
        # For each of the Exporter tabs
        print('------------------------------------------------')
        print('Downloading data from https://exporter.nih.gov/ ')
        print('.... files will be saved to', save_directory )
        print('------------------------------------------------')
        for index, tab in enumerate(['projects','abstracts','publications','patents','clinical_studies','link_tables']):
            
            # Limits to tables provided (if any)
            if limit_to_tables != []:
                if tab not in limit_to_tables:
                    continue
            
            # Fetch the HTML
            base_url      = 'https://exporter.nih.gov/'
            req_url       = base_url + 'ExPORTER_Catalog.aspx?index=' + str(index)
            exporter_html = requests.get(req_url)
            print('downloading `' + tab + '`CSV data from ' + req_url + ' ...')
            
            # Find all the CSV Files
            matches       = findMatches(regular_expression = """href="[^\s'"`]+.zip""", text = exporter_html.text)
            matches       = [match[6:] for match in matches if 'CSV' in match]
            matches       = [ match if 'https://' in match else base_url + match for match in matches]

            # To keep track of new files we've added to the collection
            newly_downloaded_files      = 0
            previously_downloaded_files = 0
            
            # For some files, we will always want to replace existing
            _replace_existing = replace_existing
            if tab in ['patents', 'clinical_studies']:
                # remove these directories.
                if os.path.isdir(save_directory + tab):
                    shutil.rmtree(save_directory + tab) 
            
            # For each CSV File
            for match in matches:
                
                # Get the Filename
                filename = match.split('/')[-1]
                
                # The publications are special in that they
                # also contain author affiliation files.
                if (tab == 'publications') and ('_AFFLNK_' in filename):
                    tab = 'affiliations'
                if (tab == 'affiliations') and ('_AFFLNK_' not in filename):
                    tab = 'publications'
                
                # These appendicies are not applicable
                if tab == 'projects':
                    if ('_DUNS_' in filename) or ('_PRJFUNDING_' in filename):
                        continue
                
                # Make the save directory       
                if not os.path.isdir(save_directory):
                    os.mkdir(save_directory)
                
                save_dir = save_directory + tab 
                if not os.path.isdir(save_dir):
                    os.mkdir(save_dir)
                
                # Save it in the raw
                save_dir = save_directory + tab  + '/raw/'
                if not os.path.isdir(save_dir):
                    os.mkdir(save_dir)   
                    
                # Download the File
                if (os.path.exists(save_dir + filename)) and (_replace_existing == False):
                    previously_downloaded_files += 1
                    continue
                else:    
                    wget.download(match, out=save_dir)
                    newly_downloaded_files += 1
                    requires_update += list(set(requires_update + [tab]))
        
            requires_update = list(set(requires_update))   
            # Display download statistics to the users
            print('....', previously_downloaded_files, '/', (previously_downloaded_files + newly_downloaded_files), 'previously downloaded')
            if newly_downloaded_files > 0:
                print('.... downloading', newly_downloaded_files, 'new files')
            
        
                 
        print('------------------------------------------------')
        print(' Unzipping data                                 ')
        print('------------------------------------------------')
        # For each of the subdirectories in the save_directory
        data_path = glob.glob(save_directory + '*')
        for folder in data_path:
    
            # check if updates are required.
            folder_name = folder.split('/')[-1] 
            # Limits to tables provided (if any)
            if limit_to_tables != []:
                if folder_name not in limit_to_tables:
                    continue
            
            print(folder_name,'...')
            
            if folder_name not in requires_update:
                print('.... No updates required')
                continue
            else:
                print('.... Starting update')


            # For each of the .zip files in the raw director.
            file_paths = glob.glob(folder +'/raw/*.zip')
            for file in file_paths:
                
                filename = file.split('/')[-1] 
                filename = '.'.join(filename.split('.')[:-1])    
                # Create a folder to store the unzipped files
                containing_path = '/'.join(file.split('/')[:-1])
                extract_path    = containing_path + '/../unzipped'
                if not os.path.isdir(extract_path):
                    os.mkdir(extract_path)

                # Unzip the files
                #print(extract_path + '/' + filename + '.csv')
                if (os.path.exists(extract_path + '/' + filename + '.csv')) and (_replace_existing == False):
                    continue
                else:    
                    with ZipFile(file, 'r') as zipObj:
                        # Extract all the contents of zip file in current directory
                        zipObj.extractall(path = extract_path)


        print('------------------------------------------------')
        print(' Converting to JSON                             ')
        print('------------------------------------------------')                        
        data_path = glob.glob(save_directory + '*')

        # For each of the folders of data in the data path
        for folder in data_path:
            
            # check if updates are required.
            folder_name = folder.split('/')[-1] 
            
            # Limits to tables provided (if any)
            if limit_to_tables != []:
                if folder_name not in limit_to_tables:
                    continue   
                    
            print(folder_name,'...')
        
            # Check if an update is required.
            if folder_name not in requires_update:
                print('.... No updates required')
                continue
            else:
                print('.... Starting update')
                
            # Create the save directory
            savedir = folder + '/json'
            if not os.path.isdir(savedir):
                os.mkdir(savedir)

            #-----------------------------------------------------
            # For all the unzipped files...
            #-----------------------------------------------------
            file_paths = glob.glob(folder +'/unzipped/*')
            line_import_errors = 0
            for file in file_paths:

                filename = file.split('/')[-1] 
                filename = '.'.join(filename.split('.')[:-1])   

                # 
                if (os.path.exists(savedir + '/' + filename + '.jsonl')) and (replace_existing == False):
                    continue
                
                # Initialize the output file as blank
                with open(savedir + '/' + filename + '.jsonl', 'w') as outfile:
                    outfile.write('')

                # Open the output file- the 'a' means append
                outfile = open(savedir + '/' + filename + '.jsonl', "a")    
            
                # Get the year from the file name
                year = findMatches("[0-9]{4}",file)
                year = None if year == [] else year[0]

                # Print the file that 
                errors = 0

                #-----------------------------------------------------
                # Open each of the files
                #-----------------------------------------------------
                with open(file, 'r', errors='replace') as read_file:

                    #-----------------------------------------------------
                    # Process the first row - the header
                    #-----------------------------------------------------
                    json_lines, count   = [], 0
                    for line in reader(read_file):
                        count += 1

                        # If this is the first line, this is a header.
                        if count == 1:
                            headers = line
                            continue

                       # Check for errors
                        if len(headers) != len(line):
                            line_import_errors += 1
                            continue

                        # Package the line as JSON
                        json_line  = {'year': year}
                        for i,header in enumerate(headers):
                            json_line[header] = line[i]   

                        #Store the JSON
                        json_lines.append(json_line)               

                    #-----------------------------------------------------
                    # Saving Batch
                    #-----------------------------------------------------
                    # Convert the data and save it to disk
                    for entry in json_lines:
                        json.dump(entry, outfile)
                        outfile.write('\n')
                    # Clear the batch
                    json_lines = []
                
                
                outfile.close()
                print('.... Line import errors')
                
    ################################################################################################
    # This Function characterizes the ExPORTER Data Download and stores the results in ExPORTER/stats/
    #-----------------------------------------------------------------------------------------------
    # INPUTS 
    # replace_existing    <Bool>   - When True, all previously downloaded files are replaced.   
    #-----------------------------------------------------------------------------------------------
    # OUTPUTS
    # See ExPORTER/stats/ for a set of files that characterize the downloaded data.
    ################################################################################################  
    def characterizeData(self, replace_existing = False, limit_to_tables = []):
        folder_path = glob.glob(config['data_directory'] + 'ExPORTER/' + '*')
        
        print('------------------------------------------------')
        print(' Characterizing ExPORTER Data                   ')
        print('------------------------------------------------')      
        
        #----------------------------------------------    
        # For each folder of data...
        #----------------------------------------------
        for folder in folder_path:

            # Get the folder name
            folder_name = folder.split('/')[-1]; 
            if '.' in folder_name:
                folder_name = '.'.join(folder_name.split('.')[:-1])

            if limit_to_tables != []:
                if folder_name not in limit_to_tables:
                    continue
            
            # Get the data path
            data_path = glob.glob(folder + '/json/*')
            data_info = {}

            # We do not want to do anything with the data statistics
            if folder_name == 'stats':
                continue
            
            print('Processing', folder, '...')
    
            # Figure out which files we have already computed stats for
            stats_computed = [folder.split('/')[-1] for folder in glob.glob(config['data_directory'] + 'ExPORTER/stats/' + '*')]
            this_stat_name = folder_name + '.json'
            if (this_stat_name in stats_computed) and (replace_existing == False):
                print('.... Skipping - stats were previously computed')
                continue
            else:
                print('.... Computing stats - this may take a while')
            
            #----------------------------------------------
            # For each data file in the folder...
            #----------------------------------------------
            for data in data_path:
                data_name = data.split('/')[-1]; 
                data_name = '.'.join(data_name.split('.')[:-1])

                #----------------------------------------------
                # For each line in the data file...
                #----------------------------------------------
                with open(data) as f:
                    for line in f:

                        json_line = json.loads(line)

                        #----------------------------------------------
                        # Get the line statistics
                        #----------------------------------------------
                        for real_key,val in json_line.items():

                            key = real_key.lower().replace(' ','_').replace('.','_')

                            #-----------------------------------------------
                            # If this is a new key, add it to the dict
                            #-----------------------------------------------
                            if data_info.get(key) == None:
                                data_info[key] = {'max_value_size' : 0,
                                                  'data_type'      : {'INT'      : 0,
                                                                      'VARCHAR'  : 0,
                                                                      'FLOAT'    : 0,
                                                                      'DATE'     : 0
                                                                     },
                                                  'column_name'   : ''
                                                 }

                            #----------------------------------------------
                            # Generate the column name from he key
                            #-----------------------------------------------
                            if data_info[key]['column_name'] == '':
                                data_info[key]['column_name'] = key.lower().replace(' ','_').replace('.','_')

                            #-----------------------------------------------
                            # Get the max_value_size
                            #-----------------------------------------------
                            if val is not None:
                                if data_info[key]['max_value_size'] < len(val): 
                                    data_info[key]['max_value_size'] = len(val)

                            #-----------------------------------------------
                            # Get the data_type 
                            #-----------------------------------------------
                            if val is not None:
                                if representsInt(val):
                                    data_info[key]['data_type']['INT'] += 1
                                elif representsFloat(val):
                                    data_info[key]['data_type']['FLOAT'] += 1
                                elif representsDatetime(val,  fuzzy=False):
                                    data_info[key]['data_type']['DATE'] += 1
                                else:
                                    data_info[key]['data_type']['VARCHAR'] += 1

            #-----------------------------------------------------
            # Saving Batch
            #-----------------------------------------------------   
            if not os.path.isdir('data/ExPORTER/stats'):
                os.mkdir('data/ExPORTER/stats')

            outfile = open('data/ExPORTER/stats/' + folder_name + '.json', "w")    
            json.dump(data_info, outfile)  
            outfile.close()

                     
    ################################################################################################
    # This Function generates MySQL Tables using the ExPORTER Data Characteristics or static defintions.
    #-----------------------------------------------------------------------------------------------
    # INPUTS 
    # replace_existing    <Bool>   - When True, all previously downloaded files are replaced.   
    #-----------------------------------------------------------------------------------------------
    # OUTPUTS
    # Execute a query "SHOW TABLES" in MySQL to see the results of this function
    ################################################################################################              
    def generateTables(self, replace_existing = False, limit_to_tables = [], use_static_definitions = True):

        db = database()
        data_path = glob.glob(config['data_directory'] + 'ExPORTER/stats/*')
        create_table_queries = {}
        
        if use_static_definitions:
            
            # Abstracts Table
            create_table_queries['abstracts'] = """CREATE TABLE `abstracts` (
                                      `year`            int(11) DEFAULT NULL COMMENT 'The year that the grant abstract was published',
                                      `application_id`  int(11) NOT NULL COMMENT 'A unique identifier of the project record',
                                      `abstract_text`   text COMMENT 'An abstract of the research being performed in the project. The abstract is supplied to NIH by the grantee.',
                                      `source`          varchar(200) DEFAULT NULL COMMENT 'Indicates where this information was collected from.',
                                      `version`         int(11) NOT NULL DEFAULT '0' COMMENT 'Says the version of the data from the `source` field',
                                      PRIMARY KEY (`application_id`,`version`),
                                      FULLTEXT KEY `abstract_text_index` (`abstract_text`)
                                    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
                                """

            # Link Tables
            create_table_queries['link_tables'] = """CREATE TABLE `link_tables` (
                                      `year`           int(11) DEFAULT NULL COMMENT 'The year that the link was established',
                                      `pmid`           int(11) DEFAULT NULL COMMENT 'The PubMed identification number',
                                      `project_number` varchar(100) DEFAULT NULL COMMENT 'An identifier of the research project either cited in the publication acknowledgements section or reported to have provided support in the NIH Public Access manuscript submission system.',
                                      `source`         varchar(200) DEFAULT NULL COMMENT 'Indicates the source of this information.',
                                      `version`        int(11) DEFAULT '0' COMMENT 'Indicates the version of this information collected from the `source`.',
                                      KEY `link_tables_pmid_index` (`pmid`),
                                      KEY `link_tables_project_number_index` (`project_number`),
                                      KEY `link_tables_year_index` (`year`)
                                    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
                                """
            # Patents Table
            create_table_queries['patents'] = """CREATE TABLE `patents` (
                                  `year`            int(11) DEFAULT NULL COMMENT 'Indicates the year this patent was published.',
                                  `patent_id`       int(11) NOT NULL COMMENT 'A unique alpha-numeric code which identifies a federal patent.',
                                  `patent_title`    varchar(300) DEFAULT NULL COMMENT 'Title of the patent as it appears in the US Patent and Trademark Office database of issued patents.',
                                  `project_id`      varchar(100) NOT NULL COMMENT 'An identifier of the research project acknowledged as supporting development of the patent.',
                                  `patent_org_name` varchar(100) DEFAULT NULL COMMENT 'The name of the educational institution, research organization, business, or government agency receiving the patent.',
                                  `source`          varchar(200) DEFAULT NULL COMMENT 'Indicates the source of this information.',
                                  `version`         int(11) DEFAULT '0' COMMENT 'Indicates the version of this information collected from the `source`.',
                                  PRIMARY KEY (`patent_id`,`project_id`),
                                  FULLTEXT KEY `patents_patent_title_index` (`patent_title`)
                                ) ENGINE=InnoDB DEFAULT CHARSET=latin1
                                """
            
            # Projects Table
            create_table_queries['projects'] = """CREATE TABLE `projects` (
                                  `year` int(11) DEFAULT NULL COMMENT 'The year that the project was funded.',
                                  `application_id` int(11) NOT NULL COMMENT 'A unique identifier of the project record in the ExPORTER database.',
                                  `activity` varchar(100) DEFAULT NULL COMMENT ' A 3-character code identifying the grant, contract, or intramural activity through which a project is supported.  Within each funding mechanism, NIH uses 3-character activity codes (e.g., F32, K08, P01, R01, T32, etc.) to differentiate the wide variety of research-related programs NIH supports.',
                                  `administering_ic` varchar(100) DEFAULT NULL COMMENT 'Administering Institute or Center - A two-character code to designate the agency, NIH Institute, or Center administering the grant.',
                                  `application_type` int(11) DEFAULT NULL COMMENT 'A one-digit code to identify the type of application funded. See `application_types` table for descriptions of the codes.',
                                  `arra_funded` varchar(100) DEFAULT NULL COMMENT 'Y indicates a project supported by funds appropriated through the American Recovery and Reinvestment Act of 2009.',
                                  `award_notice_date` varchar(100) DEFAULT NULL COMMENT 'Award notice date or Notice of Grant Award (NGA) is a legally binding document stating the government has obligated funds and which defines the period of support and the terms and conditions of award.',
                                  `budget_start` varchar(100) DEFAULT NULL COMMENT 'The date when a project’s funding for a particular fiscal year begins.',
                                  `budget_end` varchar(100) DEFAULT NULL COMMENT 'The date when a project’s funding for a particular fiscal year ends.',
                                  `cfda_code` varchar(100) DEFAULT NULL COMMENT 'Federal programs are assigned a number in the Catalog of Federal Domestic Assistance (CFDA), which is referred to as the CFDA code. The CFDA database helps the Federal government track all programs it has domestically funded.',
                                  `core_project_num` varchar(100) DEFAULT NULL COMMENT ' An identifier for each research project, used to associate the project with publication and patent records. This identifier is not specific to any particular year of the project. It consists of the project activity code, administering IC, and serial number (a concatenation of Activity, Administering_IC, and Serial_Number).',
                                  `ed_inst_type` varchar(100) DEFAULT NULL COMMENT 'Generic name for the grouping of components across an institution who has applied for or receives NIH funding. The official name as used by NIH is Major Component Combining Name.',
                                  `foa_number` varchar(100) DEFAULT NULL COMMENT 'The number of the funding opportunity announcement, if any, under which the project application was solicited.  Funding opportunity announcements may be categorized as program announcements, requests for applications, notices of funding availability, solicitations, or other names depending on the agency and type of program. Funding opportunity announcements can be found at Grants.gov/FIND',
                                  `full_project_num` varchar(100) DEFAULT NULL COMMENT 'Commonly referred to as a grant number, intramural project, or contract number.  For grants, this unique identification number is composed of the type code, activity code, Institute/Center code, serial number, support year, and (optional) a suffix code to designate amended applications and supplements.',
                                  `funding_ics` varchar(300) DEFAULT NULL COMMENT 'The NIH Institute or Center(s) providing funding for a project are designated by their acronyms (see Institute/Center acronyms).  Each funding IC is followed by a colon (:) and the amount of funding provided for the fiscal year by that IC.  Multiple ICs are separated by semicolons (;).  Project funding information is available only for NIH, CDC, FDA, and ACF projects.',
                                  `funding_mechanism` varchar(100) DEFAULT NULL COMMENT 'The major mechanism categories used in NIH Budget mechanism tables for the President’s budget. Extramural research awards are divided into three main funding mechanisms: grants, cooperative agreements and contracts. A funding mechanism is the type of funded application or transaction used at the NIH. Within each funding mechanism NIH includes programs. Programs can be further refined by specific activity codes.',
                                  `fy` int(11) DEFAULT NULL COMMENT 'The fiscal year appropriation from which project funds were obligated.',
                                  `ic_name` varchar(100) DEFAULT NULL COMMENT 'Full name of the administering agency, Institute, or Center. ',
                                  `nih_spending_cats` text COMMENT 'Congressionally-mandated reporting categories into which NIH projects are categorized.  Available for fiscal years 2008 and later.  Each project’s spending category designations for each fiscal year are made available the following year as part of the next President’s Budget request.  See the Research, Condition, and Disease Categorization System for more information on the categorization process.',
                                  `org_city` varchar(100) DEFAULT NULL COMMENT 'The city in which the business office of the grantee organization or contractor is located.  Note that this may be different from the research performance site.  For all NIH intramural projects, Bethesda, MD is used.',
                                  `org_country` varchar(100) DEFAULT NULL COMMENT 'The country in which the business office of the grantee organization or contractor is located.  Note that this may be different from the research performance site.',
                                  `org_dept` varchar(100) DEFAULT NULL COMMENT 'The departmental affiliation of the contact principal investigator for a project, using a standardized categorization of departments. Names are available only for medical school departments.',
                                  `org_district` int(11) DEFAULT NULL COMMENT 'The congressional district in which the business office of the grantee organization or contractor is located.  Note that this may be different from the research performance site.',
                                  `org_duns` varchar(100) DEFAULT NULL COMMENT 'This field may contain multiple DUNS Numbers separated by a semi-colon. The Data Universal Numbering System is a unique nine-digit number assigned by Dun and Bradstreet Information Services, recognized as the universal standard for identifying and keeping track of business worldwide.',
                                  `org_fips` varchar(100) DEFAULT NULL COMMENT 'The country code of the grantee organization or contractor as defined in the Federal Information Processing Standard.',
                                  `org_ipf_code` int(11) DEFAULT NULL COMMENT 'The Institution Profile (IPF) number is an internal NIH identifier that uniquely identifies and associates institutional information within NIH electronic systems. The NIH assigns an IPF number after the institution submits its request for registration.',
                                  `org_name` varchar(100) DEFAULT NULL COMMENT 'The name of the educational institution, research organization, business, or government agency receiving funding for the grant, contract, cooperative agreement, or intramural project.',
                                  `org_state` varchar(100) DEFAULT NULL COMMENT 'The state in which the business office of the grantee organization or contractor is located.  Note that this may be different from the research performance site.',
                                  `org_zipcode` int(11) DEFAULT NULL COMMENT 'The zip code in which the business office of the grantee organization or contractor is located.  Note that this may be different from the research performance site.',
                                  `phr` text COMMENT 'Submitted as part of a grant application, this statement articulates a projects potential to improve public health.',
                                  `pi_ids` varchar(300) DEFAULT NULL COMMENT 'A unique identifier for each of the project Principal Investigators. Each PI in the RePORTER database has a unique identifier that is constant from project to project and year to year, but changes may be observed for investigators that have had multiple accounts in the past, particularly for those associated with contracts or sub-projects.',
                                  `pi_names` varchar(600) DEFAULT NULL COMMENT 'The name(s) of the Principal Investigator(s) designated by the organization to direct the research project.',
                                  `program_officer_name` varchar(100) DEFAULT NULL COMMENT 'An Institute staff member who coordinates the substantive aspects of a contract from planning the request for proposal to oversight.',
                                  `project_start` varchar(100) DEFAULT NULL COMMENT 'The start date of a project.  For subprojects of a multi-project grant, this is the start date of the parent award. ',
                                  `project_end` varchar(100) DEFAULT NULL COMMENT 'The current end date of the project, including any future years for which commitments have been made.  For subprojects of a multi-project grant, this is the end date of the parent award.  Upon competitive renewal of a grant, the project end date is extended by the length of the renewal award. ',
                                  `project_terms` text COMMENT 'Prior to fiscal year 2008, these were thesaurus terms assigned by NIH CRISP indexers.  For projects funded in fiscal year 2008 and later, these are concepts that are mined from the projects title, abstract, and specific aims using an automated text mining tool.',
                                  `project_title` varchar(200) DEFAULT NULL COMMENT 'Title of the funded grant, contract, or intramural (sub)project.',
                                  `serial_number` int(11) DEFAULT NULL COMMENT 'A six-digit number assigned in serial number order within each administering organization.  ',
                                  `study_section` varchar(100) DEFAULT NULL COMMENT ' A designator of the legislatively-mandated panel of subject matter experts that reviewed the research grant application for scientific and technical merit.',
                                  `study_section_name` varchar(200) DEFAULT NULL COMMENT 'The full name of a regular standing Study Section that reviewed the research grant application for scientific and technical merit.  Applications reviewed by panels other than regular standing study sections are designated by Special Emphasis Panel.',
                                  `subproject_id` varchar(100) DEFAULT NULL COMMENT 'A unique numeric designation assigned to subprojects of a `parent` multi-project research grant.',
                                  `suffix` varchar(100) DEFAULT NULL COMMENT 'A suffix to the grant application number that includes the letter `A` and a serial number to identify an amended version of an original application and/or the letter `S` and serial number indicating a supplement to the project.',
                                  `support_year` int(11) DEFAULT NULL COMMENT 'The year of support for a project, as shown in the full project number.  For example, a project with number 5R01GM0123456-04 is in its fourth year of support.',
                                  `direct_cost_amt` varchar(100) DEFAULT NULL COMMENT ' Total direct cost funding for a project from all NIH Institute and Centers for a given fiscal year. Costs are available only for NIH awards funded in FY 2012 onward. Direct cost amounts are not available for SBIR/STTR awards.',
                                  `indirect_cost_amt` varchar(100) DEFAULT NULL COMMENT 'Total indirect cost funding for a project from all NIH Institute and Centers for a given fiscal year. Costs are available only for NIH awards funded in FY 2012 and onward. Indirect cost amounts are not available for SBIR/STTR awards.',
                                  `total_cost` varchar(100) DEFAULT NULL COMMENT 'Total project funding from all NIH Institute and Centers for a given fiscal year.',
                                  `total_cost_sub_project` varchar(100) DEFAULT NULL COMMENT 'Applies to subproject records only. Total funding for a subproject from all NIH Institute and Centers for a given fiscal year. Costs are available only for NIH awards.',
                                  `source` varchar(200) DEFAULT NULL COMMENT 'The source of this information.',
                                  `version` int(11) NOT NULL DEFAULT '0' COMMENT 'The version of the data pulled from the `source`',
                                  PRIMARY KEY (`application_id`,`version`),
                                  KEY `projects_core_project_num_index` (`core_project_num`),
                                  KEY `projects_total_cost_index` (`total_cost`),
                                  FULLTEXT KEY `projects_project_title_index` (`project_title`),
                                  FULLTEXT KEY `projects_project_terms_index` (`project_terms`)
                                ) ENGINE=InnoDB DEFAULT CHARSET=latin1                
                """
        else:
            # To generate the tables, we must first characterize the data.
            self.characterizeData(limit_to_tables = limit_to_tables)

            print('------------------------------------------------')
            print(' Inferrring MySQL Table Structure from Data     ')
            print('------------------------------------------------')     
            # Connect to the Database
            db = database()

            data_path = glob.glob(config['data_directory'] + 'ExPORTER/stats/*')



            #----------------------------------------------
            # For each data file in the folder...
            #----------------------------------------------
            for data in data_path:

                # Get the Table name
                data_name = data.split('/')[-1]; 
                table_name = '.'.join(data_name.split('.')[:-1]) 

                if limit_to_tables != []:
                    if table_name not in limit_to_tables:
                        continue

                query = """ CREATE TABLE {table_name} (""".format(table_name = table_name)

                # Open the stats file
                f = open(data,)
                json_data = json.load(f)

                print('Generating CREATE TABLE statement for', table_name)        

                # Get the Column names for the table
                column_names = list(json_data.keys())
                for column in column_names:

                    # Get the data type of the column
                    data_types = json_data[column]['data_type']
                    data_type =max(data_types, key=data_types.get)

                    # If 10% or more of the data is varchar, then cast it to varchar
                    varchar_proportion = json_data[column]['data_type']['VARCHAR'] / ( json_data[column]['data_type'][data_type] + json_data[column]['data_type']['VARCHAR'] + 1)
                    if varchar_proportion > 0.1:
                        data_type = 'VARCHAR'

                    # Round up to the nearest 100
                    json_data[column]['max_value_size'] =  int(math.ceil(json_data[column]['max_value_size'] / 100.0)) * 100

                    # Add the query block
                    if json_data[column]['max_value_size'] > 1000:
                        data_type = 'TEXT'

                    query += """{column} {data_type}""".format(column=json_data[column]['column_name'], data_type=data_type)
                    if data_type == 'VARCHAR':
                        query += '({max_value_size})'.format(max_value_size = json_data[column]['max_value_size'])

                    query += ','

                #
                query += """source varchar(200), version INT DEFAULT 0"""

                # If it's the primary key column:
                if exporter_primary_keys.get(table_name) is not None:
                    primary_keys = ','.join(exporter_primary_keys[table_name])
                    query += ', PRIMARY KEY (' + primary_keys + ')'

                # End the create table statement
                query += ')'
                create_table_queries[table_name] = query

        #----------------------------------------------
        # CREATE THE TABLES 
        #----------------------------------------------
        all_tables = db.listTables()
        print('------------------------------------------------')
        print(' Creating ExPORTER Tables                       ')
        print('------------------------------------------------')    
        for table, create_table in create_table_queries.items():
            
            #if table != 'patents':
            #    continue
            
            # If we've asked to replace the table, or if this is patents
            if (replace_existing == True):
                print('....dropping', table)
                drop_table = """DROP TABLE IF EXISTS {table}""".format(table = table)
                db.query(drop_table)
                print('...creating', table)
                db.query(create_table)
            
            elif table in all_tables:
                print('....`' + table + '` table already exists; skipping creation')
            else:
                print('...Creating Table `' + table + '`')
                db.query(create_table)


    ################################################################################################
    # Imports the data from json files into the database
    #-----------------------------------------------------------------------------------------------
    # INPUTS 
    # replace_existing    <Bool>   - When True, all previously downloaded files are replaced.   
    # exlcude_data        <list>   - the list of tables you want to ignore.
    #-----------------------------------------------------------------------------------------------
    # OUTPUTS
    # When this function is complete, the data will have loaded into the database.
    ################################################################################################   
    def importData(self, replace_existing = False, exclude_data=['stats','clinical_studies'], limit_to_tables = ['abstracts', 'projects', 'patents', 'link_tables','publications'], batch_size = 5000):
        #skip_until = 'RePORTER_PRJABS_C_FY1991'
        #skip_flag = True

        
        print('------------------------------------------------')
        print(' Importing Data into SQL Database               ')
        print('------------------------------------------------')    
        # Connect to the Database
        db = database()

        # Get the names of all files already imported.
        print('Collecting list of files previously imported')
        print('.... This may take a while depending on the size of your database')
        files_already_imported = db.listDataSourceFile(tables = limit_to_tables)
         
        folder_path = glob.glob(config['data_directory'] + 'ExPORTER/' + '*')
        errors = 0
        
        #----------------------------------------------    
        # For each folder of data...
        #----------------------------------------------
        for folder in folder_path:

            # Get the folder name
            folder_name = folder.split('/')[-1]; 
            if '.' in folder_name:
                folder_name = '.'.join(folder_name.split('.')[:-1])

                
            if limit_to_tables != []:
                if folder_name not in limit_to_tables:
                    continue
                
                
            # Get the data path
            data_path = glob.glob(folder + '/json/*')
            data_info = {}
            
            # Sort the data_path
            data_list = [d.split('/')[-1].lower() for d in data_path]
            sindex    = list(np.argsort(data_list))
            data_path =  [data_path[sindex[i]] for i in range(len(data_path))]
            #print(data_path)
            #data_path.reverse()
            
            # There is some data we may not want to import
            if folder_name in exclude_data:
                print('skipping folder', folder_name)
                continue

            # Get the information on the table we want to insert into
            table_info = db.getTableInfo(folder_name) 

            print('Importing data into', folder_name)
            print('.... (previously imported data will be skipped unless replace_existing is True)')
            
            # If this is the patents table, everything must be wiped.
            if folder_name == 'patents':
                print('Deleting patents - these records are replaced, not augmented...')
                db.query("DELETE FROM patents")
            
            #----------------------------------------------
            # For each data file in the folder...
            #----------------------------------------------
            for data in data_path:
                
                # Get the name of the data file.
                data_name = data.split('/')[-1]; 
                data_name = '.'.join(data_name.split('.')[:-1])
                
                # Get the version number of the data
                if (data_name.split('_')[-1][0:2] == 'FY' ) or (data_name.split('_')[-1] == 'new') or  (data_name.split('_')[-1].lower() == 'all'):
                    version_number = 0
                else:
                    version_number = int(data_name.split('_')[-1])
                        
                # Let's see if this data exists or not: 
                if (data_name in files_already_imported) and (replace_existing == False) and ('PATENTS' not in data_name):
                    continue
                else:
                    print('....Importing', data_name)

                #----------------------------------------------
                # For each line in the data file...
                #----------------------------------------------
                with open(data) as f:
                    query_values = ''
                    parameters    = []
                    for ii, line in enumerate(f):
                        json_line = json.loads(line)

                        #----------------------------------------------
                        # Get the line statistics
                        #----------------------------------------------
                        keys, values  = '', ''
                        for real_key,value in json_line.items():

                            # Get the Keys
                            key   = real_key.lower().replace(' ','_').replace('.','_')

                            # Get the data type
                            data_type = table_info[key]['data_type']                 

                            # If this is an int/float, cast non-friendly data to None
                            if data_type == 'int':
                                if not representsInt(value):
                                    value = None

                            if value == '':
                                value = None

                            if value is not None: 
                                value = value.encode("ascii", "ignore")

                            # If this is a date, parse to SQL format
                            if data_type == 'date':
                                try:
                                    value = parse(value, fuzzy=False)
                                except:
                                    errors += 1
                                    if errors % 500 == 0:
                                        print(errors)
                                    value = None

                            parameters += [value]
                            values    += '%s' + ',' 
                            keys      += key  + ','
                        
                        # Finish off by noting the source
                        keys       += 'source' + ','
                        values     += '%s'     + ','
                        parameters += [data_name]
                        
                        #... and the version number
                        keys       += 'version'
                        values     += '%s'
                        parameters += [version_number]
                        
                        query_values += f"""({values}),"""
                        
                        # Insert the batch of data
                        if ((ii % batch_size) == 0) and (ii != 0):
                            query = """INSERT IGNORE INTO {table_name} ({keys}) 
                                       VALUES {query_values}""".format(table_name = folder_name, keys = keys, query_values = query_values[:-1])
                            db.query(query,parameters)
                            query_values = ''
                            parameters   = []
                    # Insert the last batch    
                    if query_values != '':
                        query = """INSERT IGNORE INTO {table_name} ({keys}) 
                                    VALUES {query_values}""".format(table_name = folder_name, keys = keys, query_values = query_values[:-1])
                        db.query(query,parameters)