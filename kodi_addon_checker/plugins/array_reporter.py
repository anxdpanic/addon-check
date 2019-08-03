"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

from kodi_addon_checker.report import Record
from kodi_addon_checker.reporter import Reporter, reporter


@reporter(name="array", enabled=False)
class ArrayReporter(Reporter):
    """ Provide Report in an array
    """

    def __init__(self):
        self.reports = []

    def report(self, report):
        """ Add record/report to current reports
        :param report: record/report to add to the current reports
        """
        if isinstance(report, Record):
            self._append(report)

    def _append(self, report: Record):
        """ Append record/report to the current reports
        :param report: record/report to add to the current reports
        """
        self.reports.append(report)
