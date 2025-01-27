from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.decorators import apply_defaults

def failure_handler(context):
    # Custom failure handling code
    print("Task failed. Triggering failure handler...")
    # Add your failure handling logic here

class CustomSSHOperator(SSHOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_failure_callback = failure_handler

    def execute(self, context):
        try:
            super().execute(context)
        except Exception as e:
            self.on_failure_callback(context)
            raise e

def create_ssh_operator(task_id, ssh_conn_id, command, *args, **kwargs):
    return CustomSSHOperator(
        task_id=task_id,
        ssh_conn_id=ssh_conn_id,
        command=command,
        *args, **kwargs
    )
