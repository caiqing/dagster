import os

from dagster.core.telemetry import (
    _get_user_id,
    execute_disable_telemetry,
    execute_enable_telemetry,
    execute_reset_telemetry_profile,
    log_action,
    telementry_enabled_envvar,
)
from dagster.seven import mock


def test_telemetry_disabled_envvar():
    os.environ[telementry_enabled_envvar] = 'false'
    with mock.patch('requests.post') as requests_mock:
        log_action('did something', {})
    requests_mock.assert_not_called()


def test_telemetry_enabled_envvar():
    os.environ[telementry_enabled_envvar] = 'true'
    (user_id, tracking_enabled) = _get_user_id()
    assert tracking_enabled == True
    with mock.patch('requests.post') as requests_mock:
        log_action('did something', {})

    _, kwargs = requests_mock.call_args_list[0]
    requests_mock.assert_called_once_with(
        'https://telemetry.elementl.dev/actions',
        data={
            'user_id': user_id,
            'action': 'did something',
            'client_time': kwargs['data']['client_time'],  # Ignore client time check
            'metadata': {},
        },
    )


def test_telemetry_unset_envvar():
    del os.environ[telementry_enabled_envvar]
    (user_id, tracking_enabled) = _get_user_id()
    assert tracking_enabled == True
    with mock.patch('requests.post') as requests_mock:
        log_action('did something', {})

    _, kwargs = requests_mock.call_args_list[0]
    requests_mock.assert_called_once_with(
        'https://telemetry.elementl.dev/actions',
        data={
            'user_id': user_id,
            'action': 'did something',
            'client_time': kwargs['data']['client_time'],  # Ignore client time check
            'metadata': {},
        },
    )


@mock.patch('builtins.print')
def test_reset_telemetry_profile(mocked_print):
    open_mock = mock.mock_open()
    with mock.patch("dagster.core.telemetry.open", open_mock, create=True):
        execute_reset_telemetry_profile()
        open_mock.assert_not_called()
        assert mocked_print.mock_calls == [
            mock.call('Please set $DAGSTER_HOME env var to reset profile')
        ]

        os.environ['DAGSTER_HOME'] = '/some/path/'
        execute_reset_telemetry_profile()
        open_mock.assert_called_with('/some/path/instance_profile.yaml', 'w')
        assert len(open_mock.return_value.write.call_args_list) == 5

    del os.environ['DAGSTER_HOME']


@mock.patch('builtins.print')
def test_enable_telemetry(mocked_print):
    open_mock = mock.mock_open()
    with mock.patch("dagster.core.telemetry.open", open_mock, create=True):
        execute_enable_telemetry()
        open_mock.assert_not_called()
        assert mocked_print.mock_calls == [
            mock.call('Please set $DAGSTER_HOME env var to enable telemetry')
        ]

        os.environ['DAGSTER_HOME'] = '/some/path/'
        execute_enable_telemetry()

        print(
            'open_mock.return_value.write.call_args_list',
            open_mock.return_value.write.call_args_list,
        )
        open_mock.assert_called_with('/some/path/instance_profile.yaml', 'w')

        open_mock.return_value.write.assert_has_calls(
            [
                mock.call('telemetry_enabled'),
                mock.call(':'),
                mock.call(' '),
                mock.call('true'),
                mock.call('\n'),
            ]
        )

    del os.environ['DAGSTER_HOME']


@mock.patch('builtins.print')
def test_disable_telemetry(mocked_print):
    open_mock = mock.mock_open()
    with mock.patch("dagster.core.telemetry.open", open_mock, create=True):
        execute_disable_telemetry()
        open_mock.assert_not_called()
        assert mocked_print.mock_calls == [
            mock.call('Please set $DAGSTER_HOME env var to disable telemetry')
        ]

        os.environ['DAGSTER_HOME'] = '/some/path/'
        execute_disable_telemetry()

        print(
            'open_mock.return_value.write.call_args_list',
            open_mock.return_value.write.call_args_list,
        )
        open_mock.assert_called_with('/some/path/instance_profile.yaml', 'w')

        open_mock.return_value.write.assert_has_calls(
            [
                mock.call('telemetry_enabled'),
                mock.call(':'),
                mock.call(' '),
                mock.call('false'),
                mock.call('\n'),
            ]
        )

    del os.environ['DAGSTER_HOME']
