import requests, os, json, random

from funcs import testquery, generate_random_filterparams
from models import QABightQueryAssessment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# # database connection setup
# DATABASE_URL = os.getenv('QA_TABLE_DB_CONNECTION_STRING')
# qa_assessor_eng = create_engine(DATABASE_URL)

# # DB connnection for testing generated queries from the app
# eng = create_engine(os.getenv('DB_CONNECTION_STRING'))


# ---- Basic information which is unlikely to change - may even be stored in the environment ---- #

# endpoint that we are testing
URL = 'https://data.sccwrp.org/bightquery/sql-unified2.php'
URLV2 = 'https://data.sccwrp.org/bightquery/api/v2/data/download.php'


def run_qa_iteration():
    # parameters that will change - for the QA process
    all_datatypes = ['Chemistry','BenthicInfauna','FishAbundance','SQOScores','SQOSummary','SQOCondition']
    weights = [0.5, 0.5, 0.5] + [0.1] * (len(all_datatypes) - 3)  # Adjust weights as needed

    # Use random.choices() with weights to make a biased selection
    # Make sure to switch back...
    # datatype = random.choices(all_datatypes, weights, k=1)[0]
    datatype = 'Chemistry'
    retrieveby = 'whole'

    filters = generate_random_filterparams(datatype = datatype, retrieveby = retrieveby)

    qa_assessment = testquery(
        url=URL,
        db_eng=None,
        datatype=datatype,
        retrieveby=retrieveby,
        filters=filters
    )

    print("qa_assessment")
    print(qa_assessment)


    # Session = sessionmaker(bind=qa_assessor_eng)

    # # Create session
    # session = Session()

    # # Create an instance of the QABightQueryAssessment model with the data
    # record = QABightQueryAssessment(**qa_assessment)

    # # Add the record to the session and commit
    # session.add(record)
    # session.commit()

    # # Close the session
    # session.close()


for i in range(4000):
    try:
        run_qa_iteration()
    except Exception as exc:
        print(f"Iteration {i} failed in run_qa_iteration: {exc}")
        raise
