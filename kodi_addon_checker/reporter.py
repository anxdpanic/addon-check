"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import inspect
from abc import ABC


class Reporter(ABC):
    """base class for Reporter plugins
    """
    _name = ''
    _enabled = False

    def report(self, report):
        """
        add a report/record
        :param report: report/record to add
        """
        raise NotImplementedError

    @property
    def name(self):
        """
        :return: Reporter plugin's name
        """
        return self._name

    @name.setter
    def name(self, reporter_name: str):
        """
        set the Reporter plugin's name
        :param reporter_name: name of the Reporter
        :return:
        """
        self._name = reporter_name

    @property
    def enabled(self):
        """
        :return: Reporter plugin's enabled status
        """
        return self._enabled

    @enabled.setter
    def enabled(self, status: bool):
        """
        set the Reporter plugin's enabled status
        :param status: enabled status of the Reporter
        :return:
        """
        self._enabled = status

    def __str__(self):
        """
        Text representation of the reporter plugin's name and status
        :return: text representation of the reporter plugin's name and status
        """
        return "Reporter %s is currently %s" % (self.name, 'enabled' if self.enabled else 'disabled')


class ReportManager():
    reporters = {}

    @classmethod
    def register(cls, reporter_clazz: Reporter, name: str, enabled: bool):
        """
        Register a Reporter plugin
        :param reporter_clazz: Reporter plugin class
        :param name: name of the Reporter plugin
        :param enabled: enabled status of the Reporter plugin
        :return:
        """
        clazz = reporter_clazz()
        clazz.name = name
        clazz.enabled = enabled
        cls.reporters[name] = clazz

    @classmethod
    def enable(cls, names):
        """
        Enable only the given list of names and disable the rest.
        :param names: list of reporter names
        :return: None
        """
        for name, clazz in cls.reporters.items():
            clazz.enabled = name in names

    @classmethod
    def getEnabledReporters(cls):
        return [reporter for reporter in cls.reporters.values() if reporter.enabled]


def reporter(name, enabled=False):
    def _reporter(clazz):
        if inspect.isclass(clazz):
            if not hasattr(clazz, "report") or len(inspect.signature(getattr(clazz, "report")).parameters.items()) != 2:
                raise RuntimeError("Reporter must have a function 'report(self, report: Report)")
        else:
            raise RuntimeError("Reporter must be a class")

        # Register the reporter
        ReportManager.register(clazz, name, enabled)
        return clazz

    return _reporter
