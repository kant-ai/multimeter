"""Command line tool for setting up a docker based visualization"""
import argparse
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import time


logger = logging.getLogger(__name__)


def _check_docker_compose_available():
    """
    Check is docker-compose is available.

    Tries to run 'docker-compose' and get its version number. If this command fails,
    exit with an error telling the use how to install it.
    """
    try:
        version_info = subprocess.check_output(['docker-compose', '--version'])
        logger.debug(version_info)
    except OSError:
        logger.error(
            "docker-compose not found. Please make sure it is in PATH. "
            "For install instruction, visit https://docs.docker.com/compose/install/"
        )
        sys.exit(-1)


def _get_resources_dir():
    """Return the directory containing the resources used for setting up the visu"""
    multimeter_directory = pathlib.Path(__file__).parent
    visu_resources_directory = multimeter_directory / 'visualization'
    return visu_resources_directory


def _execute_docker_command(*args, env=None):
    """
    Execute a docker-compose command.

    If the command fails, we log an error and call sys.exit().

    Args:
        *args (str): Additional arguments for the docker-compose call.
        env (Dict[str,str]: Environment variables to use for the call.

    Returns:
        The text output of the command.

    """
    try:
        return subprocess.check_output(
            [
                'docker-compose',
            ]
            + list(args),
            env=dict(os.environ, **env),
            cwd=_get_resources_dir(),
        )
    except subprocess.CalledProcessError as error:
        logger.error("Exited with %d and output %s", error.returncode, error.output)
        sys.exit(-4)


def install(args):  # pylint: disable=too-many-locals
    """
    Install the visualization container and configure them.

    Args:
        args (argparse.Namespace): The arguments parsed from command-line.
    """

    config_file_path = pathlib.Path(args.config_file)
    if config_file_path.exists():
        logger.error("Visualization config already found at %s", args.config_file)
        sys.exit(-2)

    data_directory = pathlib.Path(args.data_dir)

    multimeter_directory = pathlib.Path(__file__).parent
    visu_resources_directory = multimeter_directory / 'visualization'
    grafana_resources_directory = visu_resources_directory / 'grafana'
    grafana_provisioning_directory = grafana_resources_directory / 'provisioning'
    grafana_dashboards_templates_directory = grafana_resources_directory / 'dashboards'

    influx_resources_directory = visu_resources_directory / 'influxdb'

    org = args.org
    data_bucket = args.bucket

    data_directory.mkdir(parents=True, exist_ok=True)
    influx_dir = data_directory / 'influxdb'
    influx_dir.mkdir(exist_ok=True)
    influx_data_dir = influx_dir / 'data'
    influx_data_dir.mkdir(exist_ok=True)
    influx_config_dir = influx_dir / 'config'
    influx_config_dir.mkdir(exist_ok=True)

    grafana_dir = data_directory / 'grafana'

    new_env = {
        'UID': str(os.getuid()),
        'DATA_DIR': str(data_directory.absolute()),
        'INFLUX_ADMIN': 'admin',
        'INFLUX_PASSWORD': 'admin123',
        'INFLUX_ORG': org,
        'INFLUX_BUCKET': data_bucket,
        'GRAFANA_PROVISIONING_DIR': str(grafana_provisioning_directory.absolute()),
    }

    # Starting only influxdb
    logger.info("Create and start influxdb...")
    _execute_docker_command('up', '-d', 'influxdb2', env=new_env)

    logger.info("Waiting for influxdb to come up...")
    time.sleep(5)

    #  create authorization token
    logger.info("Create influxdb authorization token for grafana")
    output = _execute_docker_command(
        'exec',
        'influxdb2',
        'influx',
        'auth',
        'create',
        '-o',
        org,
        '-d',
        '"Token for Grafana access"',
        '--all-access',
        '--json',
        env=new_env,
    )
    json_result = json.loads(output)
    token = json_result['token']
    logger.debug("Created token %s", token)
    new_env['GRAFANA_INFLUX_DATA_SOURCE_TOKEN'] = token

    #  load example data
    logger.info("Load example data into influxdb")
    _load_example_data(influx_data_dir, influx_resources_directory)
    _execute_docker_command(
        'exec',
        'influxdb2',
        'influx',
        'write',
        '-o',
        org,
        '-b',
        data_bucket,
        '-t',
        token,
        '-f',
        '/var/lib/influxdb2/example.line',
        env=new_env,
    )

    _copy_dashboards_from_templates(
        data_bucket, grafana_dashboards_templates_directory, grafana_dir
    )

    logger.info("Create and start grafana...")
    _execute_docker_command('up', '-d', 'grafana8', env=new_env)

    _save_visu_config(config_file_path, new_env)

    _print_instructions()


def _load_example_data(influx_data_dir, influx_resources_directory):
    example_file = influx_resources_directory.absolute() / 'example.line'
    shutil.copy(example_file, influx_data_dir)


def _copy_dashboards_from_templates(
    data_bucket, grafana_dashboards_templates_directory, grafana_dir
):
    logger.info("Copy grafana dashboard template")
    grafana_dashboards_data_directory = grafana_dir / 'dashboards'
    grafana_dashboards_data_directory.mkdir(exist_ok=True, parents=True)
    for template_path in grafana_dashboards_templates_directory.iterdir():
        with open(template_path, 'r', encoding='utf-8') as file:
            template = file.read()

        dashboard = template.replace('${INFLUX_BUCKET}', data_bucket)

        dashboard_path = grafana_dashboards_data_directory / template_path.name
        with open(dashboard_path, 'w', encoding='utf-8') as file:
            file.write(dashboard)


def _save_visu_config(config_file_path, new_env):
    logger.info("Save visualization config to %s", str(config_file_path))
    with open(config_file_path, 'w', encoding='utf-8') as stream:
        json.dump({'environment': new_env}, stream)


def _print_instructions():
    logger.info("")
    logger.info("Visualization successfully set up.")
    logger.info("Example dashboard:")
    logger.info(
        "http://localhost:3000/d/6V5fU2t7r/multimeter?"
        "orgId=1&var-measurementId=example&from=1638479887312&to=1638479894580"
    )
    logger.info("Default username/password: admin/admin")
    logger.info("Database UI:")
    logger.info("http://localhost:8086/")
    logger.info("Default username/password: admin/admin123")


def remove(args):
    """
    Remove the visualization container and delete the data stored for the visu.

    Args:
        args (argparse.Namespace): The arguments parsed from command-line.
    """

    config_file_path = pathlib.Path(args.config_file)
    if not config_file_path.exists():
        logger.error("No config file found at %s", args.config_file)
        sys.exit(-3)

    with open(config_file_path, 'r', encoding='utf-8') as stream:
        environment = json.load(stream)['environment']

    logger.info("Remove docker containers...")
    _execute_docker_command('down', env=environment)

    logger.info("Remove data directory %s", str(environment['DATA_DIR']))
    shutil.rmtree(environment['DATA_DIR'])

    logger.info("Remove visualization config in %s", str(config_file_path))
    config_file_path.unlink()


def start(args):
    """
    Start the visualization container.

    Args:
        args (argparse.Namespace): The arguments parsed from command-line.
    """

    config_file_path = pathlib.Path(args.config_file)
    if not config_file_path.exists():
        logger.error("No config file found at %s", args.config_file)
        sys.exit(-3)

    with open(config_file_path, 'r', encoding='utf-8') as stream:
        environment = json.load(stream)['environment']

    logger.info("Starting docker containers...")
    _execute_docker_command('start', env=environment)


def stop(args):
    """
    Stop the visualization container.

    Args:
        args (argparse.Namespace): The arguments parsed from command-line.
    """

    config_file_path = pathlib.Path(args.config_file)
    if not config_file_path.exists():
        logger.error("No config file found at %s", args.config_file)
        sys.exit(-3)

    with open(config_file_path, 'r', encoding='utf-8') as stream:
        environment = json.load(stream)['environment']

    logger.info("Stopping docker containers...")
    _execute_docker_command('stop', env=environment)


def main(args=None):
    """
    Main function for the visualization tool.
    """
    multimeter_dir = pathlib.Path.home() / '.multimeter'
    multimeter_dir.mkdir(exist_ok=True)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(fmt='%(message)s'))
    stdout_handler.level = logging.INFO
    file_handler = logging.FileHandler(multimeter_dir / 'visu.log')
    file_handler.level = logging.DEBUG
    file_handler.setFormatter(
        logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[stdout_handler, file_handler],
    )

    logger.debug("Command line arguments: %s", args)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.set_defaults(command=lambda _: parser.print_help())
    parser.add_argument(
        '-c',
        '--config',
        dest='config_file',
        help="The file where the config for the visualization is stored.",
        default=multimeter_dir / 'visu.config.json',
    )
    subparsers = parser.add_subparsers(help='sub-command help')
    install_parser = subparsers.add_parser(
        'install', help="Create the necessary docker container and configure them"
    )
    install_parser.add_argument(
        '-d',
        '--dir',
        dest='data_dir',
        help="The directory where the data will be stored.",
        default=multimeter_dir / 'sdocker-data',
    )
    install_parser.add_argument(
        '-o', '--org', dest='org', help="The organization in influx.", default='kantai'
    )
    install_parser.add_argument(
        '-b',
        '--bucket',
        dest='bucket',
        help="The bucket in influx for storing measurements.",
        default='multimeter',
    )
    install_parser.set_defaults(command=install)

    remove_parser = subparsers.add_parser(
        'remove', help="Remove docker containers and remove the stored data"
    )
    remove_parser.set_defaults(command=remove)

    start_parser = subparsers.add_parser('start', help="Start the visualization")
    start_parser.set_defaults(command=start)

    stop_parser = subparsers.add_parser('stop', help="Stop the visualization")
    stop_parser.set_defaults(command=stop)

    _check_docker_compose_available()

    args = parser.parse_args(args)
    args.command(args)


if __name__ == '__main__':
    main()
