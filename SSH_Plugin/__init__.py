
"""
    SSHplugin
    This plugin provides an interface to the Github v3 API.
    The Github Hook extends the HttpHook and accepts both Basic and
    Token Authentication. If both are available, the hook will use
    the specified token, which should be in the following format in
    the extras field: {"token":"XXXXXXXXXXXXXXXXXXXXX"}
        The host value in the Hook should contain the following:
        https://api.github.com/
    The Github Operator provides support for the following endpoints:
        Comments
        Commits
        Commit Comments
        Issue Comments
        Issues
        Members
        Organizations
        Pull Requests
        Repositories
"""

from airflow.plugins_manager import AirflowPlugin
from SSH_Plugin.operators.ssh_alteryx_operator import SSHAlteryxOperator


class SSH_Plugin(AirflowPlugin):
    name = "ssh_plugin"
    operators = [SSHAlteryxOperator]
    # A list of class(es) derived from BaseHook
    hooks = []
    # A list of class(es) derived from BaseExecutor
    executors = []
    # A list of references to inject into the macros namespace
    macros = []
    # A list of objects created from a class derived
    # from flask_admin.BaseView
    admin_views = []
    # A list of Blueprint object created from flask.Blueprint
    flask_blueprints = []
    # A list of menu links (flask_admin.base.MenuLink)
    menu_links = []