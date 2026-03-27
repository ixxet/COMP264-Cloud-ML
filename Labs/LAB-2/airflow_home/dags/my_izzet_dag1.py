"""Lab 2 - Exercise 3: first custom DAG for Izzet."""

from __future__ import annotations

import textwrap
from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="my_izzet_dag1",
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    description="First Airflow DAG for Lab 2",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["lab2", "izzet"],
) as dag:
    print_date = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    sleep_task = BashOperator(
        task_id="sleep_5_seconds",
        bash_command="sleep 5",
    )

    templated_echo = BashOperator(
        task_id="templated_echo",
        bash_command=textwrap.dedent(
            """
            {% for i in range(3) %}
            echo "Run date: {{ ds }}"
            echo "Seven days later: {{ macros.ds_add(ds, 7) }}"
            {% endfor %}
            """
        ),
    )

    print_date >> [sleep_task, templated_echo]
