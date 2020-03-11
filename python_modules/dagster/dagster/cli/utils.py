from __future__ import print_function

import sys

import click
import six

from dagster import check
from dagster.core.execution.compute_logs import tail_polling
from dagster.core.telemetry import (
    execute_disable_telemetry,
    execute_enable_telemetry,
    execute_reset_telemetry_profile,
)


def create_utils_cli_group():
    group = click.Group(name="utils")
    group.add_command(tail_command)
    group.add_command(reset_telemetry_profile)
    group.add_command(disable_telemetry)
    group.add_command(enable_telemetry)
    return group


def extract_string_param(name, value):
    if value and not isinstance(value, six.string_types):
        if len(value) == 1:
            return value[0]
        else:
            check.failed(
                'Can only handle zero or one {name} args. Got {value}'.format(
                    name=repr(name), value=repr(value)
                )
            )
    return value


@click.command(name='tail', help='Cross-platform file tailing')
@click.argument('filepath')
@click.option('--parent-pid', help="Process pid to watch for termination")
@click.option('--io-type', help="Whether to stream to stdout/stderr", default='stdout')
def tail_command(filepath, parent_pid, io_type):
    filepath = extract_string_param('filepath', filepath)
    parent_pid = extract_string_param('parent_pid', parent_pid)
    io_type = extract_string_param('io_type', io_type)
    stream = sys.stdout if io_type == 'stdout' else sys.stderr
    tail_polling(filepath, stream, parent_pid)


@click.command(
    name='reset_telemetry_profile',
    help='Generate a new user identifier for telemetry. Requires $DAGSTER_HOME to be set. \
        For more information, check out the docs at TODO.',
)
def reset_telemetry_profile():
    execute_reset_telemetry_profile()


@click.command(
    name='disable_telemetry',
    help='TODO: standardize verbiage. Dagster is an open source tool that tracks user \
        engagement in order to provide the best service possible. Disable telemetry. \
        Requires $DAGSTER_HOME to be set',
)
def disable_telemetry():
    execute_disable_telemetry()


@click.command(
    name='enable_telemetry',
    help='TODO: standardize verbiage. Also, should this modify env var as well as yaml? \
        Dagster is an open source tool that tracks user \
        engagement in order to provide the best service possible. Enable telemetry.',
)
def enable_telemetry():
    execute_enable_telemetry()


utils_cli = create_utils_cli_group()
