import json
import random
from functools import wraps

import requests
import pandas as pd
import numpy as np


def add_exception_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            raise RuntimeError(f"Exception while executing {func.__name__}") from exc

    return wrapper


@add_exception_context
def testquery(url, db_eng, datatype, retrieveby, filters, request_method = 'post'):
    

    assert isinstance(filters, (str, dict)), "filters must be a json string or a dictionary"

    requestbody = {
        "datatype": datatype,
        "retrieve": retrieveby,
        "form": json.dumps(filters) if isinstance(filters, dict) else filters
    }

    print('requestbody')
    print(requestbody)

    resp = requests.post(url, data=requestbody) if request_method == 'post' else requests.get(url, data=requestbody)
    response = resp.json()

    returned_data = response.get('data')    
    nrows = response.get('numrows')
    api_record_count = nrows
    sql = response.get('sql')



    
    report = {
        "request_body_json": json.dumps(requestbody),
        "endpoint_tested": url,
        "request_method": request_method,
        "data_returned": returned_data is not None,
        "api_record_count" : api_record_count
    }

    return report




# To be used in the generate_random_filterparams
@add_exception_context
def getrandomvals(data):
    print("in getrandomvals")
    print("data")
    print(data)
    # Remove keys with empty lists
    cleaned_data = {k: v for k, v in data.items() if (v and k != 'sql') }
    
    # Randomly select one key
    selected_key = random.choice(list(cleaned_data.keys()))
    
    # Randomly select any number of values from the selected key's list with a bias towards lower numbers
    if cleaned_data[selected_key]:
        list_length = len(cleaned_data[selected_key])
        # Generate a biased number of items to select, favoring lower numbers
        # Here, we use exponential distribution for biasing towards lower numbers
        num_items_to_select = np.random.exponential(scale=list_length/5)
        num_items_to_select = int(max(1, min(num_items_to_select, list_length)))  # Ensure it's within valid range
        
        selected_values = random.sample(cleaned_data[selected_key], num_items_to_select)
    else:
        selected_values = []

    return {selected_key: selected_values}


@add_exception_context
def generate_random_filterparams(
    datatype = 'Chemistry',
    initial_request_endpoint = 'https://data.sccwrp.org/bightquery/api/initFilters.php',
    interactive_endpoint = 'https://data.sccwrp.org/bightquery/api/updateFilters.php',
    retrieveby = 'whole', 
    max_iterations = 3
):
    all_retrieves = ['whole','individual','grouped']
    all_datatypes = ['Chemistry','BenthicInfauna','FishAbundance','SQOScores','SQOSummary','SQOCondition']
    
    assert max_iterations > 2, "max_iterations must be greater than 2"
    assert retrieveby in all_retrieves, f"retrieveby arg must be in {','.join(all_retrieves)}"
    assert datatype in all_datatypes, f"datatype arg must be in {','.join(all_datatypes)}"

    # initialize variables
    filterparams = dict()
    resp = dict()

    requestbody =  {
        "datatype": datatype,
        "retrieve": retrieveby
    }

    for i in range(random.randint(2,max_iterations)):
        if i == 0:

            # initial call to interactive sql
            print("initial_request_endpoint")
            print(initial_request_endpoint)
            resp = requests.get(initial_request_endpoint, data=requestbody)

            print("resp")
            print(resp)

            filterparams = resp.json()

            # This is how the json response was set up - not using specific names, but rather numbers
            # these are what they represent when retrieving by whole datasets
            filterparams['stratum'] = filterparams.pop('field1')
            filterparams['region'] = filterparams.pop('field2')
            filterparams['samplingorganization'] = filterparams.pop('field3')
            filterparams['surveyyear'] = filterparams.pop('field33')
            filterparams['stationid'] = filterparams.pop('field7')
        else:

            if (retrieveby == 'whole') and (filterparams.get('stationid') is not None):
                del filterparams['stationid']
                
            print('filterparams')
            print(filterparams)

            lookup_elements = getrandomvals(filterparams)



            requestbody['lookup_elements'] = json.dumps(lookup_elements)

            resp = requests.post(interactive_endpoint, data=requestbody)

            
            filterparams = resp.json()
            filterparams['stratum'] = filterparams.pop('field1')
            filterparams['region'] = filterparams.pop('field2')
            filterparams['samplingorganization'] = filterparams.pop('field3')
            filterparams['surveyyear'] = filterparams.pop('field8')
            
        
    return {k:v for k,v in filterparams.items() if ((k!='sql') and (v))}
