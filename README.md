# Data pipelines with Apache Airflow and AWS EC2 and S3

Automated data pipeline workflows using Apache Airflow that loads and processes data in AWS EC2 and then upload into a AWS S3 bucket. In addition, a telegram-bot program is set-up to run 24/7 in AWS EC2 instance to enable user to view reports.

## Objective

MOH Malaysia releases public data regarding blood donation index everyday. Thus, this project aims to utilize those data by preparing charts and reports for the public to view easily.

## Architecture

![pipeline](https://github.com/syahiramzar/mybloodindex_project/assets/128501870/6c44abf6-d5f5-40dd-85d7-24559d6a81ea)

* MOH official data: [data-darah-public](https://github.com/MoH-Malaysia/data-darah-public) & [granulated-donor-data](https://dub.sh/ds-data-granular)
* [Apache Airlfow](https://airflow.apache.org/)
* [AWS S3](https://aws.amazon.com/s3/)
