# COMP 264 - Lab 2 Submission

Name: **Izzet Abidi**  
Course: **COMP 264 - Cloud Machine Learning**  
Lab: **Weekly Lab 2 - Apache Airflow**  
Date: **2026-03-20**

## Exercise #1 - Installation

I installed Apache Airflow in a local virtual environment and initialized Airflow metadata DB and user.

Evidence:
- `01_terminal_version_and_init.png`
- `02_terminal_dag_list.png`
- `03_terminal_start.png`
- `04_ui_login_page.png`
- `05_ui_home_dashboard.png`

## Exercise #2 - Examine `example_python_operator`

I ran and reviewed the `example_python_operator` DAG in Graph view and task details.

Findings:
- DAG execution and task statuses are visible from Graph view.
- Task details show run state and timing information.

Evidence:
- `06_example_python_operator_graph.png`
- `07_example_python_operator_run_details.png`

## Exercise #3 - Build first DAG (`my_izzet_dag1.py`)

I created `my_izzet_dag1.py` under the Airflow `dags` folder and executed it successfully.

Evidence:
- `08_my_izzet_dag1_file.png`
- `09_my_izzet_dag1_graph_success.png`

## Exercise #4 - Simple data pipeline (`my_izzet_dag2.py`)

I downloaded `tutorial_dag.py`, then renamed/adapted it to `my_izzet_dag2.py`, uploaded it to the `dags` folder, and ran it.

Pipeline behavior:
- `extract`: pushes source order data to XCom.
- `transform`: computes total order value.
- `load`: reads transformed value from XCom and prints output.

Evidence:
- `10_tutorial_dag_original_file.png`
- `11_my_izzet_dag2_file.png`
- `12_my_izzet_dag2_graph_success.png`
- `13_my_izzet_dag2_load_log.png`

Terminal wrap-up evidence (recommended):
- `14_terminal_stop.png`
- `15_terminal_zip_created.png`

## Airflow on the cloud (MWAA)

Amazon MWAA is a managed Apache Airflow service on AWS. DAGs are uploaded to S3 and run by managed scheduler/workers with monitoring through CloudWatch.

(Optional evidence: `16_cloud_mwaa_note.png`)

## Conclusion

All required local Airflow exercises were completed:
- installation and setup
- examining example DAG
- creating and running first DAG
- building and running a simple ETL-style DAG
