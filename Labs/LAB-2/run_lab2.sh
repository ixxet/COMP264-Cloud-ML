#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
export AIRFLOW_HOME="$SCRIPT_DIR/airflow_home"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtual environment not found at $VENV_DIR"
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

usage() {
  cat <<'EOF'
Usage:
  ./run_lab2.sh init                # initialize DB + create admin user
  ./run_lab2.sh list                # list DAGs of interest
  ./run_lab2.sh test [YYYY-MM-DD]   # run dags test for required DAGs
  ./run_lab2.sh start               # start webserver(8080) + scheduler in daemon mode
  ./run_lab2.sh stop                # stop webserver + scheduler daemons
  ./run_lab2.sh reset               # stop services and reset airflow_home (fresh lab)

Default login after init:
  username: admin
  password: AirflowLab2!
EOF
}

ensure_dirs() {
  mkdir -p "$AIRFLOW_HOME/dags" "$SCRIPT_DIR/screenshots" "$SCRIPT_DIR/logs"
}

create_admin_user_if_needed() {
  if airflow users list 2>/dev/null | grep -Eq '^.*\badmin\b'; then
    echo "Admin user already exists."
  else
    airflow users create \
      --username admin \
      --firstname Izzet \
      --lastname Abidi \
      --role Admin \
      --email izzet.abidi@example.com \
      --password "AirflowLab2!"
  fi
}

cmd="${1:-}"
case "$cmd" in
  init)
    ensure_dirs
    airflow db migrate
    create_admin_user_if_needed
    airflow users list
    ;;

  list)
    ensure_dirs
    airflow dags list | grep -E "example_python_operator|my_izzet_dag1|my_izzet_dag2" || true
    ;;

  test)
    ensure_dirs
    run_date="${2:-$(date +%Y-%m-%d)}"
    airflow dags test example_python_operator "$run_date"
    airflow dags test my_izzet_dag1 "$run_date"
    airflow dags test my_izzet_dag2 "$run_date"
    ;;

  start)
    ensure_dirs
    airflow webserver --port 8080 --daemon
    airflow scheduler --daemon
    echo "Airflow started. Open http://localhost:8080"
    ;;

  stop)
    pkill -f "airflow webserver.*$AIRFLOW_HOME" || true
    pkill -f "airflow scheduler.*$AIRFLOW_HOME" || true
    pkill -f "gunicorn.*$AIRFLOW_HOME" || true
    echo "Airflow services stopped."
    ;;

  reset)
    "$0" stop
    tmp_dags_dir="$(mktemp -d)"
    cp "$AIRFLOW_HOME"/dags/my_izzet_dag*.py "$tmp_dags_dir/" 2>/dev/null || true
    rm -rf "$AIRFLOW_HOME"
    mkdir -p "$AIRFLOW_HOME/dags"
    cp "$tmp_dags_dir"/my_izzet_dag*.py "$AIRFLOW_HOME/dags/" 2>/dev/null || true
    rm -rf "$tmp_dags_dir"
    "$0" init
    ;;

  *)
    usage
    exit 1
    ;;
esac
