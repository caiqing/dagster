import os

from dagster import seven
from dagster.core.telemetry import (
    _get_user_id,
    execute_disable_telemetry,
    execute_enable_telemetry,
    execute_reset_telemetry_profile,
    log_action,
)
from dagster.seven import mock


def mock_uuid():
    return 'some_random_uuid'


@mock.patch(seven.builtin_print())
@mock.patch('uuid.uuid4', mock_uuid)
def test_reset_telemetry_profile(mocked_print):
    open_mock = mock.mock_open()
    with mock.patch("dagster.core.telemetry.open", open_mock, create=True):
        execute_reset_telemetry_profile()
        open_mock.assert_not_called()

        assert mocked_print.mock_calls == seven.print_single_line_str(
            'Must set $DAGSTER_HOME environment variable to reset profile'
        )

        os.environ['DAGSTER_HOME'] = '/dagster/home/path/'
        execute_reset_telemetry_profile()
        open_mock.assert_called_with('/dagster/home/path/dagster.yaml', 'w')

        open_mock.return_value.write.assert_has_calls(
            [
                mock.call('telemetry'),
                mock.call(':'),
                mock.call('\n'),
                mock.call('  '),
                mock.call('user_id'),
                mock.call(':'),
                mock.call(' '),
                mock.call('some_random_uuid'),
                mock.call('\n'),
            ]
        )

    del os.environ['DAGSTER_HOME']


@mock.patch(seven.builtin_print())
def test_enable_telemetry(mocked_print):
    open_mock = mock.mock_open()
    with mock.patch("dagster.core.telemetry.open", open_mock, create=True):
        execute_enable_telemetry()
        open_mock.assert_not_called()
        assert mocked_print.mock_calls == seven.print_single_line_str(
            'Must set $DAGSTER_HOME environment variable to enable telemetry'
        )

        os.environ['DAGSTER_HOME'] = '/dagster/home/path/'
        execute_enable_telemetry()

        open_mock.assert_called_with('/dagster/home/path/dagster.yaml', 'w')

        open_mock.return_value.write.assert_has_calls(
            [
                mock.call('telemetry'),
                mock.call(':'),
                mock.call('\n'),
                mock.call('  '),
                mock.call('enabled'),
                mock.call(':'),
                mock.call(' '),
                mock.call('true'),
                mock.call('\n'),
            ]
        )

    del os.environ['DAGSTER_HOME']


@mock.patch(seven.builtin_print())
def test_disable_telemetry(mocked_print):
    open_mock = mock.mock_open()
    with mock.patch("dagster.core.telemetry.open", open_mock, create=True):
        execute_disable_telemetry()
        open_mock.assert_not_called()

        assert mocked_print.mock_calls == seven.print_single_line_str(
            'Must set $DAGSTER_HOME environment variable to disable telemetry'
        )

        os.environ['DAGSTER_HOME'] = '/dagster/home/path/'
        execute_disable_telemetry()

        open_mock.assert_called_with('/dagster/home/path/dagster.yaml', 'w')

        open_mock.return_value.write.assert_has_calls(
            [
                mock.call('telemetry'),
                mock.call(':'),
                mock.call('\n'),
                mock.call('  '),
                mock.call('enabled'),
                mock.call(':'),
                mock.call(' '),
                mock.call('false'),
                mock.call('\n'),
            ]
        )

    del os.environ['DAGSTER_HOME']


def test_telemetry_disabled():
    with seven.TemporaryDirectory() as tmpdir_path:
        os.environ['DAGSTER_HOME'] = tmpdir_path
        execute_disable_telemetry()
        with mock.patch('requests.post') as requests_mock:
            log_action('did something', {})
        requests_mock.assert_not_called()


def test_telemetry_enabled():
    with seven.TemporaryDirectory() as tmpdir_path:
        os.environ['DAGSTER_HOME'] = tmpdir_path
        execute_enable_telemetry()
        (user_id, telemetry_enabled) = _get_user_id()
        assert telemetry_enabled == True
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
