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

#include "usdex/core/MaterialAlgo.h"

#include "usdex/pybind/UsdBindings.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace usdex::core;
using namespace pybind11;
using namespace pxr;

namespace usdex::core::bindings
{

void bindMaterialAlgo(module& m)
{
    m.def(
        "createMaterial",
        &createMaterial,
        arg("parent"),
        arg("name"),
        R"(
            Create a ``UsdShade.Material`` as the child of the Prim parent

            Args:
                parent: Parent prim of the material
                name: Name of the material to be created
            Returns:
                The newly created ``UsdShade.Material``. Returns an invalid material object on error.
        )"
    );

    m.def(
        "bindMaterial",
        &bindMaterial,
        arg("prim"),
        arg("material"),
        R"(
            Authors a direct binding to the given material on this prim.

            Validates both the prim and the material, applies the ``UsdShade.MaterialBindingAPI`` to the target prim,
            and binds the material to the target prim.

            Note:
                The material is bound with the default "all purpose" used for both full and preview rendering, and with the default "fallback strength"
                meaning descendant prims can override with a different material. If alternate behavior is desired, use the
                ``UsdShade.MaterialBindingAPI`` directly.

            Args:
                prim: The prim that the material will affect
                material: The material to bind to the prim

            Returns:
                Whether the material was successfully bound to the target prim.
        )"
    );

    m.def(
        "computeEffectivePreviewSurfaceShader",
        &computeEffectivePreviewSurfaceShader,
        arg("material"),
        R"(
            Get the effective surface Shader of a Material for the universal render context.

            Args:
                material: The Material to consider

            Returns:
                The connected Shader. Returns an invalid shader object on error.
        )"
    );

    ::enum_<ColorSpace>(m, "ColorSpace", "Texture color space (encoding) types")
        .value("eAuto", ColorSpace::eAuto, "Check for gamma or metadata in the texture itself")
        .value(
            "eRaw",
            ColorSpace::eRaw,
            "Use linear sampling (typically used for Normal, Roughness, Metallic, Opacity textures, or when using high dynamic range file formats like EXR)"
        )
        .value("eSrgb", ColorSpace::eSrgb, "Use sRGB sampling (typically used for Diffuse textures when using PNG files)");

    m.def(
        "sRgbToLinear",
        &sRgbToLinear,
        arg("color"),
        R"(
            Translate an sRGB color value to linear color space

            Many 3D modeling applications define colors in sRGB (0-1) color space. Many others use a linear color space that aligns with how light
            and color behave in the natural world. When authoring ``UsdShade.Shader`` color input data, including external texture assets, you may
            need to translate between color spaces.

            Note:

                Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is beyond the scope of this
                module. See this [MathWorks article](https://www.mathworks.com/help/images/understanding-color-spaces-and-color-space-conversion.html)
                for a relatively brief introduction. If you need more specific color handling please use a dedicated color science library like
                [OpenColorIO](https://opencolorio.org).

            Args:
                color: sRGB representation of a color to be translated to linear color space

            Returns:
                The translated color in linear color space
        )"
    );

    m.def(
        "linearToSrgb",
        &linearToSrgb,
        arg("color"),
        R"(
            Translate a linear color value to sRGB color space

            Many 3D modeling applications define colors in sRGB (0-1) color space. Many others use a linear color space that aligns with how light
            and color behave in the natural world. When authoring ``UsdShade.Shader`` color input data, including external texture assets, you may
            need to translate between color spaces.

            Note:

                Color is a complex topic in 3D rendering and providing utilities covering the full breadth of color science is beyond the scope of this
                module. See this [MathWorks article](https://www.mathworks.com/help/images/understanding-color-spaces-and-color-space-conversion.html)
                for a relatively brief introduction. If you need more specific color handling please use a dedicated color science library like
                [OpenColorIO](https://opencolorio.org).

            Args:
                color: linear representation of a color to be translated to sRGB color space

            Returns:
                The translated color in sRGB color space
        )"
    );
}

} // namespace usdex::core::bindings
