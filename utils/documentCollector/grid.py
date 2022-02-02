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
import glob
import csv
import itertools

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

class grid:
    
    def __init__(self):
        self.base_url = 'https://grid.ac/downloads'
                     
    def updateGRID(self):
        self.collect()
        self.generateTables()
        self.ingestData()
    
    
    def collect(self, replace_existing = False, limit_to_tables = []):
        save_directory  = config['data_directory'] + 'GRID/'
        requires_update = []

        # For each of the Exporter tabs
        print('------------------------------------------------')
        print('Downloading latest GRID file from ' + self.base_url)
        print('.... files will be saved to', save_directory )
        print('------------------------------------------------')

        # Fetch the HTML to get the latest file...
        exporter_html  = requests.get(self.base_url)
        matches        = findMatches(regular_expression = """href="[^\s'"`]+files\/\d+""", text = exporter_html.text)
        latest_file    = matches[0][6:]

        # Make the save directory for the raw files       
        os.mkdir(save_directory)                if not os.path.isdir(save_directory) else None
        os.mkdir(save_directory + '/raw/')      if not os.path.isdir(save_directory + '/raw/') else None
        os.mkdir(save_directory + '/unzipped/') if not os.path.isdir(save_directory + '/unzipped/') else None
            
        # Make sure we han't downloaded this before.
        if (os.path.exists(save_directory + '/raw/' + 'grid.zip')) and (replace_existing == False):
            print('.... Skipping download: we already have this file')
            return

        # Download the file
        wget.download(latest_file, out=save_directory + '/raw/' + 'grid.zip')

        # Unzip the file
        with ZipFile(save_directory + '/raw/' + 'grid.zip', 'r') as zipObj:
            zipObj.extractall(path = save_directory + '/unzipped/')

            
    def ingestData(self):

        # For each of the Exporter tabs
        print('------------------------------------------------')
        print('Importing Latest GRID Data ')
        print('------------------------------------------------')
        
        def byrow_imper(lod, keylist):
            # imperative/procedural approach
            lol = []
            for row in lod:
                row2 = []
                for key in keylist:
                    row2.append(row[key])
                lol.append(row2)
            return lol


        db = database(); db.database = 'grid'


        res = {'labels'        : {'columns' : ['grid_id','iso639','label']},
               'types'         : {'columns' : ['grid_id', 'type']},
               'relationships' : {'columns' : ['grid_id','relationship_type','related_grid_id']},
               'links'         : {'columns' : ['grid_id', 'link']},
               'institutes'    : {'columns' : ['grid_id','name','wikipedia_url','established']},
               'aliases'       : {'columns' : ['grid_id','alias']},
               'external_ids'  : {'columns' : ['grid_id','external_id_type','external_id']},
               'acronyms'      : {'columns' : ['grid_id','acronym']},
               'addresses'     : {'columns' : ['grid_id','lat','lng','postcode','is_primary','city','state','state_code','country','country_code','geonames_city_id']}
              }; 


        for key,val in res.items():
            table    = key
            
            print('.... importing', table)
            
            location = f"""{config['data_directory']}/GRID/unzipped/full_tables/{key}.csv"""
            with open(location) as f:
                a = []
                for row in csv.DictReader(f, skipinitialspace=True):
                    rval = {k : None for k in res[key]['columns'] }
                    for k,v in row.items():
                        if v != '':
                            rval[k] = v
                    a.append(rval) 
                columns    = res[key]['columns']
                parameters = byrow_imper(a,res[key]['columns'])


            # Construct the query we will execute to insert the row(s)
            keys       = ','.join(columns)
            values     = ','.join(['%s' for x in columns])
            query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """

            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))

            # Indicates if we should skip the insert - this is useful for testing things. 
            db.query(query,parameters)        
        
        
        
    def generateTables(self):
        
        db = database(); db.database = 'grid'
        db.query("""CREATE DATABASE IF NOT EXISTS grid""")
         
        print('------------------------------------------------')
        print(' Creating GRID Tables                           ')
        print('------------------------------------------------') 
        
        db.query("""DROP TABLE IF EXISTS `labels`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `labels` (
                              `grid_id`              varchar(14)   COMMENT 'The unique identifier for the institution.',
                              `iso639`               varchar(3)    DEFAULT NULL  COMMENT 'The country code of the institution.',
                              `label`                varchar(200)  DEFAULT NULL  COMMENT 'The name of the institution',  
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "Names and country codes of the grid institutions.";
        """
        db.query(query)
        print('.... `labels` table created')
        
        db.query("""DROP TABLE IF EXISTS `types`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `types` (
                              `grid_id`  varchar(14)  COMMENT 'The unique identifier for the institution.',
                              `type`     varchar(12)  DEFAULT NULL  COMMENT 'The type of the institution: Company, Education, Nonprofit, etc.',
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "The type of the GRID entry: Education, Government, Nonprofit, etc.";
        """
        db.query(query)
        print('.... `types` table created')
        
        db.query("""DROP TABLE IF EXISTS `relationships`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `relationships` (
                              `grid_id`            varchar(14)  COMMENT 'The unique identifier for the institution.',
                              `relationship_type`  varchar(10)  DEFAULT NULL  COMMENT 'The nature of the relationship between the grid_id pair in this row',
                              `related_grid_id`    varchar(14)  DEFAULT NULL  COMMENT 'The unique identifier for the realted institution.',
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "The relationships between the GRID entries.";
        """
        db.query(query)
        print('.... `relationships` table created')
        
        
        
        db.query("""DROP TABLE IF EXISTS `links`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `links` (
                              `grid_id`            varchar(14)   COMMENT 'The unique identifier for the institution.',
                              `link`               varchar(200)  DEFAULT NULL  COMMENT 'the website of the institution,',
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "links to the web URLs of the institutions.";
        """
        db.query(query)
        print('.... `links` table created')
        
        
        db.query("""DROP TABLE IF EXISTS `institutes`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `institutes` (
                              `grid_id`              varchar(14)   COMMENT 'The unique identifier for the institution.',
                              `name`                 varchar(200)  DEFAULT NULL COMMENT 'The name of the institution.',
                              `wikipedia_url`        varchar(500)  DEFAULT NULL  COMMENT 'The wikipedia URL of the institution.', 
                              `established`          varchar(10)   DEFAULT NULL  COMMENT 'The year that the institution was established.',
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "Names and wikipedia details of the grid institutions.";
        """
        db.query(query)
        print('.... `institutes` table created')
        
        db.query("""DROP TABLE IF EXISTS `aliases`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `aliases` (
                              `grid_id`              varchar(14)   COMMENT 'The unique identifier for the institution.',
                              `alias`                varchar(200)  DEFAULT NULL  COMMENT 'The alias of the institution',  
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "Alias names for the grid institutions grid institutions.";
        """
        db.query(query)
        print('.... `aliases` table created')
        
        
        
        db.query("""DROP TABLE IF EXISTS `external_ids`;""")
        query = """
        CREATE TABLE IF NOT EXISTS `external_ids` (
                              `grid_id`              varchar(14)    COMMENT 'The unique identifier for the institution.',
                              `external_id_type`     varchar(14)    DEFAULT NULL COMMENT 'The type of the external id',
                              `external_id`          varchar(50)    DEFAULT NULL  COMMENT 'The external id',  
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT "The external identifiers of the institutions.";
        """
        db.query(query)
        print('.... `external_ids` table created')
        
        
        
        db.query("""DROP TABLE IF EXISTS `addresses`""")
        query = """
        CREATE TABLE IF NOT EXISTS `addresses` (
        `grid_id` 			varchar(14)   COMMENT 'The unique identifier for the institution.',
        `lat`     			float         DEFAULT NULL	COMMENT 'The latitude of the institution.',				
        `lng`	  			float		  DEFAULT NULL	COMMENT 'The longitude of the institution',
        `postcode`	    	varchar(20)	  DEFAULT NULL	COMMENT 'The postal code of the institution',
        `is_primary`	    varchar(5)	  DEFAULT NULL	COMMENT 'true/false flag that indicates if this is the primary address for this institution.',
        `city`		    	varchar(50)	  DEFAULT NULL	COMMENT 'The name of the city where the institution is.',
        `state`	        	varchar(50)   DEFAULT NULL	COMMENT 'The name of the state where the institution is.',
        `state_code`		varchar(10)	  DEFAULT NULL	COMMENT 'The state abbreviation',
        `country`       	varchar(50)   DEFAULT NULL  COMMENT 'The name of the country where the institution is.',
        `country_code`		varchar(5)    DEFAULT NULL  COMMENT 'The country abbreviation.',
        `geonames_city_id`  int           DEFAULT NULL  COMMENT 'The geonames city id',
         KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT "Alias names for the grid institutions grid institutions.";
        """
        db.query(query)
        print('.... `addresses` table created')
        
        # -----------------------------------------------
        db.query("""DROP TABLE IF EXISTS `acronyms`""")
        query = """
        CREATE TABLE IF NOT EXISTS `acronyms` (
                              `grid_id`              varchar(14)  COMMENT 'The unique identifier for the institution.',
                              `acronym`              varchar(50)  DEFAULT NULL  COMMENT 'The acronym of the institution',  
                               KEY (`grid_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COMMENT "Acronyms for the grid institutions grid institutions.";
        """
        db.query(query)
        print('.... `acronyms` table created')