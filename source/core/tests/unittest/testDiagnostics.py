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
import platform
import subprocess
import sys
from typing import List

import usdex.core
import usdex.test


class DiagnosticsTest(usdex.test.TestCase):

    def setUp(self):
        super().setUp()
        # assert expected defaults
        self.assertEqual(usdex.core.getDiagnosticsLevel(), usdex.core.DiagnosticsLevel.eWarning)
        self.assertEqual(usdex.core.getDiagnosticsOutputStream(), usdex.core.DiagnosticsOutputStream.eStderr)

    def tearDown(self):
        super().tearDown()
        # restore defaults for tests that manipulate them
        usdex.core.setDiagnosticsLevel(usdex.core.DiagnosticsLevel.eWarning)
        usdex.core.setDiagnosticsOutputStream(usdex.core.DiagnosticsOutputStream.eStderr)

    def assertOutputStreams(self, command, expectedStdout: List[str], expectedStderr: List[str], expectSuccess: bool = True):

        # PXR env vars that drive TfEnvSettings can cause extra stderr output
        # We aren't concerned with any non-default behavior in these tests, so
        # we clear those env vars to ensure consistent a stderr stream.
        # Important: PXR_WORK_THREAD_LIMIT my be set in CI to reduce thread contention
        # on multi-job runners. Do not invoke multiple threads from these tests.
        env = os.environ.copy()
        for key in list(env.keys()):
            if key.startswith("PXR_"):
                del env[key]

        result = subprocess.run(
            [sys.executable, "-c", command],
            env=env,
            capture_output=True,
            encoding="utf-8",
            universal_newlines=True,
        )

        failureMessage = f"""
Command:
{command}

Return Code:
{result.returncode}

Stdout:
{result.stdout}

Stderr:
{result.stderr}
"""

        if expectSuccess and result.returncode != 0:
            self.fail(msg=failureMessage)
        elif not expectSuccess and result.returncode == 0:
            # Fatal diagnostics on Linux with restricted ptrace permissions currently cause the process
            # to abort with an incorrect returncode. See OpenUSD GitHub PR3014 for more details.
            returnCodeCanBeTrusted = True
            if platform.system().lower() == "linux" and os.path.exists("/proc/sys/kernel/yama/ptrace_scope"):
                with open("/proc/sys/kernel/yama/ptrace_scope", "r") as f:
                    returnCodeCanBeTrusted = f.read().strip() == "0"
            if returnCodeCanBeTrusted:
                self.fail(msg=failureMessage)

        output = result.stdout.strip("\n").split("\n") if result.stdout else []
        self.assertEqual(len(output), len(expectedStdout), msg=failureMessage)
        for i in range(0, len(expectedStdout)):
            self.assertEqual(output[i], expectedStdout[i])

        if expectSuccess:
            error = result.stderr.strip("\n").split("\n") if result.stderr else []
            self.assertEqual(len(error), len(expectedStderr), msg=failureMessage)
            for i in range(0, len(expectedStderr)):
                self.assertEqual(error[i], expectedStderr[i])
        else:
            # we can't be as strict about what errors print on a crashed process
            error = result.stderr.strip("\n").split("\n") if result.stderr else []
            self.assertLessEqual(len(expectedStderr), len(error), msg=failureMessage)
            for i in range(0, len(expectedStderr)):
                self.assertIn(expectedStderr[i], error)

    def testActivation(self):
        self.assertTrue(usdex.core.isDiagnosticsDelegateActive())  # activated in setUpClass
        usdex.core.deactivateDiagnosticsDelegate()
        self.assertFalse(usdex.core.isDiagnosticsDelegateActive())
        usdex.core.activateDiagnosticsDelegate()
        self.assertTrue(usdex.core.isDiagnosticsDelegateActive())

    def testOutputFormatting(self):
        command = inspect.cleandoc(
            """
            import usdex.core
            from pxr import Tf

            def emitDiagnostics():
                {body}

            usdex.core.setDiagnosticsLevel(usdex.core.{level})

            usdex.core.activateDiagnosticsDelegate()
            emitDiagnostics()

            usdex.core.deactivateDiagnosticsDelegate()
            emitDiagnostics()

            usdex.core.activateDiagnosticsDelegate()
            emitDiagnostics()
            """
        )

        self.assertOutputStreams(
            command=command.format(
                level=usdex.core.DiagnosticsLevel.eWarning,
                body=inspect.cleandoc(
                    """
                    Tf.Warn("This is a warning")
                    """
                ),
            ),
            expectedStdout=[],
            expectedStderr=[
                "[Warning] [__main__.emitDiagnostics] This is a warning",  # usdex formatting
                "Warning: in __main__.emitDiagnostics at line 5 of <string> -- This is a warning",  # default formatting
                "[Warning] [__main__.emitDiagnostics] This is a warning",  # usdex formatting
            ],
        )

        self.assertOutputStreams(
            command=command.format(
                level=usdex.core.DiagnosticsLevel.eStatus,
                body=inspect.cleandoc(
                    """
                    Tf.Status("This is a status")
                    """
                ),
            ),
            expectedStdout=[],
            expectedStderr=[
                "[Status] [__main__.emitDiagnostics] This is a status",  # usdex formatting
                "Status: in __main__.emitDiagnostics at line 5 of <string> -- This is a status",  # default formatting
                "[Status] [__main__.emitDiagnostics] This is a status",  # usdex formatting
            ],
        )

        pythonExeSuffix = "" if platform.system().lower() == "windows" else f"{sys.version_info.major}.{sys.version_info.minor}"
        self.assertOutputStreams(
            command=command.format(
                level=usdex.core.DiagnosticsLevel.eStatus,
                body=inspect.cleandoc(
                    """
                    Tf.Status("This is a succinct status", verbose=False)
                    """
                ),
            ),
            expectedStdout=[],
            expectedStderr=[
                "[Status] This is a succinct status",  # usdex formatting
                f"Status: This is a succinct status [python{pythonExeSuffix}]",  # default formatting
                "[Status] This is a succinct status",  # usdex formatting
            ],
        )

    def testLevel(self):
        command = inspect.cleandoc(
            """
            import usdex.core
            from pxr import Tf, Usd

            usdex.core.activateDiagnosticsDelegate()
            assert usdex.core.isDiagnosticsDelegateActive()

            usdex.core.setDiagnosticsLevel(usdex.core.{level})
            assert usdex.core.getDiagnosticsLevel() == usdex.core.{level}

            def emitDiagnostics():
                Tf.Status("This is a status")
                Tf.Warn("This is a warning")
                usdex.core.defineXform(Usd.Stage.CreateInMemory(), "/")  # emits Tf Runtime Error

            emitDiagnostics()
            """
        )

        # eStatus emits all diagnostics
        self.assertOutputStreams(
            command=command.format(level=usdex.core.DiagnosticsLevel.eStatus),
            expectedStdout=[],
            expectedStderr=[
                "[Status] [__main__.emitDiagnostics] This is a status",
                "[Warning] [__main__.emitDiagnostics] This is a warning",
                '[Runtime Error] [usdex::core::defineXform] Unable to define UsdGeomXform due to an invalid location: "/" is not a valid absolute prim path.',
            ],
        )

        # eWarning filters out status diagnostics
        self.assertOutputStreams(
            command=command.format(level=usdex.core.DiagnosticsLevel.eWarning),
            expectedStdout=[],
            expectedStderr=[
                "[Warning] [__main__.emitDiagnostics] This is a warning",
                '[Runtime Error] [usdex::core::defineXform] Unable to define UsdGeomXform due to an invalid location: "/" is not a valid absolute prim path.',
            ],
        )

        # eError filters out status & warning diagnostics
        self.assertOutputStreams(
            command=command.format(level=usdex.core.DiagnosticsLevel.eError),
            expectedStdout=[],
            expectedStderr=[
                '[Runtime Error] [usdex::core::defineXform] Unable to define UsdGeomXform due to an invalid location: "/" is not a valid absolute prim path.',
            ],
        )

        # eFatal filters out status, warning, and error diagnostics
        self.assertOutputStreams(
            command=command.format(level=usdex.core.DiagnosticsLevel.eFatal),
            expectedStdout=[],
            expectedStderr=[],
        )

    def testOutputStream(self):
        command = inspect.cleandoc(
            """
            import usdex.core
            from pxr import Tf, Usd

            usdex.core.activateDiagnosticsDelegate()
            assert usdex.core.isDiagnosticsDelegateActive()

            usdex.core.setDiagnosticsOutputStream(usdex.core.{stream})
            assert usdex.core.getDiagnosticsOutputStream() == usdex.core.{stream}

            def emitDiagnostics():
                Tf.Warn("This is a warning")

            emitDiagnostics()
            """
        )

        self.assertOutputStreams(
            command=command.format(stream=usdex.core.DiagnosticsOutputStream.eStdout),
            expectedStdout=["[Warning] [__main__.emitDiagnostics] This is a warning"],
            expectedStderr=[],
        )

        self.assertOutputStreams(
            command=command.format(stream=usdex.core.DiagnosticsOutputStream.eStderr),
            expectedStdout=[],
            expectedStderr=["[Warning] [__main__.emitDiagnostics] This is a warning"],
        )

        self.assertOutputStreams(
            command=command.format(stream=usdex.core.DiagnosticsOutputStream.eNone),
            expectedStdout=[],
            expectedStderr=[],
        )

    def testUtf8Diagnostics(self):
        self.assertOutputStreams(
            command=inspect.cleandoc(
                """
                import usdex.core
                from pxr import Tf

                def emitDiagnostics():
                    Tf.Warn("カーテンウォール")
                    Tf.Warn("Bäcker")
                    Tf.Warn("😸")

                usdex.core.activateDiagnosticsDelegate()
                emitDiagnostics()
                """
            ),
            expectedStdout=[],
            expectedStderr=[
                "[Warning] [__main__.emitDiagnostics] カーテンウォール",
                "[Warning] [__main__.emitDiagnostics] Bäcker",
                "[Warning] [__main__.emitDiagnostics] 😸",
            ],
        )

    def testFatal(self):
        command = inspect.cleandoc(
            """
            import usdex.core
            from pxr import Tf
            usdex.core.activateDiagnosticsDelegate()
            assert usdex.core.isDiagnosticsDelegateActive()

            def emitDiagnostics():
                Tf.Fatal("Will cause the process to Abort in modern USD versions")
                Tf.Warn("Will only be emitted in older USD versions")

            emitDiagnostics()
            """
        )

        if self.isUsdOlderThan("0.23.11"):
            # Fatal Error diagnostics do not cause the subprocess to abort
            expectSuccess = True
            expectedStderr = [
                "[Fatal] [__main__.emitDiagnostics] Python Fatal Error: Will cause the process to Abort in modern USD versions",
                "[Warning] [__main__.emitDiagnostics] Will only be emitted in older USD versions",
            ]
        else:
            # Fatal Error diagnostics cause the subprocess to abort
            expectSuccess = False
            expectedStderr = [
                "[Fatal] [__main__.emitDiagnostics] Python Fatal Error: Will cause the process to Abort in modern USD versions",
            ]

        self.assertOutputStreams(
            command=command,
            expectedStdout=[],
            expectedStderr=expectedStderr,
            expectSuccess=expectSuccess,
        )
