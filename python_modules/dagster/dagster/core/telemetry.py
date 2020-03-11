# As an open source project, we collect usage statistics to improve the experience for our users.
# This will motivate projects such as developing new features for frequently used parts of the CLI
# and adding more examples to our docs. We cannot see or store configs, modes, context, or any data
# processed in your solids. If you'd like to opt out, add the following to
# $DAGSTER_HOME/instance_profile.yaml, creating that file if necessary: {'telemetry_enabled': 'false'}

import datetime
import os
import uuid

import requests
import yaml

telementry_enabled_envvar = 'TELEMETRY_ENABLED'


def log_action(action, metadata=None):
    try:
        if os.getenv(telementry_enabled_envvar) == 'false':
            return

        (user_id, tracking_enabled) = _get_user_id()

        if tracking_enabled is False:
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
    tracking_enabled = None

    dagster_home_path = _dagster_home()

    if dagster_home_path is None:
        return (uuid.getnode(), True)

    instance_profile_path = os.path.join(dagster_home_path, 'instance_profile.yaml')

    if not os.path.exists(instance_profile_path):
        with open(instance_profile_path, 'w+') as f:
            user_id = str(uuid.getnode())
            tracking_enabled = True
            yaml.dump({'user_id': user_id, 'tracking_enabled': tracking_enabled}, f)
    else:
        with open(instance_profile_path, 'r') as f:
            instance_profile_json = yaml.load(f, Loader=yaml.FullLoader)
            if instance_profile_json is None:
                instance_profile_json = {}

            if 'user_id' in instance_profile_json:
                user_id = instance_profile_json['user_id']
            if 'tracking_enabled' in instance_profile_json:
                tracking_enabled = instance_profile_json['tracking_enabled']

        if not tracking_enabled is False and (user_id is None or tracking_enabled is None):
            if user_id is None:
                user_id = str(uuid.uuid4())
                instance_profile_json['user_id'] = user_id
            if tracking_enabled is None:
                tracking_enabled = True
                instance_profile_json['tracking_enabled'] = tracking_enabled

            with open(instance_profile_path, 'w') as f:
                yaml.dump(instance_profile_json, f)

    return (user_id, tracking_enabled)


def execute_reset_telemetry_profile():
    dagster_home_path = _dagster_home()
    if not dagster_home_path:
        print('Please set $DAGSTER_HOME env var to reset profile')
        return

    instance_profile_path = os.path.join(dagster_home_path, 'instance_profile.yaml')
    if not os.path.exists(instance_profile_path):
        with open(instance_profile_path, 'w') as f:
            yaml.dump({'user_id': str(uuid.uuid4())}, f)

    else:
        with open(instance_profile_path, 'r') as f:
            instance_profile_json = yaml.load(f, Loader=yaml.FullLoader)
            instance_profile_json['user_id'] = str(uuid.uuid4())
            with open(instance_profile_path, 'w') as f:
                yaml.dump(instance_profile_json, f)


def execute_disable_telemetry():
    _toggle_telemetry(False)


def execute_enable_telemetry():
    _toggle_telemetry(True)


def _toggle_telemetry(enable_telemetry):
    dagster_home_path = _dagster_home()
    if not dagster_home_path:
        print(
            "Please set $DAGSTER_HOME env var to {enable_telemetry} telemetry".format(
                enable_telemetry="enable" if enable_telemetry else "disable"
            )
        )
        return

    instance_profile_path = os.path.join(dagster_home_path, 'instance_profile.yaml')

    if not os.path.exists(instance_profile_path):
        with open(instance_profile_path, 'w') as f:
            yaml.dump({'telemetry_enabled': enable_telemetry}, f)

    else:
        with open(instance_profile_path, 'r') as f:
            instance_profile_json = yaml.load(f, Loader=yaml.FullLoader)
            instance_profile_json['telemetry_enabled'] = enable_telemetry

            with open(instance_profile_path, 'w') as f:
                yaml.dump(instance_profile_json, f)
