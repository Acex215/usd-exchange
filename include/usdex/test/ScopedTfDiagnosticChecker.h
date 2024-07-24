// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

//! @file usdex/test/ScopedTfDiagnosticChecker.h
//! @brief A scoped class to capture and assert expected `TfDiagnostics` and `TfErrorMarks` for use in a `doctest` suite.

#include <pxr/base/tf/diagnosticMgr.h>
#include <pxr/base/tf/enum.h>
#include <pxr/base/tf/errorMark.h>
#include <pxr/usd/usdUtils/coalescingDiagnosticDelegate.h>

#include <fmt/format.h>

#include <doctest/doctest.h>

#include <regex>

//! @brief The namespace for the OpenUSD Exchange SDK doctest based Testing Library.
namespace usdex::test
{

//! @defgroup doctest Utilities for testing USD authoring within doctest test suites.
//!
//! In C++ `usdex::test` uses the <a href="https://github.com/doctest/doctest">doctest</a> testing framework. The utility classes and functions
//! within this group use doctest commands in their implementations directly and as such are expected to be used within a running doctest
//! context.
//!
//! @{

//! A scoped class to capture and assert expected `TfDiagnostics` and `TfErrorMarks` for use in a `doctest` suite.
//!
//! Construct a `ScopedTfDiagnosticChecker` and a list of expected diagnostic messages.
//!
//! Each `DiagnosticPattern` must contain:
//!     - One `TfDiagnosticType` (e.g `TF_DIAGNOSTIC_STATUS_TYPE`)
//!     - A regex pattern matching the expected diagnostic commentary (message)
//!
//! On context exit, the `ScopedTfDiagnosticChecker` will assert that all expected `TfDiagnostics` and `TfErrorMarks` were emmitted.
//!
//! @note `TfErrorMarks` will be diagnosed before any general `TfDiagnostics`. The supplied list of expected values should account for this.
//!
//! Example:
//!
//!     #include <usdex/test/ScopedTfDiagnosticChecker.h>
//!     #include <pxr/base/tf/diagnostic.h>
//!
//!     #define DOCTEST_CONFIG_IMPLEMENTATION_IN_DLL
//!     #include <doctest/doctest.h>
//!
//!     using namespace pxr;
//!
//!     TEST_CASE("My Test Case")
//!     {
//!         {
//!             usdex::test::ScopedTfDiagnosticChecker check({ { TF_DIAGNOSTIC_WARNING_TYPE, ".*foo" } });
//!             TF_WARN("This message ends in foo");
//!         }
//!     }
class ScopedTfDiagnosticChecker
{

public:

    //! A vector of expected `TfDiagnosticTypes` and `std::regex` compliant match patterns.
    using DiagnosticPatterns = std::vector<std::pair<pxr::TfEnum, std::string>>;

    //! Construct a default `ScopedTfDiagnosticChecker` to assert that no `TfDiagnostics` or `TfErrorMarks` are emitted.
    ScopedTfDiagnosticChecker() = default;

    //! Construct a `ScopedTfDiagnosticChecker` with a vector of expected `DiagnosticPattern` pairs.
    ScopedTfDiagnosticChecker(DiagnosticPatterns expected) : m_expected{ std::move(expected) } {};

    //! On destruction the `ScopedTfDiagnosticChecker` will assert the expected `TfDiagnostics` and `TfErrorMarks` were emitted using doctest `CHECK`
    ~ScopedTfDiagnosticChecker()
    {
        auto diagnostics = m_delegate.TakeUncoalescedDiagnostics();

        if (m_expected.empty())
        {
            CHECK(m_errors.IsClean());
            CHECK(diagnostics.size() == 0);
        }
        else if (diagnostics.size() != m_expected.size())
        {
            CHECK(!m_errors.IsClean());
        }

        size_t i = 0;
        for (const pxr::TfError& error : m_errors)
        {
            CHECK(i < m_expected.size());
            if (i >= m_expected.size())
            {
                return;
            }
            CHECK(error.GetErrorCode() == m_expected[i].first);
            CHECK_MESSAGE(
                std::regex_match(error.GetCommentary(), std::regex(m_expected[i].second)),
                fmt::format("\n\tPattern: {0}\n\tCommentary: {1}", m_expected[i].second, error.GetCommentary())
            );
            ++i;
        }

        for (auto& diagnostic : diagnostics)
        {
            CHECK(i < m_expected.size());
            if (i >= m_expected.size())
            {
                return;
            }
            CHECK(diagnostic->GetDiagnosticCode() == m_expected[i].first);
            CHECK_MESSAGE(
                std::regex_match(diagnostic->GetCommentary(), std::regex(m_expected[i].second)),
                fmt::format("\n\tPattern: {0}\n\tCommentary: {1}", m_expected[i].second, diagnostic->GetCommentary())
            );
            ++i;
        }

        // ensure we have found all expected diagnostics
        CHECK(i == m_expected.size());

        // dismiss the errors so they don't propagate to stderr
        m_errors.Clear();
    };

private:

    pxr::TfErrorMark m_errors;
    pxr::UsdUtilsCoalescingDiagnosticDelegate m_delegate;
    DiagnosticPatterns m_expected;
};

//! @}

} // namespace usdex::test
