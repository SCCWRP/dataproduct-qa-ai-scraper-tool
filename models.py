from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON

Base = declarative_base()

class QABightQueryAssessment(Base):
    __tablename__ = 'qa_bightquery_assessment'
    
    id = Column(Integer, primary_key=True)
    request_body_json = Column(JSON)
    endpoint_tested = Column(String)
    request_method = Column(String)
    data_returned = Column(String)  # Assuming you want to store "True"/"False" as strings
    counts_match = Column(String)  # Same assumption as above
    api_record_count = Column(Integer)
    manual_execution_record_count = Column(Integer)
    dbexecute_error = Column(String)
    chatgpt_syntax_assessment = Column(String)
    chatgpt_sql_assessment = Column(String)
    chatgpt_sql_opinion = Column(String)
    chatgpt_human_prompt = Column(String)
    sql = Column(String)


