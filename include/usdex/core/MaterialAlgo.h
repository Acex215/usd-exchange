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

#include "usdex/core/Api.h"

#include <pxr/base/gf/vec3f.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdShade/shader.h>

//! @file usdex/core/MaterialAlgo.h
//! @brief Material and Shader Utilities applicable to all render contexts

namespace usdex::core
{

//! @defgroup materials UsdShade Material and Shader Utilities applicable to all render contexts
//!
//! Utility functions for creating, editing, and querying `UsdShadeMaterial` and `UsdShadeShader` objects, as well as conveniences around authoring
//! [UsdPreviewSurface specification](https://openusd.org/release/spec_usdpreviewsurface.html) compliant shader networks for use with the
//! universal render context.
//!
//! @note UsdPreviewSurface materials should be supported by all renderers, and are generally used as "fallback" shaders when renderer-specific
//! shaders have not been supplied. While typically serving as fallback/previews, they are still relatively advanced PBR materials and may be suitable
//! as final quality materials, depending on your intended target use case for your USD data.
//!
//! @{

//! Create a `UsdShadeMaterial` as a child of the Prim parent
//!
//! @param parent Parent prim of the new material
//! @param name Name of the material to be created
//! @returns The newly created `UsdShadeMaterial`. Returns an invalid material object on error.
USDEX_API pxr::UsdShadeMaterial createMaterial(pxr::UsdPrim parent, const std::string& name);

//! Authors a direct binding to the given material on this prim.
//!
//! Validates both the prim and the material, applies the `UsdShadeMaterialBindingAPI` to the target prim,
//! and binds the material to the target prim.
//!
//! @note The material is bound with the default "all purpose" used for both full and preview rendering, and with the default "fallback strength"
//! meaning descendant prims can override with a different material. If alternate behavior is desired, use the `UsdShadeMaterialBindingAPI` directly.
//!
//! @param prim The prim that the material will affect
//! @param material The material to bind to the prim
//! @returns Whether the material was successfully bound to the target prim.
USDEX_API bool bindMaterial(pxr::UsdPrim prim, const pxr::UsdShadeMaterial& material);

//! Get the effective surface Shader of a Material for the universal render context.
//!
//! @param material The Material to consider
//! @returns The connected Shader. Returns an invalid shader object on error.
USDEX_API pxr::UsdShadeShader computeEffectivePreviewSurfaceShader(const pxr::UsdShadeMaterial& material);

//! Defines a PBR `UsdShadeMaterial` driven by a `UsdPreviewSurface` shader network for the universal render context.
//!
//! The input parameters reflect a subset of the [UsdPreviewSurface specification](https://openusd.org/release/spec_usdpreviewsurface.html) commonly
//! used when authoring materials using the metallic/metalness workflow (as opposed to the specular workflow). Many other inputs are available and
//! can be authored after calling this function (including switching to the specular workflow).
//!
//! @param stage The stage on which to define the Material
//! @param path The absolute prim path at which to define the Material
//! @param color The diffuse color of the Material
//! @param opacity The Opacity Amount to set, 0.0-1.0 range where 1.0 = opaque and 0.0 = invisible
//! @param roughness The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
//! @param metallic The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic
//! @returns The newly defined `UsdShadeMaterial`. Returns an Invalid object on error.
USDEX_API pxr::UsdShadeMaterial definePreviewMaterial(
    pxr::UsdStagePtr stage,
    const pxr::SdfPath& path,
    const pxr::GfVec3f& color,
    const float opacity = 1.0f,
    const float roughness = 0.5f,
    const float metallic = 0.0f
);

//! Defines a PBR `UsdShadeMaterial` driven by a `UsdPreviewSurface` shader network for the universal render context.
//!
//! The input parameters reflect a subset of the [UsdPreviewSurface specification](https://openusd.org/release/spec_usdpreviewsurface.html) commonly
//! used when authoring materials using the metallic/metalness workflow (as opposed to the specular workflow). Many other inputs are available and
//! can be authored after calling this function (including switching to the specular workflow).
//!
//! @param parent Prim below which to define the Material
//! @param name Name of the Material
//! @param color The diffuse color of the Material
//! @param opacity The Opacity Amount to set, 0.0-1.0 range where 1.0 = opaque and 0.0 = invisible
//! @param roughness The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
//! @param metallic The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic
//! @returns The newly defined `UsdShadeMaterial`. Returns an Invalid object on error.
USDEX_API pxr::UsdShadeMaterial definePreviewMaterial(
    pxr::UsdPrim parent,
    const std::string& name,
    const pxr::GfVec3f& color,
    const float opacity = 1.0f,
    const float roughness = 0.5f,
    const float metallic = 0.0f
);

//! Texture color space (encoding) types
// clang-format off
enum class ColorSpace
{
    eAuto, //!< Check for gamma or metadata in the texture itself
    eRaw,  //!< Use linear sampling (typically used for Normal, Roughness, Metallic, Opacity textures, or when using high dynamic range file formats like EXR)
    eSrgb, //!< Use sRGB sampling (typically used for Diffuse textures when using PNG files)
};
// clang-format on

//! Translate an sRGB color value to linear color space
//!
//! Many 3D modeling applications define colors in sRGB (0-1) color space. Many others use a linear color space that aligns with how light and color
//! behave in the natural world. When authoring `UsdShadeShader` color input data, including external texture assets, you may need to translate
//! between color spaces.
//!
//! @note Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is beyond the scope of this
//! module. See this [MathWorks article](https://www.mathworks.com/help/images/understanding-color-spaces-and-color-space-conversion.html) for a
//! relatively brief introduction. If you need more specific color handling please use a dedicated color science library like
//! [OpenColorIO](https://opencolorio.org).
//!
//! @param color sRGB representation of a color to be translated to linear color space
//! @returns The translated color in linear color space
USDEX_API pxr::GfVec3f sRgbToLinear(const pxr::GfVec3f& color);

//! Translate a linear color value to sRGB color space
//!
//! Many 3D modeling applications define colors in sRGB (0-1) color space. Many others use a linear color space that aligns with how light and color
//! behave in the natural world. When authoring `UsdShadeShader` color input data, including external texture assets, you may need to translate
//! between color spaces.
//!
//! @note Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is beyond the scope of this
//! module. See this [MathWorks article](https://www.mathworks.com/help/images/understanding-color-spaces-and-color-space-conversion.html) for a
//! relatively brief introduction. If you need more specific color handling please use a dedicated color science library like
//! [OpenColorIO](https://opencolorio.org).
//!
//! @param color linear representation of a color to be translated to sRGB color space
//! @returns The color in sRGB color space
USDEX_API pxr::GfVec3f linearToSrgb(const pxr::GfVec3f& color);

//! @}

} // namespace usdex::core
