# -*- coding: utf-8 -*-
#
# Adapted from SSHOperator, which is licensed to ASF
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from base64 import b64encode
from select import select

from airflow import configuration
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
import re
from airflow.utils.decorators import apply_defaults


class SSHAlteryxOperator(BaseOperator):
    """
    Modified SSHOperator
    SSHAlteryxOperator to execute Alteryx commands on given remote host using the ssh_hook.
    :param ssh_hook: predefined ssh_hook to use for remote execution.
        Either `ssh_hook` or `ssh_conn_id` needs to be provided.
    :type ssh_hook: airflow.contrib.hooks.ssh_hook.SSHHook
    :param ssh_conn_id: connection id from airflow Connections.
        `ssh_conn_id` will be ignored if `ssh_hook` is provided.
    :type ssh_conn_id: str
    :param remote_host: remote host to connect (templated)
        Nullable. If provided, it will replace the `remote_host` which was
        defined in `ssh_hook` or predefined in the connection of `ssh_conn_id`.
    :type remote_host: str
    :param command: command to execute on remote host. (templated)
    :type command: str
    :param timeout: timeout (in seconds) for executing the command.
    :type timeout: int
    """

    template_fields = ('command', 'remote_host')
    template_ext = ('.sh',)

    @apply_defaults
    def __init__(self,
                 ssh_hook=None,
                 ssh_conn_id=None,
                 remote_host=None,
                 command=None,
                 timeout=180,
                 *args,
                 **kwargs):
        super(SSHModOperator, self).__init__(*args, **kwargs)
        self.ssh_hook = ssh_hook
        self.ssh_conn_id = ssh_conn_id
        self.remote_host = remote_host
        self.command = command
        self.timeout = timeout

    def execute(self, context):
        if self.ssh_conn_id:
            if self.ssh_hook and isinstance(self.ssh_hook, SSHHook):
                self.log.info("ssh_conn_id is ignored when ssh_hook is provided.")
            else:
                self.log.info("ssh_hook is not provided or invalid. " +
                              "Trying ssh_conn_id to create SSHHook.")
                self.ssh_hook = SSHHook(ssh_conn_id=self.ssh_conn_id,
                                        timeout=self.timeout)
        if not self.ssh_hook:
            raise AirflowException("Cannot operate without ssh_hook or ssh_conn_id.")
        if self.remote_host is not None:
            self.log.info("remote_host is provided explicitly. " +
                          "It will replace the remote_host which was defined " +
                          "in ssh_hook or predefined in connection of ssh_conn_id.")
            self.ssh_hook.remote_host = self.remote_host
        if not self.command:
            raise AirflowException("SSH command not specified. Aborting.")
        with self.ssh_hook.get_conn() as ssh_client:
            # Auto apply tty when its required in case of sudo
            get_pty = False
            if self.command.startswith('sudo'):
                get_pty = True
            self.log.info("Running command: %s", self.command)
            # set timeout taken as params
            stdin, stdout, stderr = ssh_client.exec_command(command=self.command,
                                                            get_pty=get_pty,
                                                            timeout=self.timeout
                                                            )
            # fix the encoding
            stdin._set_mode('b')
            stdout._set_mode('b')
            stderr._set_mode('b')

            agg_stdout = stdout.read().decode('utf-8', errors='ignore')
            agg_stderr = stderr.read().decode('utf-8', errors='ignore')
            
            #close the cons
            stdin.close()
            stdout.close()
            stderr.close()

            #errirs
            error = re.findall(r"(Error - .*\n)", agg_stdout)
            try:
                error = ' '.join(error)
            except:
                error = 'No Error'


            #log it
            if re.search(r'([\S\s]*?seconds with [0-9]* error)', agg_stdout.replace('.','').replace('\n','')) == None:
                enable_pickling = configuration.conf.getboolean(
                    'core', 'enable_xcom_pickling'
                )
                if enable_pickling:
                    print(agg_stdout)
                    return agg_stdout
                else:
                    print(b64encode(agg_stdout).decode('UTF-8', errors = 'ignore'))
                    return b64encode(agg_stdout).decode('UTF-8', errors = 'ignore')
            else:
                print(agg_stdout, '\n\nWorkflow error triggered by SW salesops')
                raise AirflowException("Workflow Error")

        return True

    def tunnel(self):
        ssh_client = self.ssh_hook.get_conn()
        ssh_client.get_transport()
