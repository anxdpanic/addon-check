"""
    Copyright (C) 2017-2018 Team Kodi
    This file is part of Kodi - kodi.tv

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/README.md for more information.
"""

import logging
from distutils.version import LooseVersion

from .addons.addon import Addon
from .kodi_version import KodiVersion
from .record import INFORMATION, PROBLEM, WARNING, Record
from .report import Report

COMMON_IGNORE_DEPS = ['xbmc.metadata.scraper.albums', 'xbmc.metadata.scraper.movies',
                      'xbmc.metadata.scraper.musicvideos', 'xbmc.metadata.scraper.tvshows',
                      'xbmc.metadata.scraper.library', 'xbmc.ui.screensaver', 'xbmc.player.musicviz',
                      'xbmc.python.pluginsource', 'xbmc.python.script', 'xbmc.python.weather', 'xbmc.python.lyrics',
                      'xbmc.python.library', 'xbmc.python.module', 'xbmc.subtitle.module', 'kodi.context.item',
                      'kodi.game.controller', 'xbmc.gui.skin', 'xbmc.webinterface', 'xbmc.addon.repository',
                      'xbmc.pvrclient', 'kodi.gameclient', 'kodi.peripheral', 'kodi.resource', 'xbmc.addon.video',
                      'xbmc.addon.audio', 'xbmc.addon.image', 'xbmc.addon.executable', 'kodi.addon.game',
                      'kodi.audioencoder', 'kodi.audiodecoder', 'xbmc.service', 'kodi.resource.images',
                      'kodi.resource.language', 'kodi.resource.uisounds', 'kodi.resource.games',
                      'kodi.resource.font', 'kodi.inputstream', 'kodi.vfs', 'kodi.imagedecoder', 'xbmc.addon',
                      'xbmc.gui', 'xbmc.json', 'xbmc.metadata', 'xbmc.python', 'script.module.pil']

EXTENSIONS = {"kodi.gameclient": "kodi.binary.instance.game",
              "xbmc.gui.skin": "xbmc.gui",
              "kodi.vfs": "kodi.binary.instance.vfs",
              "xbmc.metadata.scraper.albums": "xbmc.metadata",
              "xbmc.metadata.scraper.artists": "xbmc.metadata",
              "xbmc.metadata.scraper.library": "xbmc.metadata",
              "xbmc.metadata.scraper.movies": "xbmc.metadata",
              "xbmc.metadata.scraper.musicvideos": "xbmc.metadata",
              "xbmc.metadata.scraper.tvshows": "xbmc.metadata",
              "xbmc.pvrclient": "kodi.binary.instance.pvr",
              "xbmc.python.library": "xbmc.python",
              "xbmc.python.lyrics": "xbmc.python",
              "xbmc.python.module": "xbmc.python",
              "xbmc.python.pluginsource": "xbmc.python",
              "xbmc.python.script": "xbmc.python",
              "xbmc.python.weather": "xbmc.python",
              "xbmc.ui.screensaver": "xbmc.python",
              "xbmc.webinterface": "xbmc.webinterface",
              }

VERSION_ATTRB = {'xbmc.python': {'gotham': '2.14.0', 'helix': '2.19.0', 'isengard': '2.20.0',
                                 'jarvis': '2.24.0', 'krypton': '2.25.0', 'leia': '2.26.0'}}

LOGGER = logging.getLogger(__name__)


def check_addon_dependencies(report: Report, repo_addons: dict, parsed_xml, branch_name: str):
    """Check for any new dependencies in addon.xml file and reports them
        :parsed_xml: parsed addon.xml file
        :repo_addons: dictionary having all the addon list of a particular
                        version of kodi
        :branch_name: name of the kodi branch/version
    """

    addon = Addon(parsed_xml)
    ignore = _get_ignore_list(KodiVersion(branch_name))

    for dependency in addon.dependencies:
        if dependency.addon_id in ignore and not dependency.optional:
            pass

        elif dependency.addon_id not in repo_addons:
            report.add(Record(INFORMATION if dependency.optional else PROBLEM,
                              "{} dependency {} is not available in current repository"
                              .format("Optional" if dependency.optional else "Required", dependency.addon_id)))

        elif dependency.version is None:
            report.add(Record(INFORMATION if dependency.optional else WARNING,
                              "{} dependency {} does not require a minimum version, available: {}"
                              .format("Optional" if dependency.optional else "Required", dependency.addon_id,
                                      repo_addons.find(dependency.addon_id).version)))

        elif repo_addons.find(dependency.addon_id).version < dependency.version:
            report.add(Record(INFORMATION if dependency.optional else PROBLEM,
                              "Version mismatch for {} dependency {}, required: {}, Available: {}"
                              .format("optional" if dependency.optional else "required", dependency.addon_id,
                                      dependency.version, repo_addons.find(dependency.addon_id).version)))

        if dependency.addon_id in VERSION_ATTRB:
            try:
                version = VERSION_ATTRB[dependency.addon_id][branch_name]
                if LooseVersion(version) != dependency.version:
                    report.add(Record(WARNING, "For {} it is advised to set {} version to {}"
                                      .format(branch_name, dependency.addon_id, version)))
            except KeyError:
                LOGGER.warning("Misconfiguration in VERSION_ATTRB of check_dependencies")

    _check_extensions(report, parsed_xml, addon)


def check_reverse_dependencies(report: Report, addon: str, branch_name: str, all_repo_addons: dict):
    """Check for orphaned addon i.e the addons that are not requirement of any other addon.

      :addon: addon that is to be checked
      :branch_name: name of the branch on which the
                    checks are being performed
      :all_repo_addons: a nested list having information
                        about all the repo addonst
    """
    addon_in_repo = None
    rdepends = []
    rdepends_lower_branch = []
    branch_found = False

    for branch, repo in sorted(all_repo_addons.items()):
        if not branch_found and branch != branch_name:
            for rdepend in repo.rdepends(addon):
                if rdepend not in rdepends_lower_branch:
                    rdepends_lower_branch.append(rdepend)
            continue
        branch_found = True

        addon_find = repo.find(addon)
        if addon_find and addon_in_repo and addon_find != addon_in_repo:
            break

        addon_in_repo = addon_find

        for rdepend in repo.rdepends(addon):
            if rdepend not in rdepends_lower_branch and rdepend not in rdepends:
                rdepends.append(rdepend)
    if addon.startswith("script.module.") and len(rdepends) + len(rdepends_lower_branch) == 0:
        report.add(Record(WARNING, "This module isn't required by any add-on."))

    if rdepends:
        report.add(Record(INFORMATION, "Reverse dependencies: {} ({})"
                          .format(", ".join(sorted([r.addon_id for r in rdepends])), len(rdepends))))

    if rdepends_lower_branch:
        report.add(Record(INFORMATION, "Reverse dependencies (in lower branches): {} ({})"
                          .format(", ".join(sorted([r.addon_id for r in rdepends_lower_branch])),
                                  len(rdepends_lower_branch))))


def _get_ignore_list(kodi_version: KodiVersion):
    """Generate an dependency ignore list based
       on the branch name
    """

    if kodi_version == KodiVersion("leia"):
        COMMON_IGNORE_DEPS.extend(["script.module.pycryptodome"])

    if kodi_version == KodiVersion("krypton"):
        COMMON_IGNORE_DEPS.extend(["inputstream.adaptive", "inputstream.rtmp"])

    return COMMON_IGNORE_DEPS


def _check_extensions(report: Report, parsed_xml, addon):
    """Check if required dependency exist with comparision to
       the existing extension points

      :addon: class kodi_addon_checker.addons.Addon.Addon
    """
    deps = [dependency.addon_id for dependency in addon.dependencies]

    for extension in parsed_xml.findall("extension"):
        point = extension.get("point")
        if point in EXTENSIONS and EXTENSIONS[point] not in deps:
            report.add(Record(PROBLEM, "{} dependency is required for {} extensions"
                              .format(EXTENSIONS[point], point)))
