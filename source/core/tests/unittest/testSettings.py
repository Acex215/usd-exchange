# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import inspect
import os
import subprocess
import sys

import usdex.core
import usdex.test
from pxr import Tf


class SettingsTest(usdex.test.TestCase):

    def assertEnvSetting(self, setting, value, command, expectedOutputPattern):
        env = os.environ.copy()

        # PXR env vars that drive TfEnvSettings can cause extra stderr output
        # We aren't concerned with any non-default behavior in these tests, so
        # we clear those env vars to ensure a consistent stderr stream.
        # Important: PXR_WORK_THREAD_LIMIT my be set in CI to reduce thread contention
        # on multi-job runners. Do not invoke multiple threads from these tests.
        for key in list(env.keys()):
            if key.startswith("PXR_"):
                del env[key]

        env[setting] = str(value)
        result = subprocess.run(
            [sys.executable, "-c", command],
            env=env,
            capture_output=True,
            encoding="utf-8",
            universal_newlines=True,
        )
        if result.returncode != 0:
            self.fail(msg=result.stderr)
        if expectedOutputPattern == "":
            self.assertEqual(result.stderr, "")
        else:
            self.assertRegexpMatches(result.stderr, expectedOutputPattern)

    def testOmniTranscodingSetting(self):
        self.assertEqual(usdex.core.enableOmniTranscodingSetting, "USDEX_ENABLE_OMNI_TRANSCODING")
        self.assertIsNotNone(Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting))
        self.assertIsInstance(Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting), bool)
        environValue = os.environ.get("USDEX_ENABLE_OMNI_TRANSCODING", True)
        if environValue in ("False", "false", "0"):
            self.assertFalse(Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting))
        else:
            self.assertTrue(Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting))

    def testEnableOmniTranscodingSetting(self):
        # when enabled the transcoding algorithm is used to make valid identifiers
        self.assertEnvSetting(
            setting=usdex.core.enableOmniTranscodingSetting,
            value=True,
            command=inspect.cleandoc(
                """
                import usdex.core
                from pxr import Tf
                assert Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting) == True
                assert usdex.core.getValidPrimName(r"sphere%$%#ad@$1") == "tn__spheread1_kAHAJ8jC"
                assert usdex.core.getValidPrimName("1 mesh") == "tn__1mesh_c5"
                assert usdex.core.getValidPrimName("") == "tn__"
                """
            ),
            expectedOutputPattern="",
        )

    def testDisableOmniTranscodingSetting(self):
        # when disabled a fallback algorithm is used to make valid identifiers
        self.assertEnvSetting(
            setting=usdex.core.enableOmniTranscodingSetting,
            value=False,
            command=inspect.cleandoc(
                """
                import usdex.core
                from pxr import Tf
                assert Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting) == False
                assert usdex.core.getValidPrimName(r"sphere%$%#ad@$1") == "sphere____ad__1"
                assert usdex.core.getValidPrimName("1 mesh") == "_1_mesh"
                assert usdex.core.getValidPrimName("") == "_"
                """
            ),
            expectedOutputPattern=".*USDEX_ENABLE_OMNI_TRANSCODING is overridden to 'false'.*",
        )

    def testInvalidOmniTranscodingSetting(self):
        # non-bool values are handled gracefully
        self.assertEnvSetting(
            setting=usdex.core.enableOmniTranscodingSetting,
            value="invalid value type",
            command=inspect.cleandoc(
                """
                import usdex.core
                from pxr import Tf
                assert Tf.GetEnvSetting(usdex.core.enableOmniTranscodingSetting) == False
                assert usdex.core.getValidPrimName(r"sphere%$%#ad@$1") == "sphere____ad__1"
                assert usdex.core.getValidPrimName("1 mesh") == "_1_mesh"
                assert usdex.core.getValidPrimName("") == "_"
                """
            ),
            expectedOutputPattern=".*USDEX_ENABLE_OMNI_TRANSCODING is overridden to 'false'.*",
        )
