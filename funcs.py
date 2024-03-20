import requests, os, json
import pandas as pd
def testquery(url, db_eng, datatype, retrieveby, filters, gpt_model, openai_client):
    
    # easier to type
    client = openai_client

    assert isinstance(filters, (str, dict)), "filters must be a json string or a dictionary"

    requestbody = {
        "datatype": datatype,
        "retrieve": retrieveby,
        "form": json.dumps(filters) if isinstance(filters, dict) else filters
    }

    resp = requests.post(url, data=requestbody)
    response = resp.json()

    returned_data = response.get('data')    
    nrows = response.get('numrows')
    sql = response.get('sql')

    try:
        df = pd.read_sql(sql, db_eng)
        dbexecute_error = None
        counts_match = int(nrows) == len(df)
    except Exception as e:
        print("Exception executing sql query")
        print(e)
        dbexecute_error = str(e)
        counts_match = None

    # Ask the robot what it thinks
    robot_system_prompt = """
        Your job is to help me understand if SQL queries make sense and tell me what it looks like it is trying to accomplish. 
        Please also identify syntax errors or problems with the SQL query.
        Your response MUST BE A VALID JSON STRING in the following format (as my python script will parse your response using json.loads):
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
                "content": f"Does this query appear to accomplish what it looks like it is set out to do? Are there syntax errors? {sql}",
            }
        ],
        model=gpt_model
    )

    robot_assessment = [m.message.content for m in chat_completion.choices if m.message.role == 'assistant']
    robot_assessment = robot_assessment[0] if len(robot_assessment) > 0 else ''
    print("robot_assessment")
    print(robot_assessment)

    print(json.loads(robot_assessment))

    report = {
        "data_returned": returned_data is not None,
        "counts_match": counts_match,
        "dbexecute_error" : dbexecute_error,
        "chatgpt_assessment": json.loads(robot_assessment)
    }

    return report