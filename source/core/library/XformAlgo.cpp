// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/XformAlgo.h"

#include "usdex/core/StageAlgo.h"

#include <pxr/base/tf/token.h>
#include <pxr/usd/usdGeom/xformCommonAPI.h>
#include <pxr/usd/usdGeom/xformOp.h>
#include <pxr/usd/usdGeom/xformable.h>


using namespace pxr;


namespace
{

static const GfRotation g_identityRotation = GfRotation().SetIdentity();
static const GfVec3d g_identityTranslation = GfVec3d(0.0, 0.0, 0.0);


template <class HalfType, class FloatType, class DoubleType, class ValueType>
bool setValueWithPrecision(UsdGeomXformOp& xformOp, const ValueType& value, const UsdTimeCode& time)
{
    switch (xformOp.GetPrecision())
    {
        case UsdGeomXformOp::PrecisionHalf:
        {
            return xformOp.Set(HalfType(FloatType(value)), time);
        }
        case UsdGeomXformOp::PrecisionFloat:
        {
            return xformOp.Set(FloatType(value), time);
        }
        case UsdGeomXformOp::PrecisionDouble:
        {
            return xformOp.Set(DoubleType(value), time);
        }
    }
    return false;
}

UsdGeomXformCommonAPI::RotationOrder convertRotationOrder(const usdex::core::RotationOrder& rotationOrder)
{
    switch (rotationOrder)
    {
        case usdex::core::RotationOrder::eXyz:
            return UsdGeomXformCommonAPI::RotationOrderXYZ;
        case usdex::core::RotationOrder::eXzy:
            return UsdGeomXformCommonAPI::RotationOrderXZY;
        case usdex::core::RotationOrder::eYxz:
            return UsdGeomXformCommonAPI::RotationOrderYXZ;
        case usdex::core::RotationOrder::eYzx:
            return UsdGeomXformCommonAPI::RotationOrderYZX;
        case usdex::core::RotationOrder::eZxy:
            return UsdGeomXformCommonAPI::RotationOrderZXY;
        case usdex::core::RotationOrder::eZyx:
            return UsdGeomXformCommonAPI::RotationOrderZYX;
        default:
            // Default rotation order is XYZ.
            return UsdGeomXformCommonAPI::RotationOrderXYZ;
    }
}

usdex::core::RotationOrder convertRotationOrder(const UsdGeomXformCommonAPI::RotationOrder& rotationOrder)
{
    switch (rotationOrder)
    {
        case UsdGeomXformCommonAPI::RotationOrderXYZ:
            return usdex::core::RotationOrder::eXyz;
        case UsdGeomXformCommonAPI::RotationOrderXZY:
            return usdex::core::RotationOrder::eXzy;
        case UsdGeomXformCommonAPI::RotationOrderYXZ:
            return usdex::core::RotationOrder::eYxz;
        case UsdGeomXformCommonAPI::RotationOrderYZX:
            return usdex::core::RotationOrder::eYzx;
        case UsdGeomXformCommonAPI::RotationOrderZXY:
            return usdex::core::RotationOrder::eZxy;
        case UsdGeomXformCommonAPI::RotationOrderZYX:
            return usdex::core::RotationOrder::eZyx;
        default:
            // Default rotation order is XYZ.
            return usdex::core::RotationOrder::eXyz;
    }
}

GfVec3i getAxisIndices(const usdex::core::RotationOrder& rotationOrder)
{
    switch (rotationOrder)
    {
        case usdex::core::RotationOrder::eXyz:
            return GfVec3i(0, 1, 2);
        case usdex::core::RotationOrder::eXzy:
            return GfVec3i(0, 2, 1);
        case usdex::core::RotationOrder::eYxz:
            return GfVec3i(1, 0, 2);
        case usdex::core::RotationOrder::eYzx:
            return GfVec3i(1, 2, 0);
        case usdex::core::RotationOrder::eZxy:
            return GfVec3i(2, 0, 1);
        case usdex::core::RotationOrder::eZyx:
            return GfVec3i(2, 1, 0);
        default:
            // Default rotation order is XYZ.
            return GfVec3i(0, 1, 2);
    }
}

// Returns true if the transform has a non-identity pivot orientation
bool hasPivotOrientation(const GfTransform& transform)
{
    return transform.GetPivotOrientation() != g_identityRotation;
}

// Returns true if the transform has a non-identity pivot position
bool hasPivotPosition(const GfTransform& transform)
{
    return transform.GetPivotPosition() != g_identityTranslation;
}

// Compute the XYZ rotation values from a Rotation object via decomposition.
GfVec3d computeXyzRotationsFromRotation(const GfRotation& rotate)
{
    const GfVec3d angles = rotate.Decompose(GfVec3d::ZAxis(), GfVec3d::YAxis(), GfVec3d::XAxis());
    return GfVec3d(angles[2], angles[1], angles[0]);
}

GfRotation computeRotation(const GfVec3f& rotations, const usdex::core::RotationOrder rotationOrder)
{
    static const GfVec3d xyzAxes[] = { GfVec3d::XAxis(), GfVec3d::YAxis(), GfVec3d::ZAxis() };
    const GfVec3i indices = getAxisIndices(rotationOrder);

    GfRotation rotation = GfRotation(xyzAxes[indices[0]], rotations[indices[0]]);
    if (rotations[indices[1]] != 0.0)
    {
        rotation = rotation * GfRotation(xyzAxes[indices[1]], rotations[indices[1]]);
    }
    if (rotations[indices[2]] != 0.0)
    {
        rotation = rotation * GfRotation(xyzAxes[indices[2]], rotations[indices[2]]);
    }
    return rotation;
}

GfTransform computeTransformFromComponents(
    const GfVec3d& translation,
    const GfVec3d& pivot,
    const GfVec3f& rotation,
    const usdex::core::RotationOrder rotationOrder,
    const GfVec3f& scale
)
{
    // FUTURE: Refactor this to retain rotations greater than 360 degrees.
    // Right now a rotation greater than 360 will only be retained if it is in the first position and the remaining two are zero
    // otherwise the multiply function will compute a new rotation in a lossy manner.

    // Compute a rotation from the rotation vector and rotation order
    GfRotation rotate = computeRotation(rotation, rotationOrder);

    // Build a transform from the components and computed rotation
    GfTransform transform = GfTransform();
    transform.SetTranslation(translation);
    transform.SetPivotPosition(pivot);
    transform.SetRotation(rotate);
    transform.SetScale(GfVec3d(scale));

    return transform;
}

GfMatrix4d computeMatrixFromComponents(
    const GfVec3d& translation,
    const GfVec3d& pivot,
    const GfVec3f& rotation,
    const usdex::core::RotationOrder rotationOrder,
    const GfVec3f& scale
)
{
    // Build a transform from the components and return it's internal matrix
    const GfTransform transform = computeTransformFromComponents(translation, pivot, rotation, rotationOrder, scale);
    return transform.GetMatrix();
}


// Given a 4x4 matrix compute the values of common components
void computeComponentsFromMatrix(
    const GfMatrix4d& matrix,
    GfVec3d& translation,
    GfVec3d& pivot,
    GfVec3f& rotation,
    usdex::core::RotationOrder& rotationOrder,
    GfVec3f& scale
)
{
    // Get the components from the transform and cast to the expected precision
    const GfTransform transform = GfTransform(matrix);
    translation = transform.GetTranslation();
    pivot = transform.GetPivotPosition();

    // Decompose rotation into a rotationOrder of XYZ and convert from double to float
    rotation = GfVec3f(computeXyzRotationsFromRotation(transform.GetRotation()));
    rotationOrder = usdex::core::RotationOrder::eXyz;

    // Convert scale from double to float
    scale = GfVec3f(transform.GetScale());
}

// Overloaded version of UsdGeomXformCommonAPI::GetXformVectorsByAccumulation which treats pivot as a double
void getXformVectorsByAccumulation(
    const UsdGeomXformCommonAPI& xformCommonAPI,
    GfVec3d* translation,
    GfVec3d* pivot,
    GfVec3f* rotation,
    usdex::core::RotationOrder* rotationOrder,
    GfVec3f* scale,
    const UsdTimeCode time
)
{
    // Get the xform vectors in the types expected by the xformCommonAPI
    GfVec3f pivotFloat;
    UsdGeomXformCommonAPI::RotationOrder rotOrder;
    xformCommonAPI.GetXformVectors(translation, rotation, scale, &pivotFloat, &rotOrder, time);

    // Convert types to those expected by usdex_core
    pivot->Set(pivotFloat[0], pivotFloat[1], pivotFloat[2]);
    *rotationOrder = convertRotationOrder(rotOrder);
}

// Returns whether the authored xformOps are compatible with a matrix value
// The "transformOp" argument will be populated with the existing xformOp if one is authored
bool getMatrixXformOp(const std::vector<UsdGeomXformOp>& xformOps, UsdGeomXformOp* transformOp)
{
    // If there are no existing xformOps then it is compatible
    if (xformOps.empty())
    {
        return true;
    }

    // If there is more than one xformOp then it is not compatible
    if (xformOps.size() > 1)
    {
        return false;
    }

    // The xformOp it must be of type transform but not and inverse op to be compatible
    if (xformOps[0].GetOpType() == UsdGeomXformOp::TypeTransform && !xformOps[0].IsInverseOp())
    {
        *transformOp = std::move(xformOps[0]);
        return true;
    }

    return false;
}

// Ensure that there is an opinion about the xformOpOrder value in the current edit target layer
void ensureXformOpOrderExplicitlyAuthored(UsdGeomXformable& xformable)
{
    UsdAttribute attr = xformable.GetXformOpOrderAttr();
    SdfLayerHandle layer = xformable.GetPrim().GetStage()->GetEditTarget().GetLayer();

    if (!layer->HasSpec(attr.GetPath()))
    {
        VtArray<TfToken> value;
        if (attr.Get(&value))
        {
            attr.Set(value);
        }
    }
}

} // namespace

bool usdex::core::setLocalTransform(UsdPrim prim, const GfTransform& transform, UsdTimeCode time)
{
    // Early out with a failure return if the prim is not xformable
    UsdGeomXformable xformable(prim);
    if (!xformable)
    {
        return false;
    }

    // Assuming there is no existing compatible xformOpOrder inspect the transform to identify the most expressive xformOpOrder to use.
    // For performance reasons we want to use a single transform xformOp. See: https://groups.google.com/g/usd-interest/c/MR5DFhQEYSE/m/o7bSnWwNAgAJ

    // However we would ideally retain pivot position so if authored prefer the XformCommonAPI.
    // The XformCommonAPI cannot express pivotOrientation so if it has a non-identity value we need to use a transform xformOp.
    bool needsXformCommonAPI = (hasPivotPosition(transform) && !hasPivotOrientation(transform));

    // Get the existing xformOps and attempt to reuse them if compatible
    bool resetsXformStack;
    std::vector<UsdGeomXformOp> xformOps = xformable.GetOrderedXformOps(&resetsXformStack);
    if (!xformOps.empty())
    {
        // Only try to reuse the matrix xform op if the transform does not need the xformCommonAPI to express it's value
        if (!needsXformCommonAPI)
        {
            // Set the value on an existing transform xformOp if one is already authored
            UsdGeomXformOp transformXformOp;
            if (getMatrixXformOp(xformOps, &transformXformOp) && transformXformOp.IsDefined())
            {
                const GfMatrix4d matrix = transform.GetMatrix();
                transformXformOp.Set(matrix, time);
                ensureXformOpOrderExplicitlyAuthored(xformable);

                return true;
            }
        }

        // FUTURE: Attempt to reuse existing UsdGeomXformCommonAPI xformOps
    }

    // Author using UsdGeomXformCommonAPI if appropriate
    if (needsXformCommonAPI)
    {
        // Modify the xformOpOrder and set xformOp values to achieve the transform
        if (!UsdGeomXformCommonAPI(prim))
        {
            xformable.ClearXformOpOrder();
        }

        const GfVec3d rotation = computeXyzRotationsFromRotation(transform.GetRotation());

        // Get or create the UsdGeomXformCommonAPI xformOps
        UsdGeomXformCommonAPI xformCommonAPI = UsdGeomXformCommonAPI(prim);
        UsdGeomXformCommonAPI::Ops commonXformOps = xformCommonAPI.CreateXformOps(
            UsdGeomXformCommonAPI::RotationOrderXYZ,
            UsdGeomXformCommonAPI::OpTranslate,
            UsdGeomXformCommonAPI::OpPivot,
            UsdGeomXformCommonAPI::OpRotate,
            UsdGeomXformCommonAPI::OpScale
        );

        // Set the UsdGeomXformCommonAPI xformOp values allowing setValueWithPrecision to handle any value type conversions
        setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(commonXformOps.translateOp, transform.GetTranslation(), time);
        setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(commonXformOps.pivotOp, transform.GetPivotPosition(), time);
        setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(commonXformOps.rotateOp, rotation, time);
        setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(commonXformOps.scaleOp, transform.GetScale(), time);
        ensureXformOpOrderExplicitlyAuthored(xformable);

        return true;
    }

    // Modify the xformOpOrder and set xformOp values to achieve the transform
    const GfMatrix4d matrix = transform.GetMatrix();
    UsdGeomXformOp transformXformOp = xformable.MakeMatrixXform();
    transformXformOp.Set(matrix, time);
    ensureXformOpOrderExplicitlyAuthored(xformable);

    return true;
}

bool usdex::core::setLocalTransform(UsdPrim prim, const GfMatrix4d& matrix, UsdTimeCode time)
{
    // Early out with a failure return if the prim is not xformable
    UsdGeomXformable xformable(prim);
    if (!xformable)
    {
        return false;
    }

    // Get the existing xformOps and attempt to reuse them if compatible
    bool resetsXformStack;
    std::vector<UsdGeomXformOp> xformOps = xformable.GetOrderedXformOps(&resetsXformStack);
    if (!xformOps.empty())
    {
        // Set the value on an existing transform xformOp if one is already authored
        UsdGeomXformOp transformXformOp;
        if (getMatrixXformOp(xformOps, &transformXformOp) && transformXformOp.IsDefined())
        {
            transformXformOp.Set(matrix, time);
            ensureXformOpOrderExplicitlyAuthored(xformable);

            return true;
        }

        // FUTURE: Attempt to reuse existing UsdGeomXformCommonAPI xformOps
    }

    // Assuming there is no existing compatible xformOpOrder
    // Modify the xformOpOrder to use the most expressive xformOp stack and set xformOp values to achieve the transform
    UsdGeomXformOp transformXformOp = xformable.MakeMatrixXform();
    transformXformOp.Set(matrix, time);
    ensureXformOpOrderExplicitlyAuthored(xformable);

    return true;
}

bool usdex::core::setLocalTransform(
    UsdPrim prim,
    const GfVec3d& translation,
    const GfVec3d& pivot,
    const GfVec3f& rotation,
    const usdex::core::RotationOrder rotationOrder,
    const GfVec3f& scale,
    UsdTimeCode time
)
{
    // Early out with a failure return if the prim is not xformable
    UsdGeomXformable xformable(prim);
    if (!xformable)
    {
        return false;
    }

    // We would ideally retain pivot position so if it is non-identity prefer the XformCommonAPI.
    bool needsXformCommonAPI = (pivot != g_identityTranslation);

    // Get the existing xformOps and attempt to reuse them if compatible
    bool resetsXformStack;
    std::vector<UsdGeomXformOp> xformOps = xformable.GetOrderedXformOps(&resetsXformStack);
    if (!xformOps.empty())
    {
        // Only try to reuse the matrix xform op if the transform does not need the xformCommonAPI to express it's value
        if (!needsXformCommonAPI)
        {
            // Set the value on an existing transform xformOp if one is already authored
            UsdGeomXformOp transformXformOp;
            if (getMatrixXformOp(xformOps, &transformXformOp) && transformXformOp.IsDefined())
            {
                const GfMatrix4d matrix = computeMatrixFromComponents(translation, pivot, rotation, rotationOrder, scale);
                transformXformOp.Set(matrix, time);
                ensureXformOpOrderExplicitlyAuthored(xformable);

                return true;
            }
        }

        // FUTURE: Attempt to reuse existing UsdGeomXformCommonAPI xformOps
    }

    // Modify the xformOpOrder and set xformOp values to achieve the transform
    if (!UsdGeomXformCommonAPI(prim))
    {
        xformable.ClearXformOpOrder();
    }

    const UsdGeomXformCommonAPI::RotationOrder rotationOrderEnum = convertRotationOrder(rotationOrder);

    // Get or create the UsdGeomXformCommonAPI xformOps
    UsdGeomXformCommonAPI xformCommonAPI = UsdGeomXformCommonAPI(prim);
    UsdGeomXformCommonAPI::Ops commonXformOps = xformCommonAPI.CreateXformOps(
        rotationOrderEnum,
        UsdGeomXformCommonAPI::OpTranslate,
        UsdGeomXformCommonAPI::OpPivot,
        UsdGeomXformCommonAPI::OpRotate,
        UsdGeomXformCommonAPI::OpScale
    );

    // Set the UsdGeomXformCommonAPI xformOp values allowing setValueWithPrecision to handle any value type conversions
    setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(commonXformOps.translateOp, translation, time);
    setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(commonXformOps.pivotOp, pivot, time);
    setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3f>(commonXformOps.rotateOp, rotation, time);
    setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3f>(commonXformOps.scaleOp, scale, time);
    ensureXformOpOrderExplicitlyAuthored(xformable);

    return true;
}

GfTransform usdex::core::getLocalTransform(const UsdPrim& prim, UsdTimeCode time)
{
    // Initialize an identity transform as the fallback return
    GfTransform transform = GfTransform();

    // Early out if the prim is not xformable
    UsdGeomXformable xformable(prim);
    if (!xformable)
    {
        return transform;
    }

    // Attempt to extract existing xformOp values
    UsdGeomXformCommonAPI xformCommonAPI = UsdGeomXformCommonAPI(prim);
    if (xformCommonAPI)
    {
        // Extract transform components
        GfVec3d translation;
        GfVec3d pivot;
        GfVec3f rotation;
        usdex::core::RotationOrder rotOrder;
        GfVec3f scale;
        getXformVectorsByAccumulation(xformCommonAPI, &translation, &pivot, &rotation, &rotOrder, &scale, time);

        // Construct and return a transform from the components
        return computeTransformFromComponents(translation, pivot, rotation, rotOrder, scale);
    }

    // Compute the local transform matrix and populate the result from that
    GfMatrix4d matrix;
    bool resetsXformStack;
    if (xformable.GetLocalTransformation(&matrix, &resetsXformStack, time))
    {
        transform.SetMatrix(matrix);
    }

    return transform;
}

GfMatrix4d usdex::core::getLocalTransformMatrix(const UsdPrim& prim, UsdTimeCode time)
{
    // Initialize an identity matrix as the fallback return
    GfMatrix4d matrix = GfMatrix4d(1.0);

    // Early out if the prim is not xformable
    UsdGeomXformable xformable(prim);
    if (!xformable)
    {
        return matrix;
    }

    // Compute the local transform matrix and populate the result from that
    bool resetsXformStack;
    if (!xformable.GetLocalTransformation(&matrix, &resetsXformStack, time))
    {
        matrix.SetIdentity();
    }

    return matrix;
}

void usdex::core::getLocalTransformComponents(
    const UsdPrim& prim,
    GfVec3d& translation,
    GfVec3d& pivot,
    GfVec3f& rotation,
    usdex::core::RotationOrder& rotationOrder,
    GfVec3f& scale,
    UsdTimeCode time
)
{
    // Initialize as identity
    translation.Set(0.0, 0.0, 0.0);
    pivot.Set(0.0, 0.0, 0.0);
    rotation.Set(0.0, 0.0, 0.0);
    rotationOrder = usdex::core::RotationOrder::eXyz;
    scale.Set(1.0, 1.0, 1.0);

    // Early out if the prim is not xformable
    UsdGeomXformable xformable(prim);
    if (!xformable)
    {
        return;
    }

    // Attempt to extract existing xformOp values
    UsdGeomXformCommonAPI xformCommonAPI = UsdGeomXformCommonAPI(prim);
    if (xformCommonAPI)
    {
        // Extract transform components
        getXformVectorsByAccumulation(xformCommonAPI, &translation, &pivot, &rotation, &rotationOrder, &scale, time);
        return;
    }

    // Compute the local transform matrix and populate the result from that
    GfMatrix4d matrix;
    bool resetsXformStack;
    if (xformable.GetLocalTransformation(&matrix, &resetsXformStack, time))
    {
        computeComponentsFromMatrix(matrix, translation, pivot, rotation, rotationOrder, scale);
        return;
    }
}

UsdGeomXform usdex::core::defineXform(UsdStagePtr stage, const SdfPath& path, std::optional<const pxr::GfTransform> transform)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(stage, path, &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomXform due to an invalid location: %s", reason.c_str());
        return UsdGeomXform();
    }

    // Define the Xform and check that this was successful
    UsdGeomXform xform = UsdGeomXform::Define(stage, path);
    if (!xform)
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomXform at \"%s\"", path.GetAsString().c_str());
        return UsdGeomXform();
    }

    // Explicitly author the specifier and type name
    UsdPrim prim = xform.GetPrim();
    prim.SetSpecifier(SdfSpecifierDef);
    prim.SetTypeName(prim.GetTypeName());

    // Set the local transform if one was supplied
    if (transform.has_value())
    {
        usdex::core::setLocalTransform(prim, transform.value(), UsdTimeCode::Default());
    }

    return xform;
}

UsdGeomXform usdex::core::defineXform(UsdPrim parent, const std::string& name, std::optional<const pxr::GfTransform> transform)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(parent, name, &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomXform due to an invalid location: %s", reason.c_str());
        return UsdGeomXform();
    }

    // Call overloaded function
    UsdStageWeakPtr stage = parent.GetStage();
    const SdfPath path = parent.GetPath().AppendChild(TfToken(name));
    return usdex::core::defineXform(stage, path, transform);
}
