# Run Order (Fast Path)

Use this exact sequence when you are ready to capture screenshots.

## 1) Initialize

```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Labs/LAB-2"
./run_lab2.sh init
./run_lab2.sh list
```

## 2) Start Airflow services

```bash
./run_lab2.sh start
```

Open `http://localhost:8080` and log in with:
- username: `admin`
- password: `AirflowLab2!`

## 3) Trigger required DAG runs (UI recommended)

From Airflow UI, unpause and trigger:
- `example_python_operator`
- `my_izzet_dag1`
- `my_izzet_dag2`

Alternative (CLI):

```bash
source .venv/bin/activate
export AIRFLOW_HOME="/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Labs/LAB-2/airflow_home"
airflow dags unpause example_python_operator
airflow dags unpause my_izzet_dag1
airflow dags unpause my_izzet_dag2
airflow dags trigger example_python_operator
airflow dags trigger my_izzet_dag1
airflow dags trigger my_izzet_dag2
```

## 4) Capture screenshots

Follow: `docs/SCREENSHOT_CHECKLIST.md`

## 5) Stop services

```bash
./run_lab2.sh stop
```

## 6) Build final zip for submission

```bash
./prepare_submission_zip.sh
```
