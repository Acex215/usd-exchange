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

//! @file usdex/pybind/UsdBindings.h
//! @brief Provides pybind11 and boost::python interoperability for OpenUSD types.
//!
//! Many projects use pybind11 for python bindings, but OpenUSD uses boost::python. We often need to pass the python objects in and out of c++
//! between a mix of bound functions. These casters enable pybind11 to consume & to product boost::python bound objects.
//!
//! @note We bind the minimal set of OpenUSD types required by the OpenUSD Exchange SDK public C++ API. Not all types are supported, though more
//! will be added as needed by the public entry points.

#include <pxr/base/arch/defines.h>

#if defined(ARCH_OS_LINUX)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wfloat-conversion" // conversion from ‘double’ to ‘float’ may change value
#include "BindingUtils.h"
#pragma GCC diagnostic pop
#else
#include "BindingUtils.h"
#endif

#include <pxr/base/gf/camera.h>
#include <pxr/base/gf/transform.h>
#include <pxr/usd/sdf/assetPath.h>
#include <pxr/usd/sdf/layer.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/sdf/valueTypeName.h>
#include <pxr/usd/usd/attribute.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usdGeom/basisCurves.h>
#include <pxr/usd/usdGeom/camera.h>
#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdGeom/points.h>
#include <pxr/usd/usdGeom/primvar.h>
#include <pxr/usd/usdGeom/xform.h>
#include <pxr/usd/usdLux/distantLight.h>
#include <pxr/usd/usdLux/domeLight.h>
#include <pxr/usd/usdLux/rectLight.h>
#include <pxr/usd/usdLux/shapingAPI.h>
#include <pxr/usd/usdLux/sphereLight.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdShade/shader.h>


namespace pybind11::detail
{

//! pybind11 / boost::python interop for GfCamera
PYBOOST11_TYPE_CASTER(pxr::GfCamera, _("pxr.Gf.Camera"));
//! pybind11 / boost::python interop for GfVec3d
PYBOOST11_TYPE_CASTER(pxr::GfVec3d, _("pxr.Gf.Vec3d"));
//! pybind11 / boost::python interop for GfVec3f
PYBOOST11_TYPE_CASTER(pxr::GfVec3f, _("pxr.Gf.Vec3f"));
//! pybind11 / boost::python interop for GfVec3i
PYBOOST11_TYPE_CASTER(pxr::GfVec3i, _("pxr.Gf.Vec3i"));
//! pybind11 / boost::python interop for GfMatrix4d
PYBOOST11_TYPE_CASTER(pxr::GfMatrix4d, _("pxr.Gf.Matrix4d"));
//! pybind11 / boost::python interop for GfTransform
PYBOOST11_TYPE_CASTER(pxr::GfTransform, _("pxr.Gf.Transform"));
//! pybind11 / boost::python interop for SdfAssetPath
PYBOOST11_TYPE_CASTER(pxr::SdfAssetPath, _("pxr.Sdf.AssetPath"));
//! pybind11 / boost::python interop for SdfLayerHandle
PYBOOST11_TYPE_CASTER(pxr::SdfLayerHandle, _("pxr.Sdf.Layer"));
//! pybind11 / boost::python interop for SdfPath
PYBOOST11_TYPE_CASTER(pxr::SdfPath, _("pxr.Sdf.Path"));
//! pybind11 / boost::python interop for SdfValueTypeNames
PYBOOST11_TYPE_CASTER(pxr::SdfValueTypeName, _("pxr.Sdf.ValueTypeName"));
//! pybind11 / boost::python interop for TfToken
//!
//! Note we want to inform python clients that regular python strings are the expected value type, not TfTokens
PYBOOST11_TYPE_CASTER(pxr::TfToken, _("str"));
//! pybind11 / boost::python interop for TfTokenVector
//!
//! Note we want to inform python clients that regular python a list of strings are the expected value type
PYBOOST11_TYPE_CASTER(pxr::TfTokenVector, _("list(str)"));
//! pybind11 / boost::python interop for UsdAttribute
PYBOOST11_TYPE_CASTER(pxr::UsdAttribute, _("pxr.Usd.Attribute"));
//! pybind11 / boost::python interop for UsdGeomBasisCurves
PYBOOST11_TYPE_CASTER(pxr::UsdGeomBasisCurves, _("pxr.UsdGeom.BasisCurves"));
//! pybind11 / boost::python interop for UsdGeomCamera
PYBOOST11_TYPE_CASTER(pxr::UsdGeomCamera, _("pxr.UsdGeom.Camera"));
//! pybind11 / boost::python interop for UsdGeomMesh
PYBOOST11_TYPE_CASTER(pxr::UsdGeomMesh, _("pxr.UsdGeom.Mesh"));
//! pybind11 / boost::python interop for UsdGeomPoints
PYBOOST11_TYPE_CASTER(pxr::UsdGeomPoints, _("pxr.UsdGeom.Points"));
//! pybind11 / boost::python interop for UsdGeomPrimvar
PYBOOST11_TYPE_CASTER(pxr::UsdGeomPrimvar, _("pxr.UsdGeom.Primvar"));
//! pybind11 / boost::python interop for UsdGeomXform
PYBOOST11_TYPE_CASTER(pxr::UsdGeomXform, _("pxr.UsdGeom.Xform"));
//! pybind11 / boost::python interop for UsdLuxDistantLight
PYBOOST11_TYPE_CASTER(pxr::UsdLuxDistantLight, _("pxr.UsdLux.DistantLight"));
//! pybind11 / boost::python interop for UsdLuxDomeLight
PYBOOST11_TYPE_CASTER(pxr::UsdLuxDomeLight, _("pxr.UsdLux.DomeLight"));
#if PXR_VERSION >= 2111
//! pybind11 / boost::python interop for UsdLuxLightAPI
PYBOOST11_TYPE_CASTER(pxr::UsdLuxLightAPI, _("pxr.UsdLux.LightAPI"));
#else
//! pybind11 / boost::python interop for UsdLuxLight
PYBOOST11_TYPE_CASTER(pxr::UsdLuxLight, _("pxr.UsdLux.Light"));
#endif // PXR_VERSION >= 2111
//! pybind11 / boost::python interop for UsdLuxRectLight
PYBOOST11_TYPE_CASTER(pxr::UsdLuxRectLight, _("pxr.UsdLux.RectLight"));
//! pybind11 / boost::python interop for UsdLuxSphereLight
PYBOOST11_TYPE_CASTER(pxr::UsdLuxSphereLight, _("pxr.UsdLux.SphereLight"));
//! pybind11 / boost::python interop for UsdLuxShapingAPI
PYBOOST11_TYPE_CASTER(pxr::UsdLuxShapingAPI, _("pxr.UsdLux.ShapingAPI"));
//! pybind11 / boost::python interop for UsdPrim
PYBOOST11_TYPE_CASTER(pxr::UsdPrim, _("pxr.Usd.Prim"));
//! pybind11 / boost::python interop for UsdStagePtr
PYBOOST11_TYPE_CASTER(pxr::UsdStagePtr, _("pxr.Usd.Stage"));
//! pybind11 / boost::python interop for UsdTimeCode
PYBOOST11_TYPE_CASTER(pxr::UsdTimeCode, _("pxr.Usd.TimeCode"));
//! pybind11 / boost::python interop for VtFloatArray
PYBOOST11_TYPE_CASTER(pxr::VtFloatArray, _("pxr.Vt.FloatArray"));
//! pybind11 / boost::python interop for VtIntArray
PYBOOST11_TYPE_CASTER(pxr::VtIntArray, _("pxr.Vt.IntArray"));
//! pybind11 / boost::python interop for VtInt64Array
PYBOOST11_TYPE_CASTER(pxr::VtInt64Array, _("pxr.Vt.Int64Array"));
//! pybind11 / boost::python interop for VtStringArray
PYBOOST11_TYPE_CASTER(pxr::VtStringArray, _("pxr.Vt.StringArray"));
//! pybind11 / boost::python interop for VtTokenArray
PYBOOST11_TYPE_CASTER(pxr::VtTokenArray, _("pxr.Vt.TokenArray"));
//! pybind11 / boost::python interop for VtVec3fArray
PYBOOST11_TYPE_CASTER(pxr::VtVec3fArray, _("pxr.Vt.Vec3fArray"));
//! pybind11 / boost::python interop for VtVec2fArray
PYBOOST11_TYPE_CASTER(pxr::VtVec2fArray, _("pxr.Vt.Vec2fArray"));
//! pybind11 / boost::python interop for UsdShadeInput
PYBOOST11_TYPE_CASTER(pxr::UsdShadeInput, _("pxr.UsdShade.Input"));
//! pybind11 / boost::python interop for UsdShadeMaterial
PYBOOST11_TYPE_CASTER(pxr::UsdShadeMaterial, _("pxr.UsdShade.Material"));
//! pybind11 / boost::python interop for UsdShadeShader
PYBOOST11_TYPE_CASTER(pxr::UsdShadeShader, _("pxr.UsdShade.Shader"));
//! pybind11 / boost::python interop for VtValue
PYBOOST11_TYPE_CASTER(pxr::VtValue, _("pxr.Vt.Value"));

} // namespace pybind11::detail
