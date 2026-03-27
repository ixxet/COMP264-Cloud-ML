#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIP_NAME="Lab2_Izzet_Abidi_Submission.zip"

cd "$SCRIPT_DIR"
rm -f "$ZIP_NAME"

zip -r "$ZIP_NAME" \
  README.md \
  docs \
  screenshots \
  docs/source/tutorial_dag_original.py \
  airflow_home/dags/my_izzet_dag1.py \
  airflow_home/dags/my_izzet_dag2.py \
  logs/01_airflow_version.txt \
  logs/02_users_list.txt \
  logs/03_dags_list.txt \
  logs/04_my_izzet_dag2_test.txt

echo "Created: $SCRIPT_DIR/$ZIP_NAME"
