// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/MeshAlgo.h"

#include "usdex/core/StageAlgo.h"

#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdGeom/primvarsAPI.h>
#include <pxr/usd/usdUtils/pipeline.h>


using namespace usdex::core;
using namespace pxr;

namespace
{

// Validate the interpolation given the topology information
template <typename T>
bool validatePrimvarInterpolation(
    const PrimvarData<T>& primvar,
    const TfTokenVector& interpolations,
    const VtArray<int>& faceVertexCounts,
    const VtArray<int>& faceVertexIndices,
    const VtArray<GfVec3f>& points
)
{
    if (std::find(interpolations.begin(), interpolations.end(), primvar.interpolation()) == interpolations.end())
    {
        return false;
    }

    size_t size = primvar.effectiveSize();

    // Constant interpolation requires a single value
    if (primvar.interpolation() == UsdGeomTokens->constant && size == 1)
    {
        return true;
    }

    // Uniform interpolation requires a value for every face on the mesh
    if (primvar.interpolation() == UsdGeomTokens->uniform && size == faceVertexCounts.size())
    {
        return true;
    }

    // Vertex interpolation requires a value for every point in the mesh
    if (primvar.interpolation() == UsdGeomTokens->vertex && size == points.size())
    {
        return true;
    }

    // Face varying interpolation requires a value for every face vertex in the mesh
    if (primvar.interpolation() == UsdGeomTokens->faceVarying && size == faceVertexIndices.size())
    {
        return true;
    }

    return false;
}

// Validate a primvar intended for a mesh.
// Accepts a vector of allowed interpolations and returns false if the PrimvarData is not within these allowed values.
// Validates that a valid interpolation was found and that indices (if provided) fit inside the value range.
// If the primvar is invalid and reason is non-null, an error message describing the validation error will be set.
template <typename T>
bool validatePrimvar(
    const PrimvarData<T>& primvar,
    const TfTokenVector& interpolations,
    const VtArray<int>& faceVertexCounts,
    const VtArray<int>& faceVertexIndices,
    const VtArray<GfVec3f>& points,
    std::string* reason
)
{
    if (!::validatePrimvarInterpolation<T>(primvar, interpolations, faceVertexCounts, faceVertexIndices, points))
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf(
                "The interpolation \"%s\" is not valid for %zu %s",
                primvar.interpolation().GetText(),
                primvar.effectiveSize(),
                primvar.hasIndices() ? "indices" : "values"
            );
        }
        return false;
    }

    if (!primvar.isValid())
    {
        if (reason != nullptr)
        {
            *reason = TfStringPrintf("The primvar data is invalid.");
        }
        return false;
    }

    return true;
}

} // namespace

UsdGeomMesh usdex::core::definePolyMesh(
    UsdStagePtr stage,
    const SdfPath& path,
    const VtIntArray& faceVertexCounts,
    const VtIntArray& faceVertexIndices,
    const VtVec3fArray& points,
    std::optional<const Vec3fPrimvarData> normals,
    std::optional<const Vec2fPrimvarData> uvs,
    std::optional<const Vec3fPrimvarData> displayColor,
    std::optional<const FloatPrimvarData> displayOpacity
)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(stage, path, &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomMesh due to an invalid location: %s", reason.c_str());
        return UsdGeomMesh();
    }

    // Early out if the topology is not valid
    if (!UsdGeomMesh::ValidateTopology(faceVertexIndices, faceVertexCounts, points.size(), &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomMesh at \"%s\" due to invalid topology: %s", path.GetAsString().c_str(), reason.c_str());
        return UsdGeomMesh();
    }

    // Early out if normals were specified but not valid
    if (normals.has_value())
    {
        static const TfTokenVector validInterpolations = { UsdGeomTokens->uniform, UsdGeomTokens->vertex, UsdGeomTokens->faceVarying };
        if (!validatePrimvar(normals.value(), validInterpolations, faceVertexCounts, faceVertexIndices, points, &reason))
        {
            TF_RUNTIME_ERROR("Unable to define UsdGeomMesh at \"%s\" due to invalid normals: %s", path.GetAsString().c_str(), reason.c_str());
            return UsdGeomMesh();
        }
    }

    // Early out if uvs were specified but not valid
    if (uvs.has_value())
    {
        static const TfTokenVector validInterpolations = { UsdGeomTokens->vertex, UsdGeomTokens->faceVarying };
        if (!validatePrimvar(uvs.value(), validInterpolations, faceVertexCounts, faceVertexIndices, points, &reason))
        {
            TF_RUNTIME_ERROR("Unable to define UsdGeomMesh at \"%s\" due to invalid uvs: %s", path.GetAsString().c_str(), reason.c_str());
            return UsdGeomMesh();
        }
    }

    // All interpolations are valid by default
    static const TfTokenVector s_allValidInterpolations = { UsdGeomTokens->constant,
                                                            UsdGeomTokens->uniform,
                                                            UsdGeomTokens->varying,
                                                            UsdGeomTokens->vertex,
                                                            UsdGeomTokens->faceVarying };

    // Early out if displayColor was specified but not valid
    if (displayColor.has_value())
    {
        if (!::validatePrimvar(displayColor.value(), s_allValidInterpolations, faceVertexCounts, faceVertexIndices, points, &reason))
        {
            TF_RUNTIME_ERROR("Unable to define UsdGeomMesh at \"%s\" due to invalid display color: %s", path.GetAsString().c_str(), reason.c_str());
            return UsdGeomMesh();
        }
    }

    // Early out if displayOpacity was specified but not valid
    if (displayOpacity.has_value())
    {
        if (!::validatePrimvar(displayOpacity.value(), s_allValidInterpolations, faceVertexCounts, faceVertexIndices, points, &reason))
        {
            TF_RUNTIME_ERROR("Unable to define UsdGeomMesh at \"%s\" due to invalid display opacity: %s", path.GetAsString().c_str(), reason.c_str());
            return UsdGeomMesh();
        }
    }

    // Define the Mesh and check that this was successful
    UsdGeomMesh mesh = UsdGeomMesh::Define(stage, path);
    if (!mesh)
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomMesh at \"%s\"", path.GetAsString().c_str());
        return UsdGeomMesh();
    }

    // Explicitly author the specifier and type name
    UsdPrim prim = mesh.GetPrim();
    prim.SetSpecifier(SdfSpecifierDef);
    prim.SetTypeName(prim.GetTypeName());

    // Author opinions on Mesh attributes
    mesh.CreateOrientationAttr().Set(UsdGeomTokens->rightHanded);
    mesh.CreateSubdivisionSchemeAttr().Set(UsdGeomTokens->none);

    // Create and set required topology attributes
    mesh.CreateFaceVertexCountsAttr().Set(faceVertexCounts);
    mesh.CreateFaceVertexIndicesAttr().Set(faceVertexIndices);
    mesh.CreatePointsAttr().Set(points);

    // Compute an extent from the points so there is a guarantee that the extent will be correct and authored in all cases.
    VtArray<GfVec3f> extent;
    UsdGeomPointBased::ComputeExtent(points, &extent);
    mesh.CreateExtentAttr().Set(extent);

    // Optionally author normals
    if (normals.has_value())
    {
        // Define the normals primvar
        const TfToken& name = UsdGeomTokens->normals;
        const SdfValueTypeName& typeName = SdfValueTypeNames->Normal3fArray;
        UsdGeomPrimvar primvar = UsdGeomPrimvarsAPI(mesh.GetPrim()).CreatePrimvar(name, typeName);
        if (!normals.value().setPrimvar(primvar))
        {
            TF_WARN("Failed to set normals primvar for UsdGeomMesh at \"%s\"", path.GetAsString().c_str());
        }
    }

    // Optionally author the primary UV set
    if (uvs.has_value())
    {
        const TfToken& name = UsdUtilsGetPrimaryUVSetName();
        const SdfValueTypeName& typeName = SdfValueTypeNames->TexCoord2fArray;
        UsdGeomPrimvar primvar = UsdGeomPrimvarsAPI(mesh.GetPrim()).CreatePrimvar(name, typeName);
        if (!uvs.value().setPrimvar(primvar))
        {
            TF_WARN("Failed to set uvs primvar for UsdGeomMesh at \"%s\"", path.GetAsString().c_str());
        }
    }

    // Optionally author display color
    if (displayColor.has_value())
    {
        UsdGeomPrimvar primvar = mesh.CreateDisplayColorPrimvar();
        if (!displayColor.value().setPrimvar(primvar))
        {
            TF_WARN("Failed to set display color primvar for UsdGeomMesh at \"%s\"", path.GetAsString().c_str());
        }
    }

    // Optionally author display opacity
    if (displayOpacity.has_value())
    {
        UsdGeomPrimvar primvar = mesh.CreateDisplayOpacityPrimvar();
        if (!displayOpacity.value().setPrimvar(primvar))
        {
            TF_WARN("Failed to set display opacity primvar for UsdGeomMesh at \"%s\"", path.GetAsString().c_str());
        }
    }

    return mesh;
}

UsdGeomMesh usdex::core::definePolyMesh(
    UsdPrim parent,
    const std::string& name,
    const VtIntArray& faceVertexCounts,
    const VtIntArray& faceVertexIndices,
    const VtVec3fArray& points,
    std::optional<const Vec3fPrimvarData> normals,
    std::optional<const Vec2fPrimvarData> uvs,
    std::optional<const Vec3fPrimvarData> displayColor,
    std::optional<const FloatPrimvarData> displayOpacity
)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(parent, name, &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomMesh due to an invalid location: %s", reason.c_str());
        return UsdGeomMesh();
    }

    // Call overloaded function
    UsdStageWeakPtr stage = parent.GetStage();
    const SdfPath path = parent.GetPath().AppendChild(TfToken(name));
    return usdex::core::definePolyMesh(stage, path, faceVertexCounts, faceVertexIndices, points, normals, uvs, displayColor, displayOpacity);
}
