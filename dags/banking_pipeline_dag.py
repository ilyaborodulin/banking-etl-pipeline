from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime


with DAG(
    dag_id="banking_pipeline",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=["banking", "etl", "data-quality"],
) as dag:

    generate_transactions = BashOperator(
        task_id="generate_transactions",
        bash_command="cd /opt/airflow && python /opt/airflow/src/generate_transactions.py",
    )

    validate_transactions = BashOperator(
        task_id="validate_transactions",
        bash_command="cd /opt/airflow && python /opt/airflow/src/validate_transactions.py",
    )

    load_to_postgres = BashOperator(
        task_id="load_to_postgres",
        bash_command="cd /opt/airflow && python /opt/airflow/src/load_to_postgres.py",
    )

    generate_transactions >> validate_transactions >> load_to_postgres