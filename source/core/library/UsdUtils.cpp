// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "UsdUtils.h"

#include <pxr/base/tf/stringUtils.h>
#include <pxr/base/tf/token.h>
#include <pxr/base/vt/value.h>
#include <pxr/usd/sdf/schema.h>


using namespace pxr;

bool usdex::core::detail::isEditablePrimLocation(const UsdStagePtr stage, const SdfPath& path, std::string* reason)
{
    // The stage must be valid
    if (!stage)
    {
        if (reason != nullptr)
        {
            *reason = "Invalid UsdStage.";
        }
        return false;
    }

    // The path must be a valid absolute prim path
    if (!path.IsAbsolutePath() || !path.IsPrimPath())
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf("\"%s\" is not a valid absolute prim path.", path.GetAsString().c_str());
        }
        return false;
    }

    // Any existing prim must not be an instance proxy
    const UsdPrim prim = stage->GetPrimAtPath(path);
    if (prim && prim.IsInstanceProxy())
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf("\"%s\" is an instance proxy, authoring is not allowed.", path.GetAsString().c_str());
        }
        return false;
    }

    return true;
}

bool usdex::core::detail::isEditablePrimLocation(const UsdPrim& prim, const std::string& name, std::string* reason)
{
    // The parent prim must be valid
    // We don't need to check that the UsdStage is valid as it must be if the UsdPrim is valid.
    if (!prim)
    {
        if (reason != nullptr)
        {
            *reason = "Invalid UsdPrim";
        }
        return false;
    }

    // The parent prim must not be an instance proxy
    if (prim.IsInstanceProxy())
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf("\"%s\" is an instance proxy, authoring is not allowed.", prim.GetPath().GetAsString().c_str());
        }
        return false;
    }

    // The name must be a valid identifier
    if (!SdfPath::IsValidIdentifier(name))
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf("\"%s\" is not a valid prim name", name.c_str());
        }
        return false;
    }

    // Any existing prim must not be an instance proxy
    const UsdPrim child = prim.GetChild(TfToken(name));
    if (child && child.IsInstanceProxy())
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf("\"%s\" is an instance proxy, authoring is not allowed.", child.GetPath().GetAsString().c_str());
        }
        return false;
    }

    return true;
}
