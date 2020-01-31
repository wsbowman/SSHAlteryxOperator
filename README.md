# SSHAlteryxOperator
Airflow operator for executing SSH commands to Alteryx.

This tool is designed to operate similarly to the standard SSH Operator while additionally:
- Elevating Alteryx workflow errors to the airflow level
- Capturing Alteryx workflow logs inside of Airflow logs

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
