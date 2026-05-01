# Ansible Connection Settings (Crucial for Alpine)
ansible_python_interpreter: /usr/bin/python3

# Airflow System Settings
airflow_user: airflow_admin
airflow_version: "2.10.0"
python_version: "3.12" # Updated to reflect standard Alpine package repositories
airflow_home: "/home/{{ airflow_user }}/airflow"
venv_path: "/home/{{ airflow_user }}/airflow_venv"

# Database Settings
db_user: airflow_admin
db_password: airflow_password_123
db_name: airflow_db
mock_db_name: mock_database

# Airflow UI Admin User Settings
airflow_create_user: admin
airflow_create_first_name: Saif
airflow_create_last_name: Uddin
airflow_create_role: Admin
airflow_create_email: admin@example.com
airflow_create_password: admin_password_123

# Connection String (Calculated once here to avoid repeating in the playbook)
airflow_db_conn: "postgresql+psycopg2://{{ db_user }}:{{ db_password }}@localhost:5432/{{ db_name }}"