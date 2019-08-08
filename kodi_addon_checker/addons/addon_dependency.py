"""
    Copyright (C) 2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import xml.etree.ElementTree as ET
from distutils.version import LooseVersion


class AddonDependency():
    def __init__(self, import_xml: ET.Element):
        super(AddonDependency, self).__init__()
        self._addon_id = import_xml.get('addon')
        self._version = None
        if import_xml.get('version') is not None:
            self._version = LooseVersion(import_xml.get('version'))
        self._optional = import_xml.get('optional', False)

    @property
    def addon_id(self):
        """
        :return: addon dependency id
        """
        return self._addon_id

    @property
    def version(self):
        """
        :return: addon dependency version
        """
        return self._version

    @property
    def optional(self):
        """
        :return: whether the addon dependency is optional
        """
        return self._optional
