### File: airflow_task_wrappers.py

from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule

def ssh_task(task_id, ssh_conn_id, command, on_failure_callback=None, **kwargs):
    """
    Wrapper for SSHOperator with failure handling.

    :param task_id: Unique task ID for the DAG
    :param ssh_conn_id: Connection ID for the SSH connection (configured in Airflow)
    :param command: Command to run on the remote server
    :param on_failure_callback: A function to call if the task fails
    :param kwargs: Additional arguments for SSHOperator
    :return: An instance of SSHOperator
    """
    operator = SSHOperator(
        task_id=task_id,
        ssh_conn_id=ssh_conn_id,
        command=command,
        trigger_rule=TriggerRule.ALL_SUCCESS,
        **kwargs
    )

    if on_failure_callback:
        operator.on_failure_callback = on_failure_callback

    return operator

def file_sensor_task(task_id, filepath, poke_interval=10, timeout=300, **kwargs):
    """
    Wrapper for FileSensor.

    :param task_id: Unique task ID for the DAG
    :param filepath: Path to the file to sense
    :param poke_interval: Time in seconds between each poke
    :param timeout: Maximum time to wait for the file to be available
    :param kwargs: Additional arguments for FileSensor
    :return: An instance of FileSensor
    """
    return FileSensor(
        task_id=task_id,
        filepath=filepath,
        poke_interval=poke_interval,
        timeout=timeout,
        **kwargs
    )

### File: example_dag.py

from airflow import DAG
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow_task_wrappers import ssh_task, file_sensor_task

def handle_ssh_failure(context):
    """
    Example failure handler function.

    :param context: Context dictionary with task and dag run details
    """
    print("Task failed. Performing custom failure handling.")
    # Add custom failure handling logic here, such as alerting or cleanup.

def create_example_dag():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    with DAG(
        dag_id='example_airflow_task_api',
        default_args=default_args,
        description='Example DAG demonstrating task API with failure handling',
        schedule_interval=None,
        start_date=days_ago(1),
        tags=['example'],
    ) as dag:

        # Task 1: Execute an SSH command
        ssh_task_1 = ssh_task(
            task_id='run_remote_command',
            ssh_conn_id='my_ssh_connection',
            command='exit 1',  # Example command that fails
            on_failure_callback=handle_ssh_failure
        )

        # Task 2: Wait for a file to be present
        file_sensor = file_sensor_task(
            task_id='wait_for_file',
            filepath='/tmp/my_file.txt',
            poke_interval=15,
            timeout=600
        )

        ssh_task_1 >> file_sensor

    return dag

globals()['example_airflow_task_api'] = create_example_dag()
