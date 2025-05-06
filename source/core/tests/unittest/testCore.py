# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import unittest

import usdex.core


def get_changelog_version_string():
    """Get the version string from the CHANGELOG.md"""
    changes = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "CHANGELOG.md")
    with open(changes, "r") as f:
        version = f.readline().strip("# \n")
    return version


class CoreTest(unittest.TestCase):

    def testVersion(self):
        version = get_changelog_version_string()
        self.assertEqual(usdex.core.version(), version)

    def testBuildVersion(self):
        version = get_changelog_version_string()
        self.assertEqual(usdex.core.buildVersion().split("+")[0], version)

    def testModuleSymbols(self):
        allowList = [
            "os",  # module necessary to locate bindings on windows
            "_usdex_core",  # our binding module
            "_StageAlgoBindings",  # hand rolled binding
        ]
        allowList.extend([x for x in dir(usdex.core) if x.startswith("__")])  # private members

        for attr in dir(usdex.core):
            if attr in allowList:
                continue
            self.assertIn(attr, usdex.core.__all__)

        for attr in usdex.core.__all__:
            self.assertIn(attr, dir(usdex.core))
