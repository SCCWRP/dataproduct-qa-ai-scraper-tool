import requests, os, random, json
from openai import OpenAI
from funcs import testquery, generate_random_filterparams
from models import QABightQueryAssessment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# database connection setup
DATABASE_URL = os.getenv('QA_TABLE_DB_CONNECTION_STRING')
qa_assessor_eng = create_engine(DATABASE_URL)

# DB connnection for testing generated queries from the app
eng = create_engine(os.getenv('DB_CONNECTION_STRING'))


# ---- Basic information which is unlikely to change - may even be stored in the environment ---- #

# endpoint that we are testing
URL = 'https://data.sccwrp.org/bightquery/sql-unified.php'



# Open AI information
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)
gpt_model = os.getenv("GPT_MODEL")


for i in range(4000):
    try:
        # parameters that will change - for the QA process
        all_datatypes = ['Chemistry','BenthicInfauna','FishAbundance','SQOScores','SQOSummary','SQOCondition']
        weights = [0.5, 0.5, 0.5] + [0.1] * (len(all_datatypes) - 3)  # Adjust weights as needed
        # Use random.choices() with weights to make a biased selection
        selected_value = random.choices(all_datatypes, weights, k=1)[0]
        datatype = selected_value
        retrieveby = 'whole'

        filters = generate_random_filterparams(datatype = datatype, retrieveby = retrieveby)


        qa_assessment = testquery(URL, eng, datatype, retrieveby, filters, gpt_model, openai_client)

        print("qa_assessment")
        print(qa_assessment)


        Session = sessionmaker(bind=qa_assessor_eng)

        # Create session
        session = Session()

        # Create an instance of the QABightQueryAssessment model with the data
        record = QABightQueryAssessment(**qa_assessment)

        # Add the record to the session and commit
        session.add(record)
        session.commit()

        # Close the session
        session.close()
    except Exception as e:
        print("error")