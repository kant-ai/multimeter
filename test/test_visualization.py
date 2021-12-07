import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest.mock

from multimeter.visualization import install, main, remove, start, stop


class TestVisualization(unittest.TestCase):

    def setUp(self):
        self.subprocess_patcher = unittest.mock.patch("multimeter.visualization.subprocess.check_output")
        self.subprocess_mock = self.subprocess_patcher.start()
        self.args = type('', (), {})()
        self.home_patcher = unittest.mock.patch("multimeter.visualization.pathlib.Path.home")
        self.home_mock = self.home_patcher.start()
        self.home_mock.return_value = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        self.subprocess_patcher.stop()
        shutil.rmtree(self.home_mock.return_value)
        self.home_patcher.stop()

    def test_install_exits_when_docker_fails(self):
        config_path = tempfile.mktemp()

        self.args.config_file = config_path
        self.args.data_dir = tempfile.mkdtemp()
        try:
            self.args.org = 'myorg'
            self.args.bucket = 'mybucket'
            self.subprocess_mock.side_effect = subprocess.CalledProcessError(-1, '')
            with self.assertRaises(SystemExit):
                install(self.args)
        finally:
            shutil.rmtree(self.args.data_dir)

    def test_install_exits_when_config_exists(self):
        config = {'environment': {'my': 'config'}}
        _, config_path = tempfile.mkstemp()
        try:
            with open(config_path, 'w') as config_file:
                json.dump(config, config_file)
            self.args.config_file = config_path

            with self.assertRaises(SystemExit):
                install(self.args)
        finally:
            pathlib.Path(config_path).unlink()

    def test_install_creates_config(self):
        config_path = tempfile.mktemp()
        try:
            self.args.config_file = config_path
            self.args.data_dir = tempfile.mkdtemp()
            self.args.org = 'myorg'
            self.args.bucket = 'mybucket'
            with unittest.mock.patch('json.loads', return_value={'token': 'mytoken'}):
                install(self.args)
            self.assertTrue(pathlib.Path(config_path).exists())
        finally:
            pathlib.Path(config_path).unlink()

    def test_remove_exits_without_config_file(self):
        setattr(self.args, 'config_file', '/invalid/config/file')
        with self.assertRaises(SystemExit):
            remove(self.args)

    def test_remove_runs_with_environment_from_config(self):
        data_dir = tempfile.mkdtemp()
        config = {'environment': {'my': 'config', 'DATA_DIR': data_dir}}
        _, config_path = tempfile.mkstemp()
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file)

        setattr(self.args, 'config_file', config_path)
        remove(self.args)

        call_args, call_kwargs = self.subprocess_mock.call_args
        self.assertEqual(['docker-compose', 'down'], call_args[0])
        self.assertIn(('my', 'config'), call_kwargs['env'].items())

        self.assertFalse(pathlib.Path(data_dir).exists())
        self.assertFalse(pathlib.Path(config_path).exists())

    def test_start_exits_without_config_file(self):
        setattr(self.args, 'config_file', '/invalid/config/file')
        with self.assertRaises(SystemExit):
            start(self.args)

    def test_start_runs_with_environment_from_config(self):
        config = {'environment': {'my': 'config'}}
        _, config_path = tempfile.mkstemp()
        try:
            with open(config_path, 'w') as config_file:
                json.dump(config, config_file)

            setattr(self.args, 'config_file', config_path)
            start(self.args)

            call_args, call_kwargs = self.subprocess_mock.call_args
            self.assertEqual(['docker-compose', 'start'], call_args[0])
            self.assertIn(('my', 'config'), call_kwargs['env'].items())
        finally:
            pathlib.Path(config_path).unlink()

    def test_stop_exits_without_config_file(self):
        setattr(self.args, 'config_file', '/invalid/config/file')
        with self.assertRaises(SystemExit):
            stop(self.args)

    def test_stop_runs_with_environment_from_config(self):
        config = {'environment': {'my': 'config'}}
        _, config_path = tempfile.mkstemp()
        try:
            with open(config_path, 'w') as config_file:
                json.dump(config, config_file)

            setattr(self.args, 'config_file', config_path)
            stop(self.args)

            call_args, call_kwargs = self.subprocess_mock.call_args
            self.assertEqual(['docker-compose', 'stop'], call_args[0])
            self.assertIn(('my', 'config'), call_kwargs['env'].items())
        finally:
            pathlib.Path(config_path).unlink()

    def test_main_exits_without_docker_compose(self):
        self.subprocess_mock.side_effect = OSError
        with self.assertRaises(SystemExit):
            main()
        self.subprocess_mock.assert_called_with(['docker-compose', '--version'])

    def test_main_exits_without_docker_compose(self):
        self.subprocess_mock.side_effect = OSError
        with self.assertRaises(SystemExit):
            main()
        self.subprocess_mock.assert_called_with(['docker-compose', '--version'])

    def test_main_exits_when_config_exists(self):
        config = {'environment': {'my': 'config'}}
        _, config_path = tempfile.mkstemp()
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file)

        with self.assertRaises(SystemExit):
            main(['-c', config_path, 'install'])

    def test_main_exits_when_help_is_in_args(self):
        with self.assertRaises(SystemExit):
            main(['-h'])

    def test_main_shows_help_without_args(self):
        main([])


if __name__ == '__main__':
    unittest.main()
