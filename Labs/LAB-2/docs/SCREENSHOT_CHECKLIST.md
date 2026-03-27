# Lab 2 Screenshot Checklist (Run-Order Aligned)

Capture screenshots in this order and save them in `../screenshots/`.

Important:
- You do **not** need to re-install Airflow.
- Use commands from `docs/RUN_ORDER.md`.
- For Exercise #1 evidence, terminal outputs from `init`/`list` are acceptable.

## 1) Initialize (Terminal)

1. `01_terminal_version_and_init.png`
- Run in terminal:
  - `cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Labs/LAB-2"`
  - `source .venv/bin/activate`
  - `airflow version`
  - `./run_lab2.sh init`
- Capture one screenshot showing Airflow version and successful init/user list output.

2. `02_terminal_dag_list.png`
- Run: `./run_lab2.sh list`
- Capture screenshot showing `example_python_operator`, `my_izzet_dag1`, `my_izzet_dag2`.

## 2) Start Airflow (Terminal + UI)

3. `03_terminal_start.png`
- Run: `./run_lab2.sh start`
- Capture screenshot of successful start output.

4. `04_ui_login_page.png`
- Browser at `http://localhost:8080` login page.

5. `05_ui_home_dashboard.png`
- Airflow home/dashboard after login.

## 3) Exercise #2 - Examine `example_python_operator`

6. `06_example_python_operator_graph.png`
- Graph view for `example_python_operator`.

7. `07_example_python_operator_run_details.png`
- DAG run details/task details with state/timing.

## 4) Exercise #3 - `my_izzet_dag1.py`

8. `08_my_izzet_dag1_file.png`
- Code file open: `airflow_home/dags/my_izzet_dag1.py`.

9. `09_my_izzet_dag1_graph_success.png`
- Graph view and successful run for `my_izzet_dag1`.

## 5) Exercise #4 - `tutorial_dag.py` to `my_izzet_dag2.py`

10. `10_tutorial_dag_original_file.png`
- Show original source file:
  - `docs/source/tutorial_dag_original.py` (copied from your Downloads file).

11. `11_my_izzet_dag2_file.png`
- Code file open: `airflow_home/dags/my_izzet_dag2.py`.

12. `12_my_izzet_dag2_graph_success.png`
- Graph view and successful run for `my_izzet_dag2`.

13. `13_my_izzet_dag2_load_log.png`
- Task log for `load` task showing `{'total_order_value': 1236.7}`.

## 6) Finish (Terminal)

14. `14_terminal_stop.png`
- Run: `./run_lab2.sh stop`
- Capture screenshot showing services stopped.

15. `15_terminal_zip_created.png`
- Run: `./prepare_submission_zip.sh`
- Capture screenshot showing zip creation path.

## Optional

16. `16_cloud_mwaa_note.png`
- Short note/screenshot in report about AWS MWAA concept (no deployment required).
