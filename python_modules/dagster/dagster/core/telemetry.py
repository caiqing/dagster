# As an open source project, we collect usage statistics to inform development priorities.
# For more information, check out the docs at https://docs.dagster.io/latest/install/telemetry/'

import datetime
import os
import uuid

import requests
import yaml

from dagster.core.instance.config import DAGSTER_CONFIG_YAML_FILENAME

telemetry_str = 'telemetry'
user_id_str = 'user_id'
enabled_str = 'enabled'


def log_action(action, metadata=None):
    try:
        (user_id, telemetry_enabled) = _get_user_id()

        if telemetry_enabled is False:
            return

        requests.post(
            'https://telemetry.elementl.dev/actions',
            data={
                'user_id': user_id,
                'action': action,
                'client_time': datetime.datetime.now(),
                'metadata': metadata,
            },
        )
    except Exception:  # pylint: disable=broad-except
        pass


def _dagster_home():
    dagster_home_path = os.getenv('DAGSTER_HOME')

    if not dagster_home_path:
        return None

    return os.path.expanduser(dagster_home_path)


def _get_user_id():
    user_id = None
    telemetry_enabled = None
    dagster_home_path = _dagster_home()

    if dagster_home_path is None:
        return (uuid.getnode(), True)

    instance_config_path = os.path.join(dagster_home_path, DAGSTER_CONFIG_YAML_FILENAME)

    if not os.path.exists(instance_config_path):
        with open(instance_config_path, 'w') as f:
            user_id = str(uuid.getnode())
            telemetry_enabled = True
            yaml.dump({telemetry_str: {user_id_str: user_id, enabled_str: telemetry_enabled}}, f)
    else:
        with open(instance_config_path, 'r') as f:
            instance_profile_json = yaml.load(f, Loader=yaml.FullLoader)
            if instance_profile_json is None:
                instance_profile_json = {}

            if telemetry_str in instance_profile_json:
                if user_id_str in instance_profile_json[telemetry_str]:
                    user_id = instance_profile_json[telemetry_str][user_id_str]
                if enabled_str in instance_profile_json[telemetry_str]:
                    telemetry_enabled = instance_profile_json[telemetry_str][enabled_str]

        if not telemetry_enabled is False and (user_id is None or telemetry_enabled is None):
            if user_id is None:
                user_id = str(uuid.uuid4())
                instance_profile_json[telemetry_str][user_id_str] = user_id
            if telemetry_enabled is None:
                telemetry_enabled = True
                instance_profile_json[telemetry_str][enabled_str] = telemetry_enabled

            with open(instance_config_path, 'w') as f:
                yaml.dump(instance_profile_json, f)

    return (user_id, telemetry_enabled)


def execute_reset_telemetry_profile():
    dagster_home_path = _dagster_home()
    if not dagster_home_path:
        print('Must set $DAGSTER_HOME environment variable to reset profile')
        return

    instance_config_path = os.path.join(dagster_home_path, DAGSTER_CONFIG_YAML_FILENAME)
    if not os.path.exists(instance_config_path):
        with open(instance_config_path, 'w') as f:
            yaml.dump({telemetry_str: {user_id_str: str(uuid.uuid4())}}, f)

    else:
        with open(instance_config_path, 'r') as f:
            instance_profile_json = yaml.load(f, Loader=yaml.FullLoader)
            if telemetry_str in instance_profile_json:
                instance_profile_json[telemetry_str][user_id_str] = str(uuid.uuid4())
            else:
                instance_profile_json[telemetry_str] = {user_id_str: str(uuid.uuid4())}

            with open(instance_config_path, 'w') as f:
                yaml.dump(instance_profile_json, f)


def execute_disable_telemetry():
    _toggle_telemetry(False)


def execute_enable_telemetry():
    _toggle_telemetry(True)


def _toggle_telemetry(enable_telemetry):
    dagster_home_path = _dagster_home()
    if not dagster_home_path:
        print(
            "Must set $DAGSTER_HOME environment variable to {enable_telemetry} telemetry".format(
                enable_telemetry="enable" if enable_telemetry else "disable"
            )
        )
        return

    instance_config_path = os.path.join(dagster_home_path, DAGSTER_CONFIG_YAML_FILENAME)

    if not os.path.exists(instance_config_path):
        with open(instance_config_path, 'w') as f:
            yaml.dump({telemetry_str: {enabled_str: enable_telemetry}}, f)

    else:
        with open(instance_config_path, 'r') as f:
            instance_profile_json = yaml.load(f, Loader=yaml.FullLoader)
            if telemetry_str in instance_profile_json:
                instance_profile_json[telemetry_str][enabled_str] = enable_telemetry
            else:
                instance_profile_json[telemetry_str] = {enabled_str: enable_telemetry}

            with open(instance_config_path, 'w') as f:
                yaml.dump(instance_profile_json, f)
