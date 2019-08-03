"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
import logging.handlers


class Logger:

    def __init__(self, name, filename, enabled=False):
        """
        :name: name of the logger to create
        :filename: path and filename of the debug log
        :enabled: enable to write the log to provided filename, otherwise uses a NullHandler
        """
        self.name = name
        self.filename = filename
        self.enabled = enabled
        self.logger = None

    def create_logger(self):
        """Creates a logger format for error logging
        :return: created logger
        """
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.add_handler()

        return self.logger

    def add_handler(self):
        """ add handler to the logger
        """
        if self.enabled:
            formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s:%(name)s:%(funcName)s: %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')

            debug_log_handler = logging.handlers.RotatingFileHandler(self.filename, encoding='utf-8', mode="w")
            debug_log_handler.setLevel(logging.DEBUG)
            debug_log_handler.setFormatter(formatter)
            self.logger.addHandler(debug_log_handler)
        else:
            self.logger.addHandler(logging.NullHandler())
