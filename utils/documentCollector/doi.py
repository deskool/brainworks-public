###########################################################
# THIS CODE IS STILL UNDER DEVELOPMENT
# It will pull the .pdf file associated with a DOI
# and process using GROBID
###########################################################
import requests
from bs4 import BeautifulSoup
url  = 'https://doi.org/' + '10.1007/s00134-014-3406-5'
html = requests.get(url).text
soup = BeautifulSoup(html,  'html.parser')