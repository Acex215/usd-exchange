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

//! @file usdex/core/Api.h
//! @brief Symbol macros for this library

#include "Feature.h"

#ifdef __cplusplus
//! Declares a "C" exported external symbol.  This uses the "C" name decoration style of
//! adding an underscore to the start of the exported name.
#define USDEX_EXTERN_C extern "C"
#else
#define USDEX_EXTERN_C
#endif

#if defined(_WIN32)
//! This import tag will be used when including this header in other libraries.
//! See usdex_core_EXPORTS below.
#define USDEX_IMPORT __declspec(dllimport)
//! This export tag should only be used when tagging exported symbols from within usdex_core itself.
//! See usdex_core_EXPORTS below.
#define USDEX_EXPORT __declspec(dllexport)
#else
//! This import tag will be used when including this header in other libraries.
//! See usdex_core_EXPORTS below.
#define USDEX_IMPORT
//! This export tag should only be used when tagging exported symbols from within usdex_core itself.
//! See usdex_core_EXPORTS below.
#define USDEX_EXPORT __attribute__((visibility("default")))
#endif

//! Deprecate C++ API with an extra versioned message appended
//!
//! @param version: The major.minor version in which the function was first deprecated
//! @param message: A user facing message about the deprecation, ideally with a suggested alternative function.
//!     Do not include the version in this message, it will be appended automatically.
#define USDEX_DEPRECATED(version, message) [[deprecated(message ". It was deprecated in v" version " and will be removed in the future.")]]

//! Define USDEX_API macro based on whether or not we are compiling usdex_core,
//! or including headers for linking to it. Functions that wish to be exported from a .dll/.so
//! should be decorated with USDEX_API.
#ifdef usdex_core_EXPORTS
#define USDEX_API USDEX_EXPORT
#else
#define USDEX_API USDEX_IMPORT
#endif
