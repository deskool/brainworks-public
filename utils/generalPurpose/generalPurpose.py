# Flattens a JSON File
from dateutil.parser import parse
import os
import glob
import time
from pathlib import Path

_start_time = time.time()

def tic():
    global _start_time 
    _start_time = time.time()

def toc():
    t_sec = round(time.time() - _start_time)
    (t_min, t_sec) = divmod(t_sec,60)
    (t_hour,t_min) = divmod(t_min,60) 
    print('Time passed: {}hour:{}min:{}sec'.format(t_hour,t_min,t_sec))


# Returns the contents of a directory
def getDirectoryContents(data_path, extension='*'):
#     data_groups = glob.glob(data_path + '**/*.' + extension, recursive = True)
    data_groups = [str(path) for path in Path(data_path).rglob('*.' + extension)]
    return data_groups   

def generateDateDirectory(write_location, date):
        # Generate the root directory
        if not os.path.isdir(write_location):
            os.mkdir(write_location)

        if date is not None:
            # Make the date component of the directory
            if not os.path.isdir(write_location + '/' + date['year']):
                os.mkdir(write_location + '/' + date['year'])
            if not os.path.isdir(write_location + '/' + date['year'] + '/' + date['month']):
                os.mkdir(write_location + '/' + date['year'] + '/' + date['month'])
            if not os.path.isdir(write_location + '/' + date['year'] + '/' + date['month'] + '/' + date['day']):
                os.mkdir(write_location + '/' + date['year'] + '/' + date['month'] + '/' + date['day'])

        # Update the write_location
        write_location = write_location + '/' + date['year'] + '/' + date['month'] + '/' + date['day']
        return write_location


# Returns True if string can be interpreted as an Int
def representsInt(s):
    if s is None:
        return False
    try: 
        int(s)
        return True
    except ValueError:
        return False

# Returns True if string can be interpreted as an Float
def representsFloat(s):    
    if s is None:
        return False
    
    try:
        float(s)
        return True
    except ValueError:
        return False

# Returns True if string can be interpreted as an Datetime
def representsDatetime(s,  fuzzy=False):
    if s is None:
        return False
    
    try: 
        parse(s, fuzzy=fuzzy)
        return True
    except:
        return False


def flatten(my_dict, last_keys='',key_list=[], value_list=[]):    
    if isinstance(my_dict, dict):
        for key, value in my_dict.items():
            this_key = last_keys + '.' + key
            if isinstance(value, dict):
                flatten(my_dict[key],this_key,key_list,value_list)
            elif isinstance(value,list):
                flatten(my_dict[key],this_key,key_list,value_list)
            elif value == None:
                key_list.append(this_key[1:])
                value_list.append('None')
            else:
                key_list.append(this_key[1:])
                value_list.append(value)
    
    if isinstance(my_dict, list):
        for i in range(len(my_dict)):
            this_key = last_keys + '_' + str(i) + '_'
            if isinstance(my_dict[i], dict):
                flatten(my_dict[i],this_key,key_list,value_list)
            elif isinstance(my_dict[i],list):
                flatten(my_dict[i],this_key,key_list,value_list)
            elif my_dict[i] == None:
                key_list.append(this_key[1:])
                value_list.append('None')
            else:
                key_list.append(this_key[1:])
                value_list.append(my_dict[i])
    
    return dict(zip(key_list, value_list))


def extractFromFlatJson(flat_data, key_has = [], value_has = [], fetch_part = None ):
#label = extractFromPubmedData(flat_x, key_has    = ['label','@language'], 
#                                      value_has  = ['en'], 
#                                      fetch_part = '@value')

    data_elements = flat_data.keys()
    # See if this key matches the criteria 

    results = []
    valid_keys = {}
    for element in data_elements: 
        # Key Critera
        valid_keys[element] = True
        for key in key_has:
            if key not in element:
                valid_keys[element] = False

    
    valid_values = {}
    for element in data_elements:    
        if valid_keys[element]:
            
            # Value Criteria  
            valid_values[element] = True
            for value in value_has:
                if value not in str(flat_data[element]):
                    valid_values[element] = False
                   
            if valid_values[element]:
                if fetch_part is not None:
                    results.append(flat_data['.'.join(element.split('.')[:-1] + [fetch_part])])
                else:
                    results.append(flat_data[element])

    return list(set(results))

# Uses a RegEx to find all matches in a document.
def findMatches(regular_expression, text):
    import re
    
    results            = [ {"indicies":m.span(), "match":m.group() } for m in re.finditer(regular_expression,text)];
    matches            = []; [matches.append(m['match']) for m in results];
    return matches