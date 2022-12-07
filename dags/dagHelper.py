import pandas as pd
import psycopg2
import os
import configparser

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pandas as pd
#transformation function
def transformXL(fileLocation,fileDestination,worksheet = 'DataSource'):
    
    sourceDF = pd.read_excel(fileLocation,worksheet,header=0)
    
    frameCols = sourceDF.columns
    dropColumns = []
    
    for x in frameCols:
        if x.split(':')[0] == 'Unnamed':
            dropColumns.append(x)
    sourceDF.drop(dropColumns,inplace=True,axis=1)
    
    #Formatting the columns headers to 
    frameCols = sourceDF.columns
    cols = []
    for x in frameCols:
        temp = x.replace(" ",'_')
        temp = temp.replace("-","_")
        temp = temp.replace(":","_")
        cols.append(temp)
        
    sourceDF.columns = cols
    
    sourceDF.to_csv(fileDestination,index=False)

def transformDB(fileLocation,tableName,config):
    #Starting spark with database connectivity
    #database connection data
"""
[POSTGRES]
PG_HOST = 127.0.0.1
PG_DB ='yourDatabase' 
PG_UNAME ='yourUsername' 
PG_PASS = 'your passg'
PG_PORT = 5432
"""
  spark = SparkSession.builder.appName("KPI"). \
            config('spark.jars','/usr/share/java/postgresql-42.2.26.jar'). \
            getOrCreate()
    sparkread = spark.read
    sparkcon = spark.sparkContext
    
    sourceDF = sparkread.csv(fileLocation,inferSchema=True,
                            header=True)
    print(f"jdbc:postgresql://{host}:{port}/{db}")
    sourceDF.write.format("jdbc") \
        .option("url",f"jdbc:postgresql://{host}:{port}/{db}") \
        .option("dbtable",f"{tableName}") \
        .option("user",f"{user}") \
        .option("password",f"{passwd}") \
        .option("driver","org.postgresql.Driver") \
        .save(mode='overwrite')

def writeToDb(config, dataframe, tableName, fileLocation):
    
    #database connection data
    db = config['POSTGRES']['PG_DB']
    user = config['POSTGRES']['PG_UNAME']
    passwd = config['POSTGRES']['PG_PASS']
    port = config['POSTGRES']['PG_PORT']
    host = config['POSTGRES']['PG_HOST']

    try:
        conn = psycopg2.connect(host=host,dbname=db,user=user,password=passwd,port=port)
        conn.set_session(autocommit=True)
        cur = conn.cursor()

    except Exception as e:
        print(e)

    
    tableCreationQuery = schemaGen(dataframe,tableName)
    
    #Create table
    queryTable(cur,tableCreationQuery)
    
    #Create file copy query
    copyQuery = createCopyQuery(fileLocation,tableName)
    
    #Write data to the database
    
    queryTable(cur,copyQuery)
    
    print(f'Completed. Check the database by querying it with Select * FROM {tableName}')

#Using pandas read_sql for getting schema
def getSchema(tableName, credentials):
    schema = pd.read_sql("""SELECT * FROM information_schema.columns where table_name='{}'""".format(tableName),con=credentials)
    return schema

#Issue is in using pd.read_sql to write data to the database. so using psycopg2
def queryTable(cursor,query):
    try:
        schema = cursor.execute(query)

    except Exception as e:
        print(e)
        
#This doesn't return anything

#Using the pd.read_sql for getting data from db
def queryBase(query):
    requiredTable = pd.read_sql(query,con=credentials)
    return requiredTable

#This returns the dataframe

def schemaGen(dataframe, schemaName):
    localSchema = pd.io.sql.get_schema(dataframe,schemaName)
    localSchema = localSchema.replace('TEXT','VARCHAR(255)').replace('INTEGER','VARCHAR').replace('\n','').replace('"',"")
    return "".join(localSchema)

def createCopyQuery(csvFilePath, tableName):
    copyCsvData = f"""COPY {tableName} from '{csvFilePath}' DELIMITER ',' CSV HEADER"""
    return copyCsvData

    
