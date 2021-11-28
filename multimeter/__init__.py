"""Measure resource usage of your python code"""
from .multimeter import Multimeter
from .probe import ResourceProbe
from .storages.dummy import DummyStorage
from .storages.json import JsonFileStorage


__version__ = '0.1'
