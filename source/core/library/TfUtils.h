// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <string>

namespace usdex::core::detail
{

//! Produce a valid identifier from `in` by replacing invalid characters with "_".
//!
//! This function differs from pxr::TfMakeValidIdentifier in how it handles numeric characters at the start of the value.
//! Rather than replacing the character with an "_" this function will add an "_" prefix.
//!
//! @param in The input value
//! @returns A string that is considered valid for use as an identifier.
std::string makeValidIdentifier(const std::string& in);

} // namespace usdex::core::detail
