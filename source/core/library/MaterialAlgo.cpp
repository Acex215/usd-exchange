// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/MaterialAlgo.h"

#include "usdex/core/StageAlgo.h"

#include <pxr/usd/usdShade/materialBindingAPI.h>
#include <pxr/usd/usdShade/tokens.h>

using namespace pxr;

namespace
{

float toLinear(float value)
{
    if (value <= 0.04045f)
    {
        return value / 12.92f;
    }
    else
    {
        float adjusted = (value + 0.055f) / 1.055f;
        return std::pow(adjusted, 2.4f);
    }
}

float fromLinear(float value)
{
    float test = value * 12.92f;
    if (test <= 0.04045f)
    {
        return test;
    }
    else
    {
        float scaled = std::pow(value, 1.0f / 2.4f);
        return (scaled * 1.055f) - 0.055f;
    }
}

} // namespace

UsdShadeMaterial usdex::core::createMaterial(UsdPrim parent, const std::string& name)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(parent, name, &reason))
    {
        TF_WARN("Unable to create UsdShadeMaterial due to an invalid location: %s", reason.c_str());
        return UsdShadeMaterial();
    }

    SdfPath materialPath = parent.GetPath().AppendChild(TfToken(name));
    UsdStagePtr stage = parent.GetStage();

    UsdShadeMaterial material = UsdShadeMaterial::Define(stage, materialPath);
    return material;
}

bool usdex::core::bindMaterial(UsdPrim prim, const UsdShadeMaterial& material)
{
    UsdPrim matPrim = material.GetPrim();
    if (!matPrim && !prim)
    {
        TF_WARN(
            "UsdPrim <%s> and UsdShadeMaterial <%s> are not valid, cannot bind material to prim",
            prim.GetPath().GetAsString().c_str(),
            material.GetPath().GetAsString().c_str()
        );
        return false;
    }
    if (!matPrim)
    {
        TF_WARN("UsdShadeMaterial <%s> is not valid, cannot bind material to prim", matPrim.GetPath().GetAsString().c_str());
        return false;
    }
    if (!prim)
    {
        TF_WARN("UsdPrim <%s> is not valid, cannot bind material to prim", prim.GetPath().GetAsString().c_str());
        return false;
    }
    UsdShadeMaterialBindingAPI materialBinding = UsdShadeMaterialBindingAPI::Apply(prim);
    return materialBinding.Bind(material);
}

UsdShadeShader usdex::core::computeEffectivePreviewSurfaceShader(const UsdShadeMaterial& material)
{
    if (!material)
    {
        return UsdShadeShader();
    }

    return material.ComputeSurfaceSource({ UsdShadeTokens->universalRenderContext });
}

GfVec3f usdex::core::sRgbToLinear(const GfVec3f& color)
{
    return GfVec3f(toLinear(color[0]), toLinear(color[1]), toLinear(color[2]));
}

GfVec3f usdex::core::linearToSrgb(const GfVec3f& color)
{
    return GfVec3f(fromLinear(color[0]), fromLinear(color[1]), fromLinear(color[2]));
}
