import requests, os, json, random
import pandas as pd
import numpy as np


def testquery(url, db_eng, datatype, retrieveby, filters, gpt_model, openai_client, request_method = 'post'):
    
    # easier to type
    client = openai_client

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

    try:
        df = pd.read_sql(sql, db_eng)
        dbexecute_error = None
        manual_execution_record_count = len(df)
        counts_match = api_record_count == manual_execution_record_count
    except Exception as e:
        print("Exception executing sql query")
        print(e)
        dbexecute_error = str(e)
        manual_execution_record_count = None
        counts_match = None

    # Ask the robot what it thinks
    robot_system_prompt = """
        Your job is to help me understand if SQL queries make sense and tell me what it looks like it is trying to accomplish. 
        Please also identify syntax errors or problems with the SQL query.
        Your response MUST BE A VALID JSON STRING in the following format (as my python script will parse your response using json.loads):
        
        Below is what an example response must look like:
        
        {
            "has_syntax_error": A boolean - True or False,
            "appears_correct" : A boolean - True or False,
            "assessment": A string containting your overall opinion and/or assessment about the SQL query
        }
        
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": robot_system_prompt,
            },
            {
                "role": "user",
                "content": f"Does this query appear to accomplish what it looks like it is set out to do? Are there syntax errors? {sql}\n Please give a response in a json format.",
            }
        ],
        model=gpt_model
    )

    robot_assessment = [m.message.content for m in chat_completion.choices if m.message.role == 'assistant']
    robot_assessment = robot_assessment[0] if len(robot_assessment) > 0 else ''
    print("robot_assessment")
    print(robot_assessment)

    print(json.loads(robot_assessment))
    
    
    human_sql_translation_chat = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Given a SQL statement, provide a sentence (or series of sentences) in english which would be a request that would promp a data engineer to generate the query",
            },
            {
                "role": "user",
                "content": f"What would be a request a person might make if they were trying to query this data from the database? {sql}",
            }
        ],
        model=gpt_model
    )

    human_sql_translation = [m.message.content for m in human_sql_translation_chat.choices if m.message.role == 'assistant']
    human_sql_translation = human_sql_translation[0] if len(human_sql_translation) > 0 else ''
    
    # make it a dictionary
    robot_assessment = json.loads(robot_assessment)
    
    report = {
        "request_body_json": json.dumps(requestbody),
        "endpoint_tested": url,
        "request_method": request_method,
        "data_returned": returned_data is not None,
        "counts_match": counts_match,
        "api_record_count" : api_record_count,
        "manual_execution_record_count" : manual_execution_record_count,
        "dbexecute_error" : dbexecute_error,
        "chatgpt_syntax_assessment": 'Pass' if (robot_assessment.get('has_syntax_error') == False) \
            else 'Fail' if (robot_assessment.get('has_syntax_error') == True) \
            else 'Unable to determine' ,
        "chatgpt_sql_assessment": 'Fail' if (robot_assessment.get('appears_correct') == False) \
            else 'Pass' if (robot_assessment.get('appears_correct') == True) \
            else 'Unable to determine' ,
        "chatgpt_sql_opinion": robot_assessment.get('assessment') ,
        "chatgpt_human_prompt": human_sql_translation,
        "sql": sql
    }

    return report




# To be used in the generate_random_filterparams
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



def generate_random_filterparams(
    datatype = 'Chemistry',
    initial_request_endpoint = 'https://data.sccwrp.org/bightquery/interactive_sql-unified.php',
    interactive_endpoint = 'https://data.sccwrp.org/bightquery/lookup_sql-unified.php',
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
            resp = requests.get(initial_request_endpoint, data=requestbody)

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
                
            lookup_elements = getrandomvals(filterparams)

            requestbody['lookup_elements'] = json.dumps(lookup_elements)

            resp = requests.post(interactive_endpoint, data=requestbody)

            
            filterparams = resp.json()
            filterparams['stratum'] = filterparams.pop('field1')
            filterparams['region'] = filterparams.pop('field2')
            filterparams['samplingorganization'] = filterparams.pop('field3')
            filterparams['surveyyear'] = filterparams.pop('field8')
            
        
    return {k:v for k,v in filterparams.items() if ((k!='sql') and (v))}
