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

//! @file usdex/core/NameAlgo.h
//! @brief Utilities for manipulating UsdPrim objects

#include "Api.h"

#include <pxr/base/tf/token.h>
#include <pxr/usd/usd/prim.h>

#include <string>
#include <vector>


namespace usdex::core
{

//! @defgroup prim_name UsdPrim Name Functions
//!
//! Utility functions to generate valid names for `UsdPrims`
//!
//! See [Valid and Unique Names](../docs/authoring-usd.html#valid-and-unique-names) for details.
//!
//! @{

//! Produce a valid prim name from the input name
//!
//! This is a lossless encoding algorithm that supports all UTF-8 code set (even control characters).
//!
//! @param name The input name
//! @returns A string that is considered valid for use as a prim name.
USDEX_API std::string getValidPrimName(const std::string& name);

//! Take a vector of the preferred names and return a matching vector of valid and unique names.
//!
//! @param names A vector of preferred prim names.
//! @param reservedNames A vector of reserved prim names. Names in the vector will not be included in the returns.
//! @returns A vector of valid and unique names.
USDEX_API pxr::TfTokenVector getValidPrimNames(const std::vector<std::string>& names, const pxr::TfTokenVector& reservedNames = {});

//! Take a prim and a vector of the preferred names. Return a matching vector of valid and unique names as the child names of the given prim.
//!
//! @param prim The USD prim where the given prim names should live under.
//! @param names A vector of preferred prim names.
//! @returns A vector of valid and unique names.
USDEX_API pxr::TfTokenVector getValidChildNames(const pxr::UsdPrim& prim, const std::vector<std::string>& names);

//! A caching mechanism for valid and unique child prim names.
//!
//! For best performance, this object should be reused for multiple name requests.
//!
//! It is not valid to request child names from prims from multiple stages as only the prim path is used as the cache key.
//!
//! @warning This class does not automatically invalidate cached values based on changes to the stage from which values were cached.
//! Additionally, a separate instance of this class should be used per-thread, calling methods from multiple threads is not safe.
class USDEX_API ValidChildNameCache
{

public:

    ValidChildNameCache();
    ~ValidChildNameCache();

    //! Take a prim and a vector of the preferred names. Return a matching vector of valid and unique names as the child names of the given prim.
    //!
    //! @param prim The USD prim where the given prim names should live under.
    //! @param names A vector of preferred prim names.
    //! @returns A vector of valid and unique names.
    pxr::TfTokenVector getValidChildNames(const pxr::UsdPrim& prim, const std::vector<std::string>& names);

    //! Take a prim and a preferred name. Return a valid and unique name for use as the child name of the given prim.
    //!
    //! @param prim The prim that the child name should be valid for.
    //! @param name Preferred prim name.
    //! @returns Valid and unique name.
    pxr::TfToken getValidChildName(const pxr::UsdPrim& prim, const std::string& name);

    //! Update the name cache for a Prim to include all existing children.
    //!
    //! This does not clear the cache, so any names that have been previously returned will still be reserved.
    //!
    //! @param prim The prim that child names should be updated for.
    void update(const pxr::UsdPrim& prim);

    //! Clear the name cache for a Prim.
    //!
    //! @param prim The prim that child names should be cleared for.
    void clear(const pxr::UsdPrim& prim);

private:

    class CacheImpl;
    CacheImpl* m_impl;
};

//! @}

//! @defgroup property_name UsdProperty Name Functions
//!
//! Utility functions to generate valid names for properties of a `UsdPrim`
//!
//! See [Valid and Unique Names](../docs/authoring-usd.html#valid-and-unique-names) for details.
//!
//! @{

//! Produce a valid property name using the Bootstring algorithm.
//!
//! @param name The input name
//! @returns A string that is considered valid for use as a property name.
USDEX_API std::string getValidPropertyName(const std::string& name);

//! Take a vector of the preferred names and return a matching vector of valid and unique names.
//!
//! @param names A vector of preferred property names.
//! @param reservedNames A vector of reserved property names. Names in the vector will not be included in the return.
//! @returns A vector of valid and unique names.
USDEX_API pxr::TfTokenVector getValidPropertyNames(const std::vector<std::string>& names, const pxr::TfTokenVector& reservedNames = {});

//! @}

//! @defgroup prim_displayname UsdPrim Display Name Functions
//!
//! Utility functions for interacting with the display name metadata of `UsdPrims`
//! @{

//! Return this prim's display name (metadata)
//!
//! @param prim The prim to get the display name from
//! @returns Authored value, or an empty string if no display name has been set
USDEX_API std::string getDisplayName(const pxr::UsdPrim& prim);

//! Sets this prim's display name (metadata).
//!
//! DisplayName is meant to be a descriptive label, not necessarily an alternate identifier; therefore there is no restriction on which characters can
//! appear in it
//!
//! @param prim The prim to set the display name for
//! @param name The value to set
//! @returns True on success, otherwise false
USDEX_API bool setDisplayName(pxr::UsdPrim prim, const std::string& name);

//! Clears this prim's display name (metadata) in the current EditTarget (only)
//!
//! @param prim The prim to clear the display name for
//! @returns True on success, otherwise false
USDEX_API bool clearDisplayName(pxr::UsdPrim prim);

//! Block this prim's display name (metadata)
//!
//! The fallback value will be explicitly authored to cause the value to resolve as if there were no authored value opinions in weaker layers
//!
//! @param prim The prim to block the display name for
//! @returns True on success, otherwise false
USDEX_API bool blockDisplayName(pxr::UsdPrim prim);

//! Calculate the effective display name of this prim
//!
//! If the display name is un-authored or empty then the prim's name is returned
//!
//! @param prim The prim to compute the display name for
//! @returns The effective display name
USDEX_API std::string computeEffectiveDisplayName(const pxr::UsdPrim& prim);

//! @}

} // namespace usdex::core
