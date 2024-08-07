// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/CameraAlgo.h"

#include "usdex/core/StageAlgo.h"

#include <pxr/base/tf/diagnostic.h>
#include <pxr/usd/usdGeom/xformable.h>


using namespace pxr;

UsdGeomCamera usdex::core::defineCamera(UsdStagePtr stage, const SdfPath& path, const GfCamera& cameraData)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(stage, path, &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomCamera due to an invalid location: %s", reason.c_str());
        return UsdGeomCamera();
    }

    // Early out if we know that we cannot successfully set the camera attributes
    // UsdGeomCamera::SetFromCamera() will silently fail if it is unable to successfully call UsdGeomXformable::MakeMatrixXform()
    // In order to catch this case we attempt that change ourselves prior to defining the camera
    if (auto xformable = UsdGeomXformable::Get(stage, path))
    {
        // The xformOp may be invalid if there are xform op opinions in the composed layer stack stronger than that of the current edit target.
        if (!xformable.MakeMatrixXform())
        {
            TF_RUNTIME_ERROR(
                "Unable to define UsdGeomCamera at \"%s\" due to non-editable attributes: %s",
                path.GetAsString().c_str(),
                "Xform op opinions in the composed layer stack are stronger than that of the current edit target"
            );
            return UsdGeomCamera();
        }
    }

    UsdGeomCamera camera = UsdGeomCamera::Define(stage, path);
    if (!camera)
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomCamera at \"%s\"", path.GetAsString().c_str());
        return camera;
    }

    // Explicitly author the specifier and type name
    UsdPrim prim = camera.GetPrim();
    prim.SetSpecifier(SdfSpecifierDef);
    prim.SetTypeName(prim.GetTypeName());

    camera.SetFromCamera(cameraData, UsdTimeCode::Default());

    return camera;
}

UsdGeomCamera usdex::core::defineCamera(UsdPrim parent, const std::string& name, const GfCamera& cameraData)
{
    // Early out if the proposed prim location is invalid
    std::string reason;
    if (!usdex::core::isEditablePrimLocation(parent, name, &reason))
    {
        TF_RUNTIME_ERROR("Unable to define UsdGeomCamera due to an invalid location: %s", reason.c_str());
        return UsdGeomCamera();
    }

    // Call overloaded function
    UsdStageWeakPtr stage = parent.GetStage();
    const SdfPath path = parent.GetPath().AppendChild(TfToken(name));
    return usdex::core::defineCamera(stage, path, cameraData);
}
