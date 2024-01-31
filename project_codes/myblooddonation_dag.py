from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from myblood_etl_code import myblood_etl
from myblood_dataviz_code import myblood_dataviz
from myblood_blast_code import myblood_blast

#Upload files to s3 from ec2

def upload_html_s3():
    with open("/home/ubuntu/plots/chart4.html", "rb") as c4h:
        s3 = boto3.client('s3')
        s3.upload_fileobj(c4h, "syahir-my-blood-project", "chart4.html")

def upload_csv_s3():
    s3 = boto3.resource('s3')
    s3.Object('syahir-my-blood-project', 'donations_my.csv').put(Body=open('/home/ubuntu/refined_df/donations_my.csv', 'rb'))
    s3.Object('syahir-my-blood-project', 'donations_by_state.csv').put(Body=open('/home/ubuntu/refined_df/donations_state.csv', 'rb'))
    s3.Object('syahir-my-blood-project', 'newdonor_my.csv').put(Body=open('/home/ubuntu/refined_df/newdonor_my.csv', 'rb'))
    s3.Object('syahir-my-blood-project', 'newdonor_by_state.csv').put(Body=open('/home/ubuntu/refined_df/newdonor_state.csv', 'rb')) 
    s3.Object('syahir-my-blood-project', 'returning_donors.csv').put(Body=open('/home/ubuntu/refined_df/returning_donor.csv', 'rb'))
    s3.Object('syahir-my-blood-project', 'all-donors.csv').put(Body=open('/home/ubuntu/refined_df/donor_all_visits.csv', 'rb'))

default_args = {
    'owner': 'Syahir Amzar Zulkifli',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 29),
    'email': ['syahiramzar@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3)
}

with DAG(
    'myblood_project',
    default_args = default_args,
    description = 'Malaysia blood donation statistics',
    start_date = datetime(2024, 1,29),
    schedule_interval = '0 22 * * *' ) as dag:

    upload_csv_to_bucket = PythonOperator(
    task_id='uploading_df_to_s3',
    python_callable=upload_csv_s3,
    )

    myblood_etl = PythonOperator(
    task_id='extract_and_transform',
    python_callable=myblood_etl,
    )

    myblood_dataviz = PythonOperator(
    task_id='data_viz',
    python_callable=myblood_dataviz,
    )

    upload_html_to_bucket = PythonOperator(
    task_id='uploading_html_to_s3',
    python_callable=upload_html_s3,
    )

    myblood_blast = PythonOperator(
    task_id='data_blast_tg',
    python_callable=myblood_blast,
    )

    myblood_etl >> upload_csv_to_bucket >> myblood_dataviz >> upload_html_to_bucket >> myblood_blast