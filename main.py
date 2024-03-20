import requests, os
from openai import OpenAI
from funcs import testquery

# ---- Basic information which is unlikely to change - may even be stored in the environment ---- #

# endpoint that we are testing
URL = 'https://data.sccwrp.org/bightquery/sql-unified.php'

# DB conneciton
eng = os.getenv('DB_CONNECTION_STRING')

# Open AI information
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)
gpt_model = os.getenv("GPT_MODEL")

# parameters that will change - for the QA process
datatype = 'Chemistry'
retrieveby = 'whole'
filters = {'stratum': ['Estuaries'], 'region': ['Los Alamitos Estuary']}


qa_assessment = testquery(URL, eng, datatype, retrieveby, filters, gpt_model, openai_client)

print("qa_assessment")
print(qa_assessment)


