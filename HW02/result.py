import psycopg2, os
from dotenv import load_dotenv

# load env file
load_dotenv()
env = os.environ

# creating connection to database
conn = psycopg2.connect(dbname=os.getenv('DBNAME'), 
                        user=os.getenv('DBUSER'),
                        password=os.getenv('DBPASS'), 
                        host=os.getenv('DBPORT'))

# create cursor to work with database
cur = conn.cursor()

# output dictionary
result = {}

# key pgsql with empty value
result['pgsql'] = {}

# get version
cur.execute("SELECT Version();")

# store version into dictionary
result['pgsql']['version'] = cur.fetchone()[0]

# get database size
cur.execute("SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")

# store it into dictionary
result['pgsql']['dota2_db_size'] = cur.fetchone()[0]

#close cursor and connection to database
cur.close()
conn.close()