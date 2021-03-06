import boto3
import os
from botocore.config import Config
import sys
import random
import time
import psycopg2

from src.d00_utils.log_utils import setup_logging
logger = setup_logging(__name__, "d00_utils.rds_objects")

# GLOBALS
from src import (
    BUCKET,
    MY_REGION,
    MY_REGION2,
    MY_PROFILE,
    MY_KEY,
    MY_AMI ,
    MY_VPC ,
    MY_GATEWAY,
    MY_SUBNET,
    MY_GROUP
)

os.environ['AWS_PROFILE'] = MY_PROFILE
os.environ['AWS_DEFAULT_REGION'] = MY_REGION
boto_config = Config(retries=dict(max_attempts=20))
rds_client = boto3.client('rds',config=boto_config, region_name=MY_REGION)

#==============================================================
#METHODS
# get all of the db instances
def describe_db():
    try:
        dbs = rds_client.describe_db_instances()
        #print(dbs['DBInstances'])
        print(len(dbs['DBInstances']))
        for db in dbs['DBInstances']:
            #print(db)
            print ("User name: ", db['MasterUsername'], \
            ", Endpoint: ", db['Endpoint'],    \
            ", Address: ", db['Endpoint']['Address'],    \
            ", Port: ", db['Endpoint']['Port'],       \
            ", Status: ", db['DBInstanceStatus'],     \
            ", ID =", db['DBInstanceIdentifier'] , \
            #", pass =", db['MasterUserPassword'] , \
            ", DBInstanceClass =", db['DBInstanceClass'] , \
            ", PubliclyAccessible =", db['PubliclyAccessible'] , \
            ", AvailabilityZone =", db['AvailabilityZone'] , \
            #", VpcSecurityGroupIds =", db['VpcSecurityGroupIds']
            )
    except Exception as error:
        print (error)

def create_db(nuevo_id):
    try:

        db_vars = {
            "DBInstanceIdentifier":nuevo_id,
             "MasterUsername":'dpa',
             "MasterUserPassword":'dpa01_largo',
             "DBInstanceClass":'db.t2.micro',
             "Engine":'postgres',
             "AllocatedStorage":5,
             "Port":5432,
             "DBSubnetGroupName":'default-vpc-0a3808edd1a4e1e9c',
             "PubliclyAccessible":True,
             "AvailabilityZone" : MY_REGION2,
             #"DBSecurityGroups": [db_security],
             "VpcSecurityGroupIds" :["sg-07aa1c02e1d427317"]
             #"DBName":'metadatos'
        }
        rds_client.create_db_instance(**db_vars)
    except Exception as error:
        print(error)

def modify_db(my_id):
    db_vars = {
        "DBInstanceIdentifier":my_id,
         #"DBName":'metadatos'
    }
    rds_client.modify_db_instance(**db_vars)

def delete_db(id_borrar):
    try:
        response = rds_client.delete_db_instance(
        DBInstanceIdentifier=id_borrar,
        SkipFinalSnapshot=True)
        print (response)
    except Exception as error:
        print (error)


def execute_query(query):
    try:
        host="metadatos.clx22b04cf2j.us-west-2.rds.amazonaws.com"
        conn = psycopg2.connect(user="dpa", # Usuario RDS
                                     password="dpa01_largo", # password de usuario de RDS
                                     host=host,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port="5432", # cambiar por el puerto
                                     database="postgres") # Nombre de la base de datos


        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("PostgreSQL connection is closed")
    except Exception as error:
        print (error)


#==============================================================
def show_select(postgreSQL_select_Query):
    try:
        host="metadatos.clx22b04cf2j.us-west-2.rds.amazonaws.com"
        connection = psycopg2.connect(user="dpa", # Usuario RDS
                                     password="dpa01_largo", # password de usuario de RDS
                                     host=host,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port="5432", # cambiar por el puerto
                                     database="postgres") # Nombre de la base de datos
        cursor = connection.cursor()

        cursor.execute(postgreSQL_select_Query)

        print("Selecting rows from table using cursor.fetchall")
        records = cursor.fetchall()
        print(len(records))
        print("Print each row and it's columns values")
        for row in records:
           print(row)
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def execute_sql(file_name):
    try:
        host="metadatos.clx22b04cf2j.us-west-2.rds.amazonaws.com"
        connection = psycopg2.connect(user="dpa", # Usuario RDS
                                     password="dpa01_largo", # password de usuario de RDS
                                     host=host,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port="5432", # cambiar por el puerto
                                     database="postgres") # Nombre de la base de datos
        cursor = connection.cursor()
        file_dir = "./sql/" + file_name

        cursor.execute(open(file_dir, "r").read())

        connection.commit()
    except (Exception, psycopg2.Error) as error :
        print ("Error while executing sql file", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")



#==============================================================
#response=rds_client.describe_security_groups()
#print(response)
#describe_db()
def main():
    execute_sql("metada_extract.sql")

    query = "INSERT INTO metadatos.extract (fecha, nombre_task, year, month, usuario, ip_ec2, tamano_zip, nombre_archivo, ruta_s3, task_status) VALUES ( '2', '2', '3','3','4','5','5', '6', '6','8' ) ;"
    execute_query(query)

    query = "SELECT * FROM metadatos.extract ; "
    show_select(query)

    query = "CREATE SCHEMA IF NOT EXISTS paola ;"
    execute_query(query)

    query = "CREATE TABLE paola.prueba (nombre VARCHAR);"
    execute_query(query)

    query = "INSERT INTO paola.prueba (nombre) VALUES ('Paola');"
    execute_query(query)

    query = "SELECT * FROM paola.prueba ; "
    show_select(query)

#execute_sql("metada_extract.sql")

#resp = rds_client.describe_db_subnet_groups()
#print(resp['DBSubnetGroups'])

#create_db("metadatos")
#describe_db()
#create_table()
#create_table()
#create_db("metadats")
# MAIN
#url = "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_1988_11.zip"
#postgreSQL_select_Query = "select * from metadatos.extract where task_status = '" + str(url) + "';"
#show_select(postgreSQL_select_Query)

#postgreSQL_select_Query = "select * from metadatos.extract;"
#show_select(postgreSQL_select_Query)
#create_db('metadatos')
#describe_db()
#delete_db('metadatos')
#delete_db('postgres')
#describe_db()
#create_db()
#describe_db()
#execute_query(query)
"""
response = client.create_db_subnet_group(
    DBSubnetGroupName='string',
    DBSubnetGroupDescription='string',
    SubnetIds=[
        'string',
    ],
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]
)
"""
