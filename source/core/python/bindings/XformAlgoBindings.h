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

#include "usdex/core/XformAlgo.h"

#include "usdex/pybind/UsdBindings.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


using namespace usdex::core;
using namespace pybind11;

using namespace pxr;

namespace usdex::core::bindings
{

void bindXformAlgo(module& m)
{
    pybind11::enum_<RotationOrder>(m, "RotationOrder", "Enumerates the rotation order of the 3-angle Euler rotation.")
        .value("eXyz", RotationOrder::eXyz)
        .value("eXzy", RotationOrder::eXzy)
        .value("eYxz", RotationOrder::eYxz)
        .value("eYzx", RotationOrder::eYzx)
        .value("eZxy", RotationOrder::eZxy)
        .value("eZyx", RotationOrder::eZyx);

    m.def(
        "setLocalTransform",
        overload_cast<UsdPrim, const GfTransform&, UsdTimeCode>(&setLocalTransform),
        arg("prim"),
        arg("transform"),
        arg("time") = std::numeric_limits<double>::quiet_NaN(),
        R"(
            Set the local transform of a prim.

            Parameters:
                - **prim** - The prim to set local transform on.
                - **transform** - The transform value to set.
                - **time** - Time at which to write the value.

            Returns:
                A bool indicating if the local transform was set.

        )",
        call_guard<gil_scoped_release>()
    );

    m.def(
        "setLocalTransform",
        overload_cast<UsdPrim, const GfMatrix4d&, UsdTimeCode>(&setLocalTransform),
        arg("prim"),
        arg("matrix"),
        arg("time") = std::numeric_limits<double>::quiet_NaN(),
        R"(
            Set the local transform of a prim from a 4x4 matrix.

            Parameters:
                - **prim** - The prim to set local transform on.
                - **matrix** - The matrix value to set.
                - **time** - Time at which to write the value.

            Returns:
                A bool indicating if the local transform was set.

        )",
        call_guard<gil_scoped_release>()
    );

    m.def(
        "setLocalTransform",
        overload_cast<UsdPrim, const GfVec3d&, const GfVec3d&, const GfVec3f&, const RotationOrder, const GfVec3f&, UsdTimeCode>(&setLocalTransform),
        arg("prim"),
        arg("translation"),
        arg("pivot"),
        arg("rotation"),
        arg("rotationOrder"),
        arg("scale"),
        arg("time") = std::numeric_limits<double>::quiet_NaN(),
        R"(
            Set the local transform of a prim from common transform components.

            Parameters:
                - **prim** - The prim to set local transform on.
                - **translation** - The translation value to set.
                - **pivot** - The pivot position value to set.
                - **rotation** - The rotation value to set in degrees.
                - **rotationOrder** - The rotation order of the rotation value.
                - **scale** - The scale value to set.
                - **time** - Time at which to write the value.

            Returns:
                A bool indicating if the local transform was set.

        )",
        call_guard<gil_scoped_release>()
    );

    m.def(
        "getLocalTransform",
        &getLocalTransform,
        arg("prim"),
        arg("time") = std::numeric_limits<double>::quiet_NaN(),
        R"(
            Get the local transform of a prim at a given time.

            Args:
                prim: The prim to get local transform from.
                time: Time at which to query the value.

            Returns:
                Transform value as a transform.

        )"
    );

    m.def(
        "getLocalTransformMatrix",
        &getLocalTransformMatrix,
        arg("prim"),
        arg("time") = std::numeric_limits<double>::quiet_NaN(),
        R"(
            Get the local transform of a prim at a given time in the form of a 4x4 matrix.

            Args:
                prim: The prim to get local transform from.
                time: Time at which to query the value.

            Returns:
                Transform value as a 4x4 matrix.

        )"
    );

    m.def(
        "getLocalTransformComponents",
        [](const UsdPrim& prim, UsdTimeCode time)
        {
            GfVec3d translation;
            GfVec3d pivot;
            GfVec3f rotation;
            RotationOrder rotationOrder;
            GfVec3f scale;
            getLocalTransformComponents(prim, translation, pivot, rotation, rotationOrder, scale, time);
            return make_tuple(translation, pivot, rotation, rotationOrder, scale);
        },
        arg("prim"),
        arg("time") = std::numeric_limits<double>::quiet_NaN(),
        R"(
            Get the local transform of a prim at a given time in the form of common transform components.

            Args:
                prim: The prim to get local transform from.
                time: Time at which to query the value.

            Returns:
                Transform value as a tuple of translation, pivot, rotation, rotation order, scale.

        )"
    );

    m.def(
        "defineXform",
        overload_cast<UsdStagePtr, const SdfPath&, std::optional<const GfTransform>>(&defineXform),
        arg("stage"),
        arg("path"),
        arg("transform") = nullptr,
        R"(
            Defines an xform on the stage.

            Parameters:
                - **stage** - The stage on which to define the xform
                - **path** - The absolute prim path at which to define the xform
                - **transform** - Optional local transform to set

            Returns:
                UsdGeom.Xform schema wrapping the defined Usd.Prim. Returns an invalid schema on error.
        )"
    );

    m.def(
        "defineXform",
        overload_cast<UsdPrim, const std::string&, std::optional<const GfTransform>>(&defineXform),
        arg("parent"),
        arg("name"),
        arg("transform") = nullptr,
        R"(
            Defines an xform on the stage.

            Parameters:
                - **parent** - Prim below which to define the xform
                - **name** - Name of the xform
                - **transform** - Optional local transform to set

            Returns:
                UsdGeom.Xform schema wrapping the defined Usd.Prim. Returns an invalid schema on error.
        )"
    );
}

} // namespace usdex::core::bindings
