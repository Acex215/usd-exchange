# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import sys
import unittest

import omni.repo.man
import omni.repo.man.build_number
import usdex.core
from pxr import Usd


class CoreTest(unittest.TestCase):

    def testVersion(self):
        changes = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "CHANGELOG.md")
        version = omni.repo.man.build_number.generate_build_number_from_file(changes)
        self.assertEqual(usdex.core.version(), version)

    def testUsdVersion(self):
        usd_ver = omni.repo.man.resolve_tokens("${usd_ver}")
        year, month = usd_ver.split(".")
        self.assertEqual(Usd.GetVersion(), (0, int(year), int(month)))

    def testPythonVersion(self):
        python_ver = omni.repo.man.resolve_tokens("${python_ver}")
        major, minor = python_ver.split(".")
        self.assertEqual((sys.version_info.major, sys.version_info.minor), (int(major), int(minor)))

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
