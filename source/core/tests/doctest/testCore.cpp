// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <usdex/core/Core.h>
#include <usdex/core/Feature.h>
#include <usdex/core/Version.h>

#include <doctest/doctest.h>

#include <string>

TEST_CASE("Version and Features")
{
    CHECK(std::string(usdex::core::version()) == USDEX_BUILD_STRING);
    CHECK(usdex::core::withPython() == USDEX_WITH_PYTHON);
}
