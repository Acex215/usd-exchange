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

//! @file usdex/core/MeshAlgo.h
//! @brief Utility functions to create polygonal `UsdGeomMesh` Prims.

#include "Api.h"
#include "PrimvarData.h"

#include <pxr/base/gf/vec2f.h>
#include <pxr/base/gf/vec3f.h>
#include <pxr/base/vt/array.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/mesh.h>

#include <optional>

namespace usdex::core
{

//! @defgroup mesh Mesh Prims
//!
//! Utility functions to create polygonal `UsdGeomMesh` Prims.
//!
//! See [UsdGeomMesh](https://openusd.org/release/api/class_usd_geom_mesh.html) for details.
//! @{

//! Defines a basic polygon mesh on the stage.
//!
//! Attribute values will be validated and in the case of invalid data the Mesh will not be defined.
//! An invalid [UsdGeomMesh](https://openusd.org/release/api/class_usd_geom_mesh.html) object will be returned in this case.
//!
//! A "Subdivision Scheme" of "None" is authored to ensure that the Mesh is not treated as a subdivision surface.
//! For this reason there is no support for authoring subdivision surface attributes during definition.
//!
//! Values will be authored for all attributes required to completely describe the Mesh, even if weaker matching opinions already exist.
//!
//! - Face Vertex Counts
//! - Face Vertex Indices
//! - Points
//! - Extent
//!
//! The orientation of the Mesh is assumed to be "Right Handed". The winding order of the data should be reversed in advance if that is not the case.
//!
//! The "extent" of the Mesh will be computed and authored based on the `points` provided.
//!
//! The following common primvars can optionally be authored at the same time using a `PrimvarData` to specify interpolation, data,
//! and optionally indices or elementSize.
//!
//! - Normals
//! - Primary UV Set
//! - Display Color
//! - Display Opacity
//!
//! Normals are authored as `primvars:normals` so that indexing is possible and to ensure that the value takes precedence in cases where both
//! `normals` and `primvars:normals` are authored.
//! See [UsdGeomPointBased](https://openusd.org/release/api/class_usd_geom_point_based.html#ac9a057e1f221d9a20b99887f35f84480) for details.
//!
//! The primary uv set will be named based on the result of
//! [UsdUtilsGetPrimaryUVSetName()](https://openusd.org/release/api/pipeline_8h.html#aaba37cce54b9db62e0813003dc61cd07).
//! By default the name is "st" but can be configured by extension.
//! See [UsdUtils Pipeline](https://openusd.org/release/api/pipeline_8h.html#details) for details.
//!
//! @param stage The stage on which to define the mesh
//! @param path The absolute prim path at which to define the mesh
//! @param faceVertexCounts The number of vertices in each face of the mesh
//! @param faceVertexIndices Indices of the positions from the `points` to use for each face vertex
//! @param points Vertex positions for the mesh described in local space
//! @param normals Values to be authored for the normals primvar
//! @param uvs Values to be authored for the uv primvar
//! @param displayColor Values to be authored for the display color primvar
//! @param displayOpacity Values to be authored for the display opacity primvar
//! @returns UsdGeomMesh schema wrapping the defined UsdPrim
USDEX_API pxr::UsdGeomMesh definePolyMesh(
    pxr::UsdStagePtr stage,
    const pxr::SdfPath& path,
    const pxr::VtIntArray& faceVertexCounts,
    const pxr::VtIntArray& faceVertexIndices,
    const pxr::VtVec3fArray& points,
    std::optional<const Vec3fPrimvarData> normals = std::nullopt,
    std::optional<const Vec2fPrimvarData> uvs = std::nullopt,
    std::optional<const Vec3fPrimvarData> displayColor = std::nullopt,
    std::optional<const FloatPrimvarData> displayOpacity = std::nullopt
);

//! Defines a basic polygon mesh on the stage.
//!
//! This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.
//!
//! @param parent Prim below which to define the mesh
//! @param name Name of the mesh
//! @param faceVertexCounts The number of vertices in each face of the mesh
//! @param faceVertexIndices Indices of the positions from the `points` to use for each face vertex
//! @param points Vertex positions for the mesh described in local space
//! @param normals Values to be authored for the normals primvar
//! @param uvs Values to be authored for the uv primvar
//! @param displayColor Values to be authored for the display color primvar
//! @param displayOpacity Values to be authored for the display opacity primvar
//!
//! @returns UsdGeomMesh schema wrapping the defined UsdPrim
USDEX_API pxr::UsdGeomMesh definePolyMesh(
    pxr::UsdPrim parent,
    const std::string& name,
    const pxr::VtIntArray& faceVertexCounts,
    const pxr::VtIntArray& faceVertexIndices,
    const pxr::VtVec3fArray& points,
    std::optional<const Vec3fPrimvarData> normals = std::nullopt,
    std::optional<const Vec2fPrimvarData> uvs = std::nullopt,
    std::optional<const Vec3fPrimvarData> displayColor = std::nullopt,
    std::optional<const FloatPrimvarData> displayOpacity = std::nullopt
);

//! @}

} // namespace usdex::core
