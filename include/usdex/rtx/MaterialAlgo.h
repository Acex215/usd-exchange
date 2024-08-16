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

#include "usdex/rtx/Api.h"

#include <pxr/base/gf/vec3f.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdShade/shader.h>

#include <optional>

//! @file usdex/rtx/MaterialAlgo.h
//! @brief Material and Shader Utilities

namespace usdex::rtx
{

//! @defgroup materials Usd Material and Usd Shader Utilities
//!
//! Utility functions for creating, editing, and querying UsdShadeMaterial and UsdShadeShader objects
//!
//! @{

//! Texture color space (encoding) types
// clang-format off
enum class ColorSpace
{
    eAuto, //!< Check for gamma or metadata in the texture itself
    eRaw,  //!< Use linear sampling (used for Normal, Roughness, Metallic, Opacity textures)
    eSrgb, //!< Use sRGB sampling (typically used for Diffuse textures)
};
// clang-format on


//! Translate an sRGB color value to linear color space
//!
//! - Many 3D modeling applications define colors in RGB (0-255) or sRGB (0-1) color space
//! - MDL uses a linear color space that aligns with how light and color behave in the natural world
//! - Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is out of the scope of this module
//!
//! @param color sRGB representation of a color to be translated to linear color space
//! @returns The translated color in linear color space
USDEX_RTX_API pxr::GfVec3f sRgbToLinear(const pxr::GfVec3f& color);

//! Translate a linear color value to sRGB color space
//!
//! - Many 3D modeling applications define colors in RGB (0-255) or sRGB (0-1) color space
//! - MDL uses a linear color space that aligns with how light and color behave in the natural world
//! - Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is out of the scope of this module
//!
//! @param color linear representation of a color to be translated to sRGB color space
//! @returns The color in sRGB color space
USDEX_RTX_API pxr::GfVec3f linearToSrgb(const pxr::GfVec3f& color);

//! Create a UsdShadeMaterial as a child of the UsdPrim argument
//!
//! @param parent Parent UsdPrim for the material to be created
//! @param name Name of the material to be created
//! @returns The newly created UsdShadeMaterial.  Returns an Invalid prim on error.
USDEX_RTX_API pxr::UsdShadeMaterial createMaterial(pxr::UsdPrim parent, const std::string& name);

//! Create a UsdShadeShader as a child of the UsdShadeMaterial argument with the specified MDL
//!
//! @param material Parent UsdShadeMaterial for the shader to be created
//! @param name Name of the shader to be created
//! @param mdlPath Absolute or relative path to the MDL asset
//! @param module Name of the MDL module to set as source asset sub-identifier for the shader
//! @param connectMaterialOutputs If true, creates surface, displacement and volume outputs on the material and connects them to the shader output
//! @returns The newly created UsdShadeShader.  Returns an Invalid prim on error.
USDEX_RTX_API pxr::UsdShadeShader createMdlShader(
    pxr::UsdShadeMaterial& material,
    const std::string& name,
    const pxr::SdfAssetPath& mdlPath,
    const pxr::TfToken& module,
    bool connectMaterialOutputs = true
);

//! Create an MDL shader input
//!
//! If the shader input already exists and is a different type, defined in the current edit target layer -> it will be removed and recreated.
//!
//! If the shader input already exists and has a connected source -> the source will be disconnected before being set.
//!
//! @note When creating texture asset inputs (diffuse, normal, roughness, etc.) it is important to set the colorSpace parameter so that
//!       the textures are sampled correctly.  Typically, diffuse is "auto", which resolves to "sRGB".  Normal, roughness, and other textures
//!       should be "raw".
//!
//! @param material The UsdShadeMaterial prim that contains the MDL shader
//! @param name Name of the input to be created
//! @param value The value assigned to the input
//! @param typeName The value type of the input
//! @param colorSpace If set, the newly created input's colorSpace attribute
//! @returns The newly created UsdShadeInput input.  Returns an Invalid UsdShadeInput on error.
USDEX_RTX_API pxr::UsdShadeInput createMdlShaderInput(
    pxr::UsdShadeMaterial& material,
    const pxr::TfToken& name,
    const pxr::VtValue& value,
    const pxr::SdfValueTypeName& typeName,
    std::optional<const ColorSpace> colorSpace = std::nullopt
);

//! Binds a UsdShadeMaterial to a UsdPrim
//!
//! @param prim UsdPrim to bind the material to
//! @param material UsdShadeMaterial to bind to the prim
USDEX_RTX_API void bindMaterial(pxr::UsdPrim prim, const pxr::UsdShadeMaterial& material);

//! Get the effective surface Shader of a Material for the MDL render context.
//!
//! @param material The Material to consider
//! @returns The connected Shader. Returns an invalid object on error.
USDEX_RTX_API pxr::UsdShadeShader computeEffectiveMdlSurfaceShader(const pxr::UsdShadeMaterial& material);

//! Get the effective surface Shader of a Material for the universal render context.
//!
//! @param material The Material to consider
//! @returns The connected Shader. Returns an invalid object on error.
USDEX_RTX_API pxr::UsdShadeShader computeEffectivePreviewSurfaceShader(const pxr::UsdShadeMaterial& material);

//! Defines an OmniPBR UsdShadeMaterial interface that drives both an RTX render context and a UsdPreviewSurface context
//!
//! MDL and UsdPreviewSurface use a linear color space, please convert RGB and sRGB values to linear
//!
//! Note: The use of MDL shaders inside this Material interface is considered an implementation detail of the RTX Renderer.
//! Once the RTX Renderer supports OpenPBR or MaterialX shaders we may change the implementation to author those shaders instead of MDL.
//!
//! @param stage The stage on which to define the Material
//! @param path The absolute prim path at which to define the Material
//! @param color The diffuse color of the Material
//! @param opacity The Opacity Amount to set. When less than 1.0, Enable Opacity is set to true and Fractional Opacity is enabled in the RT renderer
//! @param roughness The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
//! @param metallic The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic
//! @returns The newly defined UsdShadeMaterial. Returns an Invalid prim on error
USDEX_RTX_API pxr::UsdShadeMaterial defineOmniPbrMaterial(
    pxr::UsdStagePtr stage,
    const pxr::SdfPath& path,
    const pxr::GfVec3f& color,
    const float opacity = 1.0f,
    const float roughness = 0.5f,
    const float metallic = 0.0f
);

//! Defines an OmniPBR UsdShadeMaterial interface that drives both an RTX render context and a UsdPreviewSurface context
//!
//! MDL and UsdPreviewSurface use a linear color space, please convert RGB and sRGB values to linear
//!
//! Note: The use of MDL shaders inside this Material interface is considered an implementation detail of the RTX Renderer.
//! Once the RTX Renderer supports OpenPBR or MaterialX shaders we may change the implementation to author those shaders instead of MDL.
//!
//! @param parent Prim below which to define the Material
//! @param name Name of the Material
//! @param color The diffuse color of the Material
//! @param opacity The Opacity Amount to set. When less than 1.0, Enable Opacity is set to true and Fractional Opacity is enabled in the RT renderer
//! @param roughness The Roughness Amount to set, 0.0-1.0 range where 1.0 = flat and 0.0 = glossy
//! @param metallic The Metallic Amount to set, 0.0-1.0 range where 1.0 = max metallic and 0.0 = no metallic
//! @returns The newly defined UsdShadeMaterial. Returns an Invalid prim on error
USDEX_RTX_API pxr::UsdShadeMaterial defineOmniPbrMaterial(
    pxr::UsdPrim parent,
    const std::string& name,
    const pxr::GfVec3f& color,
    const float opacity = 1.0f,
    const float roughness = 0.5f,
    const float metallic = 0.0f
);

//! Adds a diffuse texture to the PBR material
//!
//! It is expected that the material was created by the USDEX defineOmniPbrMaterial() function.
//!
//! @note The material prim's "Color" input will be removed and replaced with "DiffuseTexture".
//!       Due to the input removal this function should be used at initial authoring time rather than in a stronger layer.
//!
//! @param material The UsdShadeMaterial prim to add the texture
//! @param texturePath The SdfAssetPath to the texture file
//! @returns Whether or not the texture was added to the material
USDEX_RTX_API bool addDiffuseTextureToPbrMaterial(pxr::UsdShadeMaterial& material, const pxr::SdfAssetPath& texturePath);

//! Adds a normal texture to the PBR material
//!
//! It is expected that the material was created by the USDEX defineOmniPbrMaterial() function.
//!
//! @param material The UsdShadeMaterial prim to add the texture
//! @param texturePath The SdfAssetPath to the texture file
//! @returns Whether or not the texture was added to the material
USDEX_RTX_API bool addNormalTextureToPbrMaterial(pxr::UsdShadeMaterial& material, const pxr::SdfAssetPath& texturePath);

//! Adds an ORM (occlusion, roughness, metallic) texture to the PBR material
//!
//! It is expected that the material was created by the USDEX defineOmniPbrMaterial() function.
//!
//! @note The material prim's "Roughness" and "Metallic" inputs will be removed and replaced with "ORMTexture".
//!       Due to the input removal this function should be used at initial authoring time rather than in a stronger layer.
//!
//! @param material The UsdShadeMaterial prim to add the texture
//! @param texturePath The SdfAssetPath to the texture file
//! @returns Whether or not the texture was added to the material
USDEX_RTX_API bool addOrmTextureToPbrMaterial(pxr::UsdShadeMaterial& material, const pxr::SdfAssetPath& texturePath);

//! Adds a roughness texture to the PBR material
//!
//! It is expected that the material was created by the USDEX defineOmniPbrMaterial() function.
//!
//! @note The material prim's "Roughness" input will be removed and replaced with "RoughnessTexture".
//!       Due to the input removal this function should be used at initial authoring time rather than in a stronger layer.
//!
//! @param material The UsdShadeMaterial prim to add the texture
//! @param texturePath The SdfAssetPath to the texture file
//! @returns Whether or not the texture was added to the material
USDEX_RTX_API bool addRoughnessTextureToPbrMaterial(pxr::UsdShadeMaterial& material, const pxr::SdfAssetPath& texturePath);

//! Adds a metallic texture to the PBR material
//!
//! It is expected that the material was created by the USDEX defineOmniPbrMaterial() function.
//!
//! @note The material prim's "Metallic" input will be removed and replaced with "MetallicTexture".
//!       Due to the input removal this function should be used at initial authoring time rather than in a stronger layer.
//!
//! @param material The UsdShadeMaterial prim to add the texture
//! @param texturePath The SdfAssetPath to the texture file
//! @returns Whether or not the texture was added to the material
USDEX_RTX_API bool addMetallicTextureToPbrMaterial(pxr::UsdShadeMaterial& material, const pxr::SdfAssetPath& texturePath);

//! Adds an opacity texture to the PBR material
//!
//! It is expected that the material was created by the USDEX defineOmniPbrMaterial() function.
//!
//! @note The material prim's "Opacity" input will be removed and replaced with "OpacityTexture".
//!       Due to the input removal this function should be used at initial authoring time rather than in a stronger layer.
//!
//! These shader parameters will be set to produce better masked geometry:
//! - MDL OmniPBR: `opacity_threshold = float_epsilon` (just greater than zero)
//! - UsdPreviewSurface: `ior = 1.0`
//! - UsdPreviewSurface: `opacityThreshold = float_epsilon` (just greater than zero)
//!
//! @param material The UsdShadeMaterial prim to add the texture
//! @param texturePath The SdfAssetPath to the texture file
//! @returns Whether or not the texture was added to the material
USDEX_RTX_API bool addOpacityTextureToPbrMaterial(pxr::UsdShadeMaterial& material, const pxr::SdfAssetPath& texturePath);

//! Defines an OmniGlass UsdShadeMaterial interface that drives both an RTX render context and a UsdPreviewSurface context
//!
//! MDL and UsdPreviewSurface use a linear color space, please convert RGB and sRGB values to linear
//!
//! Note: The use of MDL shaders inside this Material interface is considered an implementation detail of the RTX Renderer.
//! Once the RTX Renderer supports OpenPBR or MaterialX shaders we may change the implementation to author those shaders instead of MDL.
//!
//! @param stage The stage on which to define the Material
//! @param path The absolute prim path at which to define the Material
//! @param color The color of the Material
//! @param indexOfRefraction The Index of Refraction to set, 1.0-4.0 range
//! @returns The newly defined UsdShadeMaterial. Returns an Invalid prim on error
USDEX_RTX_API pxr::UsdShadeMaterial defineOmniGlassMaterial(
    pxr::UsdStagePtr stage,
    const pxr::SdfPath& path,
    const pxr::GfVec3f& color,
    const float indexOfRefraction = 1.491f
);

//! Defines an OmniGlass UsdShadeMaterial interface that drives both an RTX render context and a UsdPreviewSurface context
//!
//! MDL and UsdPreviewSurface use a linear color space, please convert RGB and sRGB values to linear
//!
//! Note: The use of MDL shaders inside this Material interface is considered an implementation detail of the RTX Renderer.
//! Once the RTX Renderer supports OpenPBR or MaterialX shaders we may change the implementation to author those shaders instead of MDL.
//!
//! @param parent Prim below which to define the Material
//! @param name Name of the Material
//! @param color The color of the Material
//! @param indexOfRefraction The Index of Refraction to set, 1.0-4.0 range
//! @returns The newly defined UsdShadeMaterial. Returns an Invalid prim on error
USDEX_RTX_API pxr::UsdShadeMaterial defineOmniGlassMaterial(
    pxr::UsdPrim parent,
    const std::string& name,
    const pxr::GfVec3f& color,
    const float indexOfRefraction = 1.491f
);

//! @}

} // namespace usdex::rtx
