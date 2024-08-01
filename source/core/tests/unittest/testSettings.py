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

    def assertEnvSetting(self, setting, value, command, expectedOutputPattern=None):
        env = os.environ.copy()
        env[setting] = str(value)
        try:
            output = subprocess.check_output(
                [sys.executable, "-c", command],
                env=env,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            output = e.output
            self.fail(msg=output)
        finally:
            if expectedOutputPattern:
                self.assertRegexpMatches(output, expectedOutputPattern)

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
