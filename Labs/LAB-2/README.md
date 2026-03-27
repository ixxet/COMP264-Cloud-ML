# Lab 2 Submittable (Izzet Abidi)

This folder contains a complete, self-contained Apache Airflow Lab 2 setup for COMP 264.

## Folder structure

- `airflow_home/`: Airflow home (DB, logs, and DAGs)
- `airflow_home/dags/my_izzet_dag1.py`: Exercise #3 DAG
- `airflow_home/dags/my_izzet_dag2.py`: Exercise #4 DAG (from `tutorial_dag.py` pattern)
- `docs/source/tutorial_dag_original.py`: original downloaded `tutorial_dag.py` used for Exercise #4
- `run_lab2.sh`: helper script to run required lab commands
- `prepare_submission_zip.sh`: builds a clean submission zip (without `.venv`)
- `docs/SCREENSHOT_CHECKLIST.md`: exact screenshot checklist for submission
- `docs/SUBMISSION_REPORT_TEMPLATE.md`: fill-in report template
- `docs/RUN_ORDER.md`: fastest command sequence to complete screenshots
- `screenshots/`: put your captured screenshots here

## Airflow version used

- `apache-airflow==2.11.2`
- Installed in local virtual environment: `.venv`

## Quick run commands

```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Labs/LAB-2"
./run_lab2.sh init
./run_lab2.sh list
./run_lab2.sh test 2026-03-20
./run_lab2.sh start
```

Open [http://localhost:8080](http://localhost:8080) and log in:

- username: `admin`
- password: `AirflowLab2!`

When done:

```bash
./run_lab2.sh stop
```

## Notes for lab grading

- `example_python_operator`, `my_izzet_dag1`, and `my_izzet_dag2` are available in Airflow.
- Both custom DAG files are inside `airflow_home/dags` as requested.
- `my_izzet_dag2.py` was created directly from your downloaded `tutorial_dag.py` by renaming the DAG id.
- Use the checklist in `docs/SCREENSHOT_CHECKLIST.md` to capture all required evidence.
