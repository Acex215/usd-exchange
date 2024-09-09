# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

__all__ = [
    "ScopedDiagnosticChecker",
]

import re
from typing import List, Tuple

import usdex.core
from pxr import Tf, UsdUtils


class ScopedDiagnosticChecker:
    """A context manager to capture and assert expected `Tf.Diagnostics` and `Tf.ErrorMarks`

    Construct a `ScopedDiagnosticChecker` with a `unittest.TestCase` instance and a list of expected diagnostic messages.

    Each `Tuple` must contain:

        - One `Tf.DiagnosticType` (e.g `Tf.TF_DIAGNOSTIC_STATUS_TYPE`)
        - A regex pattern matching the expected diagnostic commentary (message)

    On context exit, the `ScopedDiagnosticChecker` will assert that all expected `Tf.Diagnostics` and `Tf.ErrorMarks` were emmitted.

    Note:

        Any `Tf.ErrorMarks` will be diagnosed before any general `Tf.Diagnostics`. The supplied list of expected values should account for this.

    Example:

        .. code-block:: python

            import unittest

            import usdex.test
            from pxr import Tf

            class MyTestCase(unittest.TestCase):
                def testDiagnostics(self):
                    with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*foo")]):
                        Tf.Warn("This message ends in foo")
    """

    def __init__(self, testCase, expected: List[Tuple[Tf.DiagnosticType, str]]) -> None:
        self.testCase = testCase
        self.expected = expected
        self.__originalOutputStream = usdex.core.getDiagnosticsOutputStream() if usdex.core.isDiagnosticsDelegateActive() else False

    def __enter__(self):
        self.errorMark = Tf.Error.Mark()
        self.delegate = UsdUtils.CoalescingDiagnosticDelegate()
        if usdex.core.isDiagnosticsDelegateActive():
            usdex.core.setDiagnosticsOutputStream(usdex.core.DiagnosticsOutputStream.eNone)

    def __exit__(self, exc_type, exc_val, exc_tb):
        diagnostics = self.delegate.TakeUncoalescedDiagnostics()

        if len(self.expected) == 0:
            self.testCase.assertTrue(self.errorMark.IsClean() and len(diagnostics) == 0)
        else:
            self.testCase.assertTrue(
                len(diagnostics) == len(self.expected) or not self.errorMark.IsClean(),
                msg="""
Errors:
{errors}

Diagnostics:
{diagnostics}

Expected:
{expected}
                """.format(
                    errors="\n".join([x.commentary for x in self.errorMark.GetErrors()]),
                    diagnostics="\n".join([x.commentary for x in diagnostics]),
                    expected="\n".join([x[1] for x in self.expected]),
                ),
            )

        i = 0
        for error in self.errorMark.GetErrors():
            self.testCase.assertTrue(i < len(self.expected))
            if i >= len(self.expected):
                return
            self.testCase.assertEqual(error.errorCode, self.expected[i][0])
            pattern = f"{self.expected[i][1]}"
            self.testCase.assertTrue(
                re.match(pattern, error.commentary),
                msg=f"""
                Pattern: {pattern}
                Commentary: {error.commentary}
                """,
            )
            i += 1

        for diagnostic in diagnostics:
            self.testCase.assertTrue(i < len(self.expected))
            if i >= len(self.expected):
                return
            self.testCase.assertEqual(diagnostic.diagnosticCode, self.expected[i][0])
            pattern = f"{self.expected[i][1]}"
            self.testCase.assertTrue(
                re.match(pattern, diagnostic.commentary),
                msg=f"""
                Pattern: {pattern}
                Commentary: {diagnostic.commentary}
                """,
            )
            i += 1

        self.testCase.assertEqual(i, len(self.expected))

        self.errorMark.Clear()

        if usdex.core.isDiagnosticsDelegateActive():
            usdex.core.setDiagnosticsOutputStream(self.__originalOutputStream)
