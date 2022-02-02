#######################################################################################
# BRAINWORKS - Information Extraction Pipeline
#######################################################################################
# Pulls all papers from 1990 to 2021, one month at a time from a database
# and passes these papers to the information extraction pipelines. Please note, 
# you do not need to call the database to use the information extraction piepline.
#######################################################################################
import re 
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir  = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from utils.database.database import database
db = database()

from utils.documentCollector.pubmed import pubmed
pm = pubmed()

########################################################################################

########################################################################################
year_start,year_end = 1990,2021
process_month       = int(sys.argv[1])
months_total        = 12*(year_end - (year_start-1)) + 1
process_month       = months_total - process_month

# For each year
for year in range(year_end,(year_start-1),-1):
    
    # For each month
    for month in range(12,0,-1):
        if process_month == (12*(year - (year_start-1)) + month - 12):
            print('Processing...', year, month)
            
            # Pull the publication data from that month
            data = db.query(f"""SELECT content, pmid, pub_date
                                FROM   documents
                                WHERE  content_type  = 'abstract'
                                  AND YEAR(pub_date)  = {year}
                                  AND MONTH(pub_date) = {month}
                            """)
            
            # Run the information extraction pipeline
            pm.extractInformation(paper_list     = data,
                                  db_insert      = True,
                                  batch_size     = 1000,
                                  filter_results = True
                                  )

