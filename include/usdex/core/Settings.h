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

//! @file usdex/core/Settings.h
//! @brief Global static runtime settings

#include "usdex/core/Api.h"

#include <pxr/base/tf/envSetting.h>

namespace usdex::core
{

//! @defgroup settings Runtime Settings
//!
//! Some OpenUSD Exchange behaviors are controllable via global static runtime settings, using
//! OpenUSD's [TfEnvSetting](https://openusd.org/release/api/env_setting_8h.html#details) mechanism.
//!
//! To change the value of any setting from its default, you must set the associated environment variable before loading `usdex_core` or
//! any OpenUSD module (e.g. `tf`). The environment variable for any setting exactly matches the c++ variable name (without any explicit namespace).
//!
//! Alternatively, a single environment variable `PIXAR_TF_ENV_SETTING_FILE` can be used to supply a file containing key=value lines, where each
//! key is a `TfEnvSetting` variable name and each value is in the expected range for that `TfEnvSetting`.
//!
//! @{

//! Set the `USDEX_ENABLE_OMNI_TRANSCODING` environment variable to enable/disable the use of `omni_transcoding` within `getValidPrimName(s)`,
//! `getValidChildName(s)`, and `getValidPropertyName(s)`. Defaults `true` (transcoding is enabled).
//!
//! See [Valid and Unique Names](../docs/authoring-usd.html#valid-and-unique-names) for details.
USDEX_API extern pxr::TfEnvSetting<bool> USDEX_ENABLE_OMNI_TRANSCODING;

//! }@

} // namespace usdex::core
