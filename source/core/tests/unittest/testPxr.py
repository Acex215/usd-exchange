# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import os
import subprocess
import sys
import unittest


class PxrTest(unittest.TestCase):

    def testPxrImport(self):
        # clear the PATH to avoid test suite bootstrapping the USD install
        env = os.environ.copy()
        env["PATH"] = ""
        # Run in subprocess to avoid usdex.core already being imported
        code = "from pxr import Tf; assert hasattr(Tf, 'Status')"
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, f"Failed to import pxr: {result.stderr.decode()}")
