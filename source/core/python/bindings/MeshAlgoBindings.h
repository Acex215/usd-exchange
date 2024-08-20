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

#include "usdex/core/MeshAlgo.h"

#include "usdex/pybind/UsdBindings.h"

#include <pybind11/pybind11.h>

using namespace usdex::core;
using namespace pybind11;
using namespace pxr;


namespace usdex::core::bindings
{

void bindMeshAlgo(module& m)
{
    m.def(
        "definePolyMesh",
        overload_cast<
            UsdStagePtr,
            const SdfPath&,
            const VtIntArray&,
            const VtIntArray&,
            const VtVec3fArray&,
            std::optional<const Vec3fPrimvarData>,
            std::optional<const Vec2fPrimvarData>,
            std::optional<const Vec3fPrimvarData>,
            std::optional<const FloatPrimvarData>>(&definePolyMesh),
        arg("stage"),
        arg("path"),
        arg("faceVertexCounts"),
        arg("faceVertexIndices"),
        arg("points"),
        arg("normals") = nullptr,
        arg("uvs") = nullptr,
        arg("displayColor") = nullptr,
        arg("displayOpacity") = nullptr,
        R"(
            Defines a basic polygon mesh on the stage.

            All interrelated attribute values will be authored, even if weaker matching opinions already exist.

            The following common primvars can optionally be authored at the same time.

                - Normals
                - Primary UV Set
                - Display Color
                - Display Opacity

            Parameters:
                - **stage** - The stage on which to define the mesh
                - **path** - The absolute prim path at which to define the mesh
                - **faceVertexCounts** - The number of vertices in each face of the mesh
                - **faceVertexIndices** - Indices of the positions from the ``points`` to use for each face vertex
                - **points** - Vertex positions for the mesh described points in local space
                - **normals** - Values to be authored for the normals primvar
                - **uvs** - Values to be authored for the uv primvar
                - **displayColor** - Value to be authored for the display color primvar
                - **displayOpacity** - Value to be authored for the display opacity primvar

            Returns:
                ``UsdGeom.Mesh`` schema wrapping the defined ``Usd.Prim``.

        )"
    );

    m.def(
        "definePolyMesh",
        overload_cast<
            UsdPrim,
            const std::string&,
            const VtIntArray&,
            const VtIntArray&,
            const VtVec3fArray&,
            std::optional<const Vec3fPrimvarData>,
            std::optional<const Vec2fPrimvarData>,
            std::optional<const Vec3fPrimvarData>,
            std::optional<const FloatPrimvarData>>(&definePolyMesh),
        arg("parent"),
        arg("name"),
        arg("faceVertexCounts"),
        arg("faceVertexIndices"),
        arg("points"),
        arg("normals") = nullptr,
        arg("uvs") = nullptr,
        arg("displayColor") = nullptr,
        arg("displayOpacity") = nullptr,
        R"(
            Defines a basic polygon mesh on the stage.

            All interrelated attribute values will be authored, even if weaker matching opinions already exist.

            This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

            Parameters:
                - **parent** - Prim below which to define the mesh
                - **name** - Name of the mesh
                - **faceVertexCounts** - The number of vertices in each face of the mesh
                - **faceVertexIndices** - Indices of the positions from the ``points`` to use for each face vertex
                - **points** - Vertex positions for the mesh described points in local space
                - **normals** - Values to be authored for the normals primvar
                - **uvs** - Values to be authored for the uv primvar
                - **displayColor** - Value to be authored for the display color primvar
                - **displayOpacity** - Value to be authored for the display opacity primvar

            Returns:
                ``UsdGeom.Mesh`` schema wrapping the defined ``Usd.Prim``.

        )"
    );
}

} // namespace usdex::core::bindings
