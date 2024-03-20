# sccwrp/flask:ai-search
FROM debian:bookworm-slim

WORKDIR /home

# Libs to compile and install python, and others
RUN apt-get update
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev 
RUN apt-get install -y wget xz-utils uwsgi vim 

# For Postgres Libs - psycopg2 and sqlalchemy
RUN apt-get install -y libpq-dev gcc


# Install Python 3.9.9
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.10.9/Python-3.10.9.tgz
RUN tar -xf Python-3.10.9.tgz
WORKDIR /tmp/Python-3.10.9
RUN ./configure --enable-optimizations
RUN make -j 2
RUN make install
WORKDIR /tmp
RUN rm -rf Python-3.10.9/
RUN rm Python-3.10.9.tgz
WORKDIR /home

# Order matters here
# libs that i know have breaking changes are sqlalchemy, pandas and the OpenAI API for Python
RUN pip3 install ipython
RUN pip3 install openai==1.9.0
RUN pip3 install psycopg2
RUN pip3 install "sqlalchemy<2.0.0"
RUN pip3 install flask
RUN pip3 install "pandas<2.0.0" 

# For running the flask app - i think
RUN pip3 install uwsgi

# Because i thought requests was in the PSL
RUN pip3 install requests

# forgot to install openpyxl and xlsxwriter
RUN pip3 install openpyxl xlsxwriter

# forgot to install chromadb
RUN pip3 install chromadb