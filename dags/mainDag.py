import os
import warnings
warnings.filterwarnings('ignore')
from dagHelper import *

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
#This is Dag File
args = {
        'owner':'spacer'
}

source = "/run/media/solverbot/repoA/gitFolders/dashBoard Designs/fsPipelines/fileupload/"
dest = "/run/media/solverbot/repoA/gitFolders/dashBoard Designs/fsPipelines/fileCSV/"

name = os.listdir(source)[1]
sourceName = source + name
#The source dataframe is generated
destName = os.listdir(source)[1].split('.')[0]+".csv"
newDest = dest + destName.replace(' ','_')
print(os.listdir(os.curdir))


with DAG(
        dag_id='Excel_CSV_PG_writer',
        default_args=args,
        schedule_interval='0 0 * * *',
        start_date=days_ago(2)
) as dag:
    t1 = PythonOperator(
            task_id='t1',
            python_callable=transformXL,
            op_kwargs={
                'fileLocation':sourceName,
                'fileDestination':newDest,
                'worksheet':'StoreData'
                }
            )
    t1

if __name__ == "__main__":
    dag.cli()
            
