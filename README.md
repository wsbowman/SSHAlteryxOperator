# SSHAlteryxOperator
Airflow operator for executing SSH commands to Alteryx.

### Instructions
Put the SHH_Plugin folder into the plugins folder in your Airflow project.

### Use
```
from airflow.operators.ssh_plugin import SSHAlteryxOperator

upload_docs = SSHAlteryxOperator(
    ssh_conn_id="my_ssh_conn",
    task_id='My_Workflow.yxmd',
    command = r'AlteryxEngineCmd.exe "C:\User\My Workflow.yxmd"',
    dag=dag)
   ```
