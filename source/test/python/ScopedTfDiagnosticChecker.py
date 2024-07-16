# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import List, Tuple

from pxr import Tf, UsdUtils


class ScopedTfDiagnosticChecker:
    """A context manager to capture and assert expected Tf.Diagnostics and Tf.ErrorMarks"""

    def __init__(self, testCase, expected: List[Tuple[Tf.DiagnosticType, str]]) -> None:
        self.testCase = testCase
        self.expected = expected

    def __enter__(self):
        self.errorMark = Tf.Error.Mark()
        self.delegate = UsdUtils.CoalescingDiagnosticDelegate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        diagnostics = self.delegate.TakeUncoalescedDiagnostics()

        if len(self.expected) == 0:
            self.testCase.assertTrue(self.errorMark.IsClean() and len(diagnostics) == 0)
        else:
            self.testCase.assertTrue(len(diagnostics) == len(self.expected) or not self.errorMark.IsClean())

        i = 0
        for error in self.errorMark.GetErrors():
            self.testCase.assertTrue(i < len(self.expected))
            if i >= len(self.expected):
                return
            self.testCase.assertEqual(error.errorCode, self.expected[i][0])
            self.testCase.assertIn(self.expected[i][1], error.commentary)
            i += 1

        for diagnostic in diagnostics:
            self.testCase.assertTrue(i < len(self.expected))
            if i >= len(self.expected):
                return
            self.testCase.assertEqual(diagnostic.diagnosticCode, self.expected[i][0])
            self.testCase.assertIn(self.expected[i][1], diagnostic.commentary)
            i += 1

        self.testCase.assertEqual(i, len(self.expected))

        self.errorMark.Clear()
