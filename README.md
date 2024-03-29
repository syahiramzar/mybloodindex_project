# Data Pipelines with Apache Airflow and AWS EC2 and S3

Automated data pipeline workflows using Apache Airflow that loads and processes data in AWS EC2 and then upload into a AWS S3 bucket. In addition, a telegram-bot program is set-up to run 24/7 in AWS EC2 instance to enable user to view reports.

## Objective

MOH Malaysia releases public data regarding blood donation index everyday. Thus, the goal of this project is to utilize those data by preparing charts and reports for the public to view easily using Telegram automated bot. Using Apache Airflow, a data pipeline workflow was created with custom operators that perform tasks such as extract and transform data, generate data visualizations, upload into s3 bucket and blast a notification Telegram users (in group). The telegram bot will be ran 24/7, while the data will be refreshed at 10:00AM (MYT) everyday. 

## Architecture

![pipeline](https://github.com/syahiramzar/mybloodindex_project/assets/128501870/6c44abf6-d5f5-40dd-85d7-24559d6a81ea)

* MOH official data: [data-darah-public](https://github.com/MoH-Malaysia/data-darah-public) & [granulated-donor-data](https://dub.sh/ds-data-granular)
* [Apache Airlfow](https://airflow.apache.org/)
* [AWS S3](https://aws.amazon.com/s3/)

* [AWS EC2](https://aws.amazon.com/ec2/) instance with the following specs is used:

![image](https://github.com/syahiramzar/mybloodindex_project/assets/128501870/5fe746d4-b0cd-4b7d-8653-dc6dfbb22e79)

Prerequisites:
* AWS account with EC2 and S3 bucket set up
* Python 3
* Airflow
* Python libraries, as listed in `requirements.txt`


The end result will be a pipeline definition in Apache Airflow as illustrated below.

![image](https://github.com/syahiramzar/mybloodindex_project/assets/128501870/4ef420a1-428b-4014-9367-0deb5abb402b)

## Project files
In addition to the libraries, the project also includes:

* `myblooddonation_dag.py` - DAG (Directed Acyclic Graph) definition script. Placed in `home/airflow/project_dag` folder.
* `myblood_etl_code.py` - Python script for extracting and transforming data. Placed in `home/airflow/project_dag` folder.
* `myblood_dataviz_code.py` - Python script for data visualization. Placed in `home/airflow/project_dag` folder.
* `myblood_blast_code.py` - Python script for sending Telegram message. Placed in `home/airflow/project_dag` folder.
* `blood_telebot.py` - Python script for telegram-bot than runs 24/7 Placed in `home/` folder.

# Steps to run project

1. Set up AWS EC2 and S3. An AWS IAM user with the following policies (or equivalent permissions) is required:

* AmazonS3FullAccess
* IAMFullAccess
* AmazonEC2FullAccess

2. On first connect to instance, install the following libraries using these commands:

  * `sudo apt update` - ensure EC2 has the latest files.
  * `sudo apt install python3-pip` - install python 3 pip
  * `sudo apt install python3.10-venv` - install python 3 virtual environment (venv)

3. Go into virtual environment by using this command: `source /venv/bin/activate`

4. Intall Apache Airflow using `pip install apache-airflow` command.

5. Install python libraries as listed in `requirements.txt`.

6. Use `cd airflow` and then `makedir "folder_name"` to create a new folder. 

7. Place all the project files in their corresponding directories.

8. Update `home/airflow/airflow.cfg` file to include DAGs in the newly created folder as in 6. 

9. From root directory, use these commands to run:

  * `nohup python blood_telebot.py &` - run telegram-bot 24/7 in the background.
  * `airflow db init` - initialize airflow database.
  * `airflow webserver &` - run airflow webserver.
  * `nohup airflow scheduler &` - run airflow scheduler in the background.

10. Access Airflow through the web browser using url: "ec2-public-ipv4-dns":8080

11. In the Airflow UI, enable the `myblood_project` DAG. The pipeline will run on the schedule defined in the DAG. For this project, set to 10:00AM everyday.

12. For everytime the EC2 stops or reboots, repeat 9. 
